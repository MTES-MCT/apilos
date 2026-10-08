private: gunicorn --workers 4 --timeout 30 --chdir core core.wsgi --bind 0.0.0.0:8080 --log-file -
worker: python -m celery -A core.worker worker -B -l INFO
postdeploy: bash bin/post_deploy
