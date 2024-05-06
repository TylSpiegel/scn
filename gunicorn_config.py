import os
from dotenv import load_dotenv
import logging

load_dotenv()


def on_starting(server):
    logger = logging.getLogger('gunicorn.info')
    # Log pour voir la structure complète de server.address
    logger.info(f"Configuration du serveur: {server.address}")
    try:
        # Tentative d'accéder au port, supposant que server.address est un tuple (host, port)
        logger.info(f"Serveur démarré sur le port {server.address[1]}")
    except IndexError as e:
        # Log de l'erreur si l'indice est hors limites
        logger.error(f"Erreur d'IndexError: {e}. Structure de server.address non conforme aux attentes.")


default_settings_module = 'scn_website.settings.production'
os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv('DJANGO_SETTINGS_MODULE', default_settings_module)

loglevel = 'info'
logfile = 'logs/gunicorn_logfile.log'
accesslog = 'logs/gunicorn_accesslog.log'
errorlog = 'logs/gunicorn_errorlog.log'

access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

bind = "localhost:" + str(os.environ.get('DEPLOY_PORT'))
print(f'Deploying on port {bind}')
workers = 3
