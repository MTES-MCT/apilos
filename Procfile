web: gunicorn --chdir core core.wsgi --log-file -
worker: python manage.py rundramatiq
postdeploy: bash bin/post_deploy
