NAME=mapbike
SHELL=/bin/bash
MANAGE=python manage.py


test:
	ENVIRONMENT=test python manage.py test

resetdb:
	@if [[ ${DATABASE_URL} == *"amazonaws"* ]]; then exit -1; fi
	-phd dropdb
	phd createdb
	echo "CREATE EXTENSION postgis;" | phd psql
	$(MANAGE) syncdb --noinput
	$(MANAGE) migrate --noinput
	$(MANAGE) loaddata markets

# There's a long wait in here on purpose!
# TODO combine these together so they share 'sleep'
# use XMLHttpRequest to get compressed json
testdata/austin:
	curl -H "X-Requested-With: XMLHttpRequest" http://bikeme-api.herokuapp.com/austin/ > bikeme/apps/core/tests/support/austin_response1.json
	sleep 600
	curl -H "X-Requested-With: XMLHttpRequest" http://bikeme-api.herokuapp.com/austin/ > bikeme/apps/core/tests/support/austin_response2.json

testdata/chicago:
	curl http://www.divvybikes.com/stations/json/ > bikeme/apps/core/tests/support/divvy_response1.json
	sleep 600
	curl http://www.divvybikes.com/stations/json/ > bikeme/apps/core/tests/support/divvy_response2.json

docker/build:
	docker build -t crccheck/${NAME} .

docker/runserver:
	docker run --rm --env-file env-docker -p 8000:8000 crccheck/${NAME} \
	  python manage.py runserver 0.0.0.0:8000

docker/scrape:
	docker run --rm --env-file env-docker crccheck/${NAME} \
	  python manage.py scrape
