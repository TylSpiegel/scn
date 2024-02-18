loglevel = 'info'
logfile = 'logs/gunicorn_logfile.log'
accesslog = 'logs/gunicorn_accesslog.log'
errorlog = 'logs/gunicorn_errorlog.log'

access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
