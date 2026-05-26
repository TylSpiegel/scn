"""
Migre les donnees depuis la base SQLite de la branche master vers la base
Postgres de la branche rework-structure (via l'ORM Django de cette derniere).

Usage :
    python manage.py migrate_legacy --source /path/to/legacy.sqlite3
    python manage.py migrate_legacy --source ... --dry-run
    python manage.py migrate_legacy --source ... --skip roles,events

Domaines couverts en phase 1 :
    - roles      : choristes_choirrole -> Role
    - choristes  : choristes_choriste -> Choriste (+ M2M Role, + Addresses)
    - events     : choristes_evenement -> Event (+ tags pour is_repetition / pupitre)

Idempotent : sur clef metier raisonnable (Role.name, Choriste.mail|name,
Event.(name,start_date)). Relancer ne duplique pas.

Phase 2 (a venir) : pieces (Wagtail Pages + media docs).
"""

import sqlite3
from contextlib import contextmanager

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils.html import escape as html_escape

from apps.community.models.member import Role, Choriste, Address
from apps.community.models.event import Event
from apps.music.models import Piece, PieceIndexPage, RepertoirePage, RepertoireItem
from apps.content.models import HomePage, ContentPage, ContentSection
from wagtail.documents import get_document_model
from wagtail.models import Collection


# Mapping pupitres legacy -> valeurs VOICE_PART_CHOICES de rework
# La cle est la valeur stockee en master (PUPITRES choices), la valeur est
# la valeur correspondante dans rework.
PUPITRE_MAP = {
    'Tutti': 'Tutti',
    'Soprano': 'Soprano',
    'Mezzo-soprano': 'Mezzo-soprano',
    'Mezzo': 'Mezzo-soprano',
    'Alto': 'Alto',
    'Mezzo-alto': 'Mezzo-alto',
    'Tenor': 'Ténor',
    'Ténor': 'Ténor',
    'Basse': 'Basse',
    'Bass': 'Basse',
    'Autre': 'Autre',
}


def _norm_pupitre(value):
    if not value:
        return None
    value = value.strip()
    return PUPITRE_MAP.get(value, value if value in dict(PUPITRE_MAP).values() else None)


@contextmanager
def _legacy_conn(path):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _table_exists(conn, name):
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    )
    return cur.fetchone() is not None


def _columns(conn, table):
    return {row['name'] for row in conn.execute(f"PRAGMA table_info({table})")}


