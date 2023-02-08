web: gunicorn --timeout 300 --chdir core core.wsgi --log-file -
worker: python manage.py rundramatiq --processes 2 --threads 1
postdeploy: bash bin/post_deploy
