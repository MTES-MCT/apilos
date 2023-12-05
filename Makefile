runserver:
	python manage.py runserver 0.0.0.0:8001

install_requirements:
	pip install --require-hashes --no-deps -r requirements.txt -r dev-requirements.txt

test:
	python manage.py test

upgrade_requirements:
	pip-compile --upgrade --generate-hashes requirements.in
	pip-compile --upgrade --generate-hashes dev-requirements.in
