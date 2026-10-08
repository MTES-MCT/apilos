private: gunicorn --workers 4 --timeout 30 --chdir core core.wsgi --log-file - app:app --bind "${SCALINGO_PRIVATE_HOSTNAME}:8080
worker: python -m celery -A core.worker worker -B -l INFO
postdeploy: bash bin/post_deploy
