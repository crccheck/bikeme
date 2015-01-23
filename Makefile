NAME=mapbike


test:
	ENVIRONMENT=test python manage.py test


docker/build:
	docker build -t crccheck/${NAME} .

docker/runserver:
	docker run --rm --env-file env-docker -p 8000:8000 crccheck/${NAME} \
	  python manage.py runserver 0.0.0.0:8000

docker/scrape:
	docker run --rm --env-file env-docker crccheck/${NAME} \
	  python manage.py scrape