class Command(BaseCommand):
    help = "Migre les donnees d'une SQLite (branche master) vers la base actuelle."

    def add_arguments(self, parser):
        parser.add_argument('--source', required=True, help="Chemin vers le .sqlite3 legacy")
        parser.add_argument('--dry-run', action='store_true',
                            help="N'ecrit rien (transaction rollback en fin de run)")
        parser.add_argument('--skip', default='',
                            help="Domaines a sauter (csv): roles,choristes,events,"
                                 "documents,pieces,repertoires,content_pages")

    def handle(self, *args, **options):
        path = options['source']
        skip = {s.strip() for s in options['skip'].split(',') if s.strip()}
        dry = options['dry_run']

        with _legacy_conn(path) as conn:
            try:
                with transaction.atomic():
                    role_map = {}
                    if 'roles' not in skip:
                        role_map = self._migrate_roles(conn)
                    else:
                        self.stdout.write("== roles : skip ==")

                    if 'choristes' not in skip:
                        self._migrate_choristes(conn, role_map)
                    else:
                        self.stdout.write("== choristes : skip ==")

                    if 'events' not in skip:
                        self._migrate_events(conn)
                    else:
                        self.stdout.write("== events : skip ==")

                    if 'documents' not in skip:
                        self._migrate_documents(conn)
                    else:
                        self.stdout.write("== documents : skip ==")

                    piece_map = {}
                    if 'pieces' not in skip:
                        piece_map = self._migrate_pieces(conn)
                    else:
                        self.stdout.write("== pieces : skip ==")

                    if 'repertoires' not in skip:
                        self._migrate_repertoires(conn, piece_map)
                    else:
                        self.stdout.write("== repertoires : skip ==")

                    if 'content_pages' not in skip:
                        self._migrate_content_pages(conn)
                    else:
                        self.stdout.write("== content_pages : skip ==")

                    if dry:
                        raise _DryRunRollback()
            except _DryRunRollback:
                self.stdout.write(self.style.WARNING(
                    "[DRY-RUN] Transaction rollback : aucune ecriture committee."
                ))

        self.stdout.write(self.style.SUCCESS("Migration terminee."))

    # ------------------------------------------------------------------ #
    # Roles
    # ------------------------------------------------------------------ #

    def _migrate_roles(self, conn):
        self.stdout.write("== roles ==")
        table = 'choristes_choirrole'
        if not _table_exists(conn, table):
            self.stdout.write(f"  table {table} absente, skip")
            return {}

        legacy_to_new = {}
        rows = conn.execute(f"SELECT id, name, description FROM {table}").fetchall()
        for row in rows:
            name = (row['name'] or '').strip()
            if not name:
                continue
            obj, created = Role.objects.update_or_create(
                name=name,
                defaults={'description': row['description'] or ''},
            )
            legacy_to_new[row['id']] = obj.pk
            self.stdout.write(
                f"  {'[cree]' if created else '[maj] '} Role « {name} »"
            )
        return legacy_to_new

    # ------------------------------------------------------------------ #
    # Choristes (+ M2M + Addresses)
    # ------------------------------------------------------------------ #

    def _migrate_choristes(self, conn, role_map):
        self.stdout.write("== choristes ==")
        table = 'choristes_choriste'
        if not _table_exists(conn, table):
            self.stdout.write(f"  table {table} absente, skip")
            return

        cols = _columns(conn, table)
        legacy_to_new = {}
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()

        for row in rows:
            name = (row['name'] or '').strip()
            if not name:
                continue

            # Clef metier: mail si dispo et non vide, sinon (name, birthdate)
            mail = (row['mail'] or '').strip().lower() or None
            lookup = {'mail': mail} if mail else {'name': name}

            defaults = {
                'name': name,
                'active': bool(row['active']) if 'active' in cols else False,
                'pupitre': _norm_pupitre(row['pupitre']) if 'pupitre' in cols else None,
                'phone': (row['phone'] or '') if 'phone' in cols else '',
                'birthdate': row['birthdate'] if 'birthdate' in cols else None,
            }
            if mail:
                defaults['mail'] = mail
            else:
                defaults['mail'] = None
            # Si on a une cle mail, on met name dans defaults aussi
            if 'mail' in lookup:
                defaults['name'] = name

            obj, created = Choriste.objects.update_or_create(
                **lookup, defaults=defaults
            )
            legacy_to_new[row['id']] = obj.pk

            # M2M Roles
            if role_map:
                m2m_table = 'choristes_choriste_choir_functions'
                if _table_exists(conn, m2m_table):
                    m2m_cols = _columns(conn, m2m_table)
                    fk_col = 'choirrole_id' if 'choirrole_id' in m2m_cols else 'role_id'
                    m2m_rows = conn.execute(
                        f"SELECT {fk_col} FROM {m2m_table} WHERE choriste_id = ?",
                        (row['id'],),
                    ).fetchall()
                    new_role_pks = [
                        role_map[r[fk_col]] for r in m2m_rows
                        if r[fk_col] in role_map
                    ]
                    obj.choir_functions.set(new_role_pks)

            # Addresses
            addr_table = 'choristes_address'
            if _table_exists(conn, addr_table):
                addr_rows = conn.execute(
                    f"SELECT * FROM {addr_table} WHERE choriste_id = ?", (row['id'],)
                ).fetchall()
                # On wipe les addresses existantes du choriste pour eviter les doublons
                obj.addresses.all().delete()
                for addr in addr_rows:
                    Address.objects.create(
                        choriste=obj,
                        street=(addr['street'] or '').strip(),
                        zip_code=(addr['zip_code'] or '').strip(),
                        city=(addr['city'] or '').strip(),
                    )

            self.stdout.write(
                f"  {'[cree]' if created else '[maj] '} Choriste « {name} »"
                f"{' + ' + str(len(addr_rows)) + ' addr' if _table_exists(conn, addr_table) and addr_rows else ''}"
            )

    # ------------------------------------------------------------------ #
    # Events (+ tags is_repetition / pupitre)
    # ------------------------------------------------------------------ #

    def _migrate_events(self, conn):
        self.stdout.write("== events ==")
        table = 'choristes_evenement'
        if not _table_exists(conn, table):
            self.stdout.write(f"  table {table} absente, skip")
            return

        cols = _columns(conn, table)
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()

        for row in rows:
            name = (row['name'] or '').strip() or 'Sans titre'
            start_date = row['start_date']
            if not start_date:
                self.stderr.write(f"  [skip] event id={row['id']} sans start_date")
                continue

            # Hours -> time_tbd
            start_time = row['start_hour'] if 'start_hour' in cols else None
            end_time = row['end_hour'] if 'end_hour' in cols else None
            time_tbd = not bool(start_time)
            if time_tbd:
                start_time = None
                end_time = None
            elif end_time and not start_time:
                end_time = None  # validateur exige start_time si end_time

            # Description (TextField legacy -> RichTextField rework, on entoure
            # le texte plat d'un <p> pour que Wagtail l'affiche correctement)
            raw_descr = (row['description'] or '').strip() if 'description' in cols else ''
            long_description = f"<p>{html_escape(raw_descr)}</p>" if raw_descr else ''

            defaults = {
                'short_description': '',
                'long_description': long_description,
                'end_date': row['end_date'] if 'end_date' in cols else None,
                'time_tbd': time_tbd,
                'start_time': start_time,
                'end_time': end_time,
                'lieu': (row['lieu'] or None) if 'lieu' in cols else None,
                'adresse': (row['adresse'] or None) if 'adresse' in cols else None,
            }

            # end_date doit etre >= start_date sinon save() leve.
            # Si on a un end_date < start_date dans la source, on aligne.
            if defaults['end_date'] and defaults['end_date'] < start_date:
                defaults['end_date'] = start_date

            obj, created = Event.objects.update_or_create(
                name=name, start_date=start_date, defaults=defaults,
            )

            # Tags
            tag_set = []
            if 'is_repetition' in cols:
                tag_set.append('répétition' if row['is_repetition'] else 'concert')
            if 'pupitre' in cols and row['pupitre']:
                p = _norm_pupitre(row['pupitre'])
                if p:
                    tag_set.append(p.lower())
            obj.tags.set(tag_set)

            self.stdout.write(
                f"  {'[cree]' if created else '[maj] '} Event « {name} »"
                f" ({start_date}) tags={tag_set}"
            )


    # ------------------------------------------------------------------ #
    # Collections Wagtail (treebeard)
    # ------------------------------------------------------------------ #

    def _migrate_collections(self, conn):
        """Migre wagtailcore_collection. Retourne le mapping src_id -> dst_id."""
        table = 'wagtailcore_collection'
        col_map = {}
        if not _table_exists(conn, table):
            return col_map

        rows = conn.execute(f"SELECT * FROM {table} ORDER BY depth, path").fetchall()
        if not rows:
            return col_map

        # Root cible (toujours depth=1 dans Wagtail, cree par les migrations)
        root_dst = Collection.objects.filter(depth=1).first()
        if not root_dst:
            self.stderr.write("  Pas de Root Collection dans la cible, abandon.")
            return col_map

        for row in rows:
            if row['depth'] == 1:
                # Root: on associe le src.id au root.pk de la cible
                col_map[row['id']] = root_dst.pk
                continue

            # Sub-collection: on cree ou on retrouve par nom (sous root)
            name = row['name'] or 'Sans nom'
            existing = Collection.objects.filter(name=name, depth=row['depth']).first()
            if existing:
                col_map[row['id']] = existing.pk
            else:
                new_col = root_dst.add_child(instance=Collection(name=name))
                col_map[row['id']] = new_col.pk

        self.stdout.write(f"== collections: {len(col_map)} mappees ==")
        return col_map

    # ------------------------------------------------------------------ #
    # Documents Wagtail (PDF, audios, fichiers additionnels)
    # ------------------------------------------------------------------ #

    def _migrate_documents(self, conn):
        self.stdout.write("== documents ==")
        Document = get_document_model()
        table = 'wagtaildocs_document'
        if not _table_exists(conn, table):
            self.stdout.write(f"  table {table} absente, skip")
            return

        # Migrer les Collections d'abord pour avoir les FK valides
        col_map = self._migrate_collections(conn)
        # Fallback: Root Collection (depth=1) si la collection source n'est pas mappee
        root_dst = Collection.objects.filter(depth=1).first()
        root_pk = root_dst.pk if root_dst else 1

        cols = _columns(conn, table)
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
        n_created = n_updated = n_skipped = 0
        max_id = 0
        for row in rows:
            try:
                src_col = row['collection_id'] if 'collection_id' in cols else None
                dst_col = col_map.get(src_col, root_pk) if src_col else root_pk
                defaults = {
                    'title': row['title'] or '',
                    'file': row['file'] or '',
                    'collection_id': dst_col,
                }
                if 'created_at' in cols and row['created_at']:
                    defaults['created_at'] = row['created_at']
                if 'file_size' in cols:
                    defaults['file_size'] = row['file_size']
                if 'file_hash' in cols:
                    defaults['file_hash'] = row['file_hash'] or ''

                _, created = Document.objects.update_or_create(
                    pk=row['id'], defaults=defaults,
                )
                if created:
                    n_created += 1
                else:
                    n_updated += 1
                max_id = max(max_id, row['id'])
            except Exception as e:
                n_skipped += 1
                self.stderr.write(f"  [skip] document id={row['id']}: {e}")

        # Aligner la sequence Postgres pour eviter les conflits sur futurs inserts
        if max_id and connection.vendor == 'postgresql':
            with connection.cursor() as c:
                c.execute(
                    "SELECT setval(pg_get_serial_sequence(%s, 'id'), %s, true)",
                    [table, max_id],
                )

        self.stdout.write(f"  -> docs: {n_created} crees, {n_updated} mis a jour, "
                          f"{n_skipped} ignores (max id = {max_id})")

    # ------------------------------------------------------------------ #
    # Pieces (MorceauPage -> Piece, parentes a PieceIndexPage unique)
    # ------------------------------------------------------------------ #

    def _migrate_pieces(self, conn):
        self.stdout.write("== pieces ==")
        index = PieceIndexPage.objects.first()
        if not index:
            raise CommandError(
                "PieceIndexPage absente. Lance d'abord setup_site (django_setup.yml)."
            )

        table = 'choristes_morceaupage'
        if not _table_exists(conn, table):
            self.stdout.write(f"  table {table} absente, skip")
            return {}

        cols = _columns(conn, table)
        rows = conn.execute(f"""
            SELECT m.*, p.title as page_title, p.slug as page_slug, p.live as page_live
            FROM {table} m
            JOIN wagtailcore_page p ON p.id = m.page_ptr_id
            ORDER BY p.path
        """).fetchall()

        legacy_to_new = {}  # page_ptr_id source -> Piece.pk cible
        n_created = n_updated = 0

        for row in rows:
            # Priorite au champ custom `titre`, fallback sur Page.title
            title = ((row['titre'] if 'titre' in cols else '') or row['page_title'] or 'Sans titre').strip()
            slug = (row['page_slug'] or '').strip()
            if not slug:
                continue

            defaults = {
                'title': title,
                'compositeur': ((row['compositeur'] if 'compositeur' in cols else '') or '').strip(),
                'descr': row['descr'] if 'descr' in cols else '',
                'traduction': row['traduction'] if 'traduction' in cols else '',
                'interpretation': row['interpretation'] if 'interpretation' in cols else '',
                'activer_timecodes': bool(row['activer_timecodes']) if 'activer_timecodes' in cols else False,
                # timecodes legacy: ancien StreamField (JSON). Format incompatible
                # avec le nouveau TextField « paroles + [mm:ss] » -> on n'importe pas.
                'timecodes': '',
                'audios': row['audios'] if 'audios' in cols and row['audios'] else '[]',
                'additional_files': row['additional_files'] if 'additional_files' in cols and row['additional_files'] else '[]',
                'live': bool(row['page_live']),
            }
            if 'pdf_id' in cols:
                defaults['pdf_id'] = row['pdf_id']

            existing = Piece.objects.filter(slug=slug).first()
            if existing:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                existing.save()
                legacy_to_new[row['page_ptr_id']] = existing.pk
                n_updated += 1
            else:
                piece = Piece(slug=slug, **defaults)
                index.add_child(instance=piece)
                legacy_to_new[row['page_ptr_id']] = piece.pk
                n_created += 1

            self.stdout.write(
                f"  {'[cree]' if existing is None else '[maj] '} Piece « {title} » (slug={slug})"
            )

        self.stdout.write(f"  -> pieces: {n_created} crees, {n_updated} mis a jour")
        return legacy_to_new

    # ------------------------------------------------------------------ #
    # Repertoires (MorceauIndexPage -> RepertoirePage) + RepertoireItem
    # ------------------------------------------------------------------ #

    def _migrate_repertoires(self, conn, piece_map):
        self.stdout.write("== repertoires ==")
        home = HomePage.objects.first()
        if not home:
            raise CommandError(
                "HomePage absente. Lance d'abord setup_site (django_setup.yml)."
            )

        index_table = 'choristes_morceauindexpage'
        if not _table_exists(conn, index_table):
            self.stdout.write(f"  table {index_table} absente, skip")
            return

        index_cols = _columns(conn, index_table)
        idx_rows = conn.execute(f"""
            SELECT mi.*, p.title as page_title, p.slug as page_slug,
                   p.path, p.depth, p.live as page_live
            FROM {index_table} mi
            JOIN wagtailcore_page p ON p.id = mi.page_ptr_id
            ORDER BY p.path
        """).fetchall()

        # Construire mapping path source -> RepertoirePage cree dans rework
        path_to_rep_pk = {}
        for row in idx_rows:
            title = (row['page_title'] or 'Répertoire').strip()
            slug = (row['page_slug'] or '').strip()
            if not slug:
                continue
            intro = (row['introduction'] if 'introduction' in index_cols else '') or ''

            existing = RepertoirePage.objects.filter(slug=slug).first()
            if existing:
                existing.title = title
                existing.introduction = intro
                existing.live = bool(row['page_live'])
                existing.save()
                rep = existing
            else:
                rep = RepertoirePage(
                    title=title, slug=slug,
                    introduction=intro, live=bool(row['page_live']),
                )
                home.add_child(instance=rep)

            path_to_rep_pk[row['path']] = rep.pk
            self.stdout.write(f"  {'[maj] ' if existing else '[cree]'} Repertoire « {title} »")

        # Pour chaque MorceauPage, retrouver son MorceauIndexPage parent via path
        # (Wagtail utilise un path tree de 4 chars par niveau).
        piece_table = 'choristes_morceaupage'
        piece_rows = conn.execute(f"""
            SELECT m.page_ptr_id, p.path
            FROM {piece_table} m
            JOIN wagtailcore_page p ON p.id = m.page_ptr_id
            ORDER BY p.path
        """).fetchall()

        n_items = n_skipped = 0
        for row in piece_rows:
            parent_path = row['path'][:-4]   # un niveau au-dessus
            rep_pk = path_to_rep_pk.get(parent_path)
            if not rep_pk:
                n_skipped += 1
                continue

            new_piece_pk = piece_map.get(row['page_ptr_id'])
            if not new_piece_pk:
                n_skipped += 1
                continue

            RepertoireItem.objects.update_or_create(
                repertoire_id=rep_pk,
                piece_id=new_piece_pk,
            )
            n_items += 1

        self.stdout.write(
            f"  -> repertoire_items: {n_items} crees/maj, {n_skipped} ignores "
            f"(parent index ou piece manquante)"
        )


    # ------------------------------------------------------------------ #
    # ContentPage (StreamField content master -> ContentSection unique rework)
    # ------------------------------------------------------------------ #

    def _migrate_content_pages(self, conn):
        self.stdout.write("== content_pages ==")
        import json
        from datetime import date as _date

        home = HomePage.objects.first()
        if not home:
            raise CommandError(
                "HomePage absente. Lance d'abord setup_site (django_setup.yml)."
            )

        # En master, l'app contenu s'appelle 'home', donc la table est home_contentpage.
        # On gere aussi 'content_contentpage' au cas ou un repo aurait deja renomme.
        candidate_tables = ['home_contentpage', 'content_contentpage']
        table = next((t for t in candidate_tables if _table_exists(conn, t)), None)
        if not table:
            self.stdout.write(
                f"  table {' / '.join(candidate_tables)} absente, skip"
            )
            return

        cols = _columns(conn, table)
        rows = conn.execute(f"""
            SELECT c.*, p.title as page_title, p.slug as page_slug,
                   p.live as page_live
            FROM {table} c
            JOIN wagtailcore_page p ON p.id = c.page_ptr_id
            ORDER BY p.path
        """).fetchall()

        n_created = n_updated = 0
        for row in rows:
            title = (row['page_title'] or 'Sans titre').strip()
            slug = (row['page_slug'] or '').strip()
            if not slug:
                continue

            existing = ContentPage.objects.filter(slug=slug).first()
            if existing:
                existing.title = title
                existing.live = bool(row['page_live'])
                existing.save()
                page = existing
                n_updated += 1
            else:
                page = ContentPage(
                    title=title, slug=slug, live=bool(row['page_live']),
                )
                home.add_child(instance=page)
                n_created += 1

            # Reconstruction du contenu : StreamField master -> HTML aggrege
            raw = row['content'] if 'content' in cols else None
            html = self._stream_to_simple_html(raw)

            # Idempotence : on remplace les sections existantes
            page.sections.all().delete()
            if html.strip():
                ContentSection.objects.create(
                    page=page,
                    title='Contenu',
                    date=_date.today(),
                    body=html,
                )

            self.stdout.write(
                f"  {'[cree]' if existing is None else '[maj] '} "
                f"ContentPage « {title} » (slug={slug})"
            )

        self.stdout.write(
            f"  -> content_pages: {n_created} crees, {n_updated} mis a jour"
        )

    def _stream_to_simple_html(self, raw):
        """Convertit le StreamField JSON master en HTML aggrege (basse fidelite).

        Blocks geres :
        - richtext / paragraph / text : valeur HTML reprise telle quelle
        - image : placeholder car les images ne sont pas migrees
        - multicolumn : aplatissement des colonnes (les valeurs HTML internes
          sont concatenees, la structure colonnes est perdue)
        - autres types : ignores
        """
        import json
        if not raw:
            return ''
        try:
            blocks = json.loads(raw)
        except (ValueError, TypeError):
            return ''
        if not isinstance(blocks, list):
            return ''

        parts = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            btype = block.get('type', '')
            bval = block.get('value')

            if btype in ('richtext', 'paragraph', 'text'):
                if isinstance(bval, str):
                    parts.append(bval)
            elif btype == 'image':
                parts.append('<p><em>[Image perdue dans la migration]</em></p>')
            elif btype == 'multicolumn':
                if isinstance(bval, dict):
                    cols = bval.get('columns') or []
                    for col in cols:
                        if isinstance(col, dict):
                            for v in col.values():
                                if isinstance(v, str) and v.lstrip().startswith('<'):
                                    parts.append(v)
            # autres types : silent skip
        return '\n'.join(parts)


class _DryRunRollback(Exception):
    """Sentinelle pour annuler la transaction en mode --dry-run."""
    pass
