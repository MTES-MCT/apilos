web: gunicorn --timeout 300 --chdir core --workers 4 core.wsgi --log-file -
worker: python -m celery -A core.worker worker -B -l INFO
postdeploy: bash bin/post_deploy
