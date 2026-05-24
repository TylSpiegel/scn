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
from django.db import transaction
from django.utils.html import escape as html_escape

from apps.community.models.member import Role, Choriste, Address
from apps.community.models.event import Event


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
                            help="Domaines a sauter (csv): roles,choristes,events")

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


class _DryRunRollback(Exception):
    """Sentinelle pour annuler la transaction en mode --dry-run."""
    pass
