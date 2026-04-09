web: gunicorn --timeout 30 --chdir core core.wsgi --log-file -
worker: python -m celery -A core.worker worker -B -l INFO
postdeploy: bash bin/post_deploy
