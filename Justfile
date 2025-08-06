default: runserver

refresh:
    just makemigrations
    just migrate
    just runserver

venv:
    source ./venv/bin/activate

migrate: venv
    python manage.py migrate

makemigrations: venv
    python manage.py makemigrations

runserver: venv
    python manage.py runserver

buildcss:
	npx @tailwindcss/cli  -i scn_website/static/css/scn_website.css -o scn_website/static/css/tailwind.css

deploy_prod : venv
    python manage.py collectstatic
    git checkout prod
    gunicorn scn_website.wsgi:application --bind localhost:9200
