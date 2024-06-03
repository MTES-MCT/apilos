web: gunicorn --timeout 300 --chdir core --workers 4 --max-requests 5000 --max-requests-jitter 50 core.wsgi --log-file -
worker: python -m celery -A core.worker worker -B -l INFO
postdeploy: bash bin/post_deploy
