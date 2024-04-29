import os
from dotenv import load_dotenv

load_dotenv()

default_settings_module = 'scn_website.settings.production'
os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv('DJANGO_SETTINGS_MODULE', default_settings_module)

loglevel = 'info'
logfile = 'logs/gunicorn_logfile.log'
accesslog = 'logs/gunicorn_accesslog.log'
errorlog = 'logs/gunicorn_errorlog.log'

access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

bind = "localhost:" + str(os.environ.get('DEPLOY_PORT', 9200))
workers = 3
