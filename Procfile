web: gunicorn --timeout 300 --chdir core core.wsgi --log-file -
worker: python manage.py rundramatiq $DRAMATIQ_CLI_OPTIONS
postdeploy: bash bin/post_deploy
