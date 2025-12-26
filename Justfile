default: runserver

refresh:
    just makemigrations
    just migrate
    just runserver

migrate:
    uv run python manage.py migrate

makemigrations:
    uv run python manage.py makemigrations

runserver:
    uv run python manage.py runserver

buildcss:
    npx @tailwindcss/cli -i scn_website/static/css/scn_website.css -o scn_website/static/css/tailwind.css

deploy_prod:
    uv run python manage.py collectstatic
    git checkout prod
    uv run gunicorn scn_website.wsgi:application --bind localhost:9200

# Commandes utiles supplémentaires
sync:
    uv sync

lock:
    uv lock

add package:
    uv add {{package}}

remove package:
    uv remove {{package}}

shell:
    uv run python manage.py shell

test:
    uv run python manage.py test