# Variables d'environnement avec valeurs par défaut
set dotenv-load := true

# Variables
django_port := env_var_or_default('DJANGO_PORT', '8000')
gunicorn_port := env_var_or_default('GUNICORN_PORT', '9200')
django_settings := env_var_or_default('DJANGO_SETTINGS_MODULE', 'scn_website.settings.dev')

# Commande par défaut
default: dev

# === DÉVELOPPEMENT ===

# Lancer le serveur de développement
dev:
    just build
    just runserver

# Lancer le serveur Django
runserver:
    uv run python manage.py runserver {{django_port}}

# Mode watch (CSS + Django)
watch:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    npm run watch &
    just runserver &
    wait

# === BUILD ===

# Build tous les assets (CSS + vendor files)
build:
    npm run build

# Build uniquement le CSS
build-css:
    npm run build:css

# Build uniquement les assets vendor
build-assets:
    npm run build:assets

# Watch le CSS uniquement
watch-css:
    npm run watch

# === BASE DE DONNÉES ===

# Créer les migrations
makemigrations:
    uv run python manage.py makemigrations

# Appliquer les migrations
migrate:
    uv run python manage.py migrate

full-migration:
    just makemigrations
    just migrate

# Reset complet de la base de données
reset-db:
    rm -f db.sqlite3
    just makemigrations
    just migrate
    just createsuperuser

# Créer un superutilisateur
createsuperuser:
    uv run python manage.py createsuperuser

# === DONNÉES ===

# Charger les données de seed
seed:
    uv run python manage.py seed_data

# Charger les données de seed (clear avant)
seed-clear:
    uv run python manage.py seed_data --clear

# === STATIC FILES ===

# Collecter les fichiers statiques
collectstatic:
    uv run python manage.py collectstatic --noinput

# Nettoyer les fichiers statiques
clean-static:
    rm -rf static/
    rm -rf scn_website/static/vendor/
    rm -rf scn_website/static/css/bulma.css

# === PRODUCTION ===

# Déploiement production
deploy:
    just install
    just build
    just collectstatic
    just migrate

# Lancer Gunicorn (production)
gunicorn:
    uv run gunicorn scn_website.wsgi:application --bind localhost:{{gunicorn_port}}

# === DÉPENDANCES ===

# Installer les dépendances (Python + Node)
install:
    uv sync
    npm ci

# Installer les dépendances Python
sync:
    uv sync

# Lock les dépendances Python
lock:
    uv lock

# Ajouter un package Python
add package:
    uv add {{package}}

# Retirer un package Python
remove package:
    uv remove {{package}}

# Installer un package npm
npm-add package:
    npm install {{package}}

# === UTILITAIRES ===

# Shell Django
shell:
    uv run python manage.py shell

# Shell avec iPython si disponible
ishell:
    uv run python manage.py shell -i ipython

# Tests
test:
    uv run python manage.py test

# Tests avec coverage
test-coverage:
    uv run coverage run --source='.' manage.py test
    uv run coverage report
    uv run coverage html

# Linter Python
lint:
    uv run ruff check .

# Formater le code Python
format:
    uv run ruff format .

# === LOGS ===

# Créer le dossier logs
setup-logs:
    mkdir -p logs

# Voir les logs
logs:
    tail -f logs/debug.log

# Nettoyer les logs
clean-logs:
    rm -rf logs/*.log

# === NETTOYAGE ===

# Nettoyer tout (cache, build, static)
clean:
    just clean-static
    just clean-logs
    rm -rf __pycache__
    rm -rf */__pycache__
    rm -rf */*/__pycache__
    find . -name "*.pyc" -delete
    find . -name ".DS_Store" -delete

# Nettoyage profond (+ dépendances)
deep-clean:
    just clean
    rm -rf node_modules
    rm -rf .venv
    rm -rf uv.lock

# === MAINTENANCE ===

# Vérifier l'état du système
check:
    @echo "🔍 Checking system..."
    @uv --version
    @node --version
    @npm --version
    @python --version
    @echo "✅ All tools installed"

# Mise à jour des dépendances
update:
    npm update
    uv lock --upgrade

# === DOCUMENTATION ===

# Afficher l'aide
help:
    @just --list

# Afficher les variables d'environnement
env:
    @echo "Django Port: {{django_port}}"
    @echo "Gunicorn Port: {{gunicorn_port}}"
    @echo "Settings Module: {{django_settings}}"
