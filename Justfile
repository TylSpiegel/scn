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
	npx tailwindcss build scn_website/static/css/scn_website.css -o scn_website/static/css/tailwind.css
