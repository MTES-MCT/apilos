web: gunicorn --timeout 300 --chdir core core.wsgi --log-file -
worker: python manage.py rundramatiq
postdeploy: bash bin/post_deploy
