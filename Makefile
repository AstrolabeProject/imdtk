# environment variables for Docker container run parameters.
TOPLVL=${PWD}
CATS=${TOPLVL}/catalogs
IMGS=${TOPLVL}/images
SCRIPTS=${TOPLVL}/scripts
WORK=${TOPLVL}/work

ARGS=
APP_ROOT=/imdtk
CONSCRIPTS=${APP_ROOT}/scripts
COLLECTION=JWST
ENVLOC=/etc/trhenv
EP=/bin/bash
IMG=imdtk:devel
NAME=imdtk
NET=vos_net
PROG=imdtk
SHELL=/bin/bash
STACK=vos
TARG=/imdtk
TSTIMG=imdtk:test


.PHONY: help bash cleancache cleanwork docker dockert down exec run runit runtc runte stop up watch

help:
	@echo "Make what? Try: bash, cleancache, cleanwork, docker, dockert, down, run, runit, runt1, runtc, runtep, stop, up, watch"
	@echo '  where:'
	@echo '     help      - show this help message'
	@echo '     bash      - run Bash in a ${PROG} container (for development)'
	@echo '     cleancache - REMOVE ALL __pycache__ dirs from the project directory!'
	@echo '     cleanwork - REMOVE ALL input and output files from the work directory!'
	@echo '     docker    - build a production container image'
	@echo '     dockert   - build a container image with tests (for testing)'
	@echo '     down      - stop the ${PROG} container, which is running in the VOS stack'
	@echo '     exec      - exec into running development server (CLI arg: NAME=containerID)'
	@echo '     run       - start a container (CLI: ARGS=args)'
	@echo '     runit     - run the runit program in a test container'
	@echo '     runt1     - run a test/test-dir in a container (CLI: TARG=testpath)'
	@echo '     runtc     - run all tests and code coverage in a container'
	@echo '     runtep    - run a test container with alternate entrypoint (CLI: EP=entrypoint, ARGS=args)'
	@echo '     stop      - stop a running container'
	@echo '     up        - start a ${PROG} container, running in the VOS stack'
	@echo '     watch     - show logfile for a running container'

bash:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${CATS}:/catalogs:ro -v ${IMGS}:/images:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${WORK}:/work --entrypoint ${SHELL} ${TSTIMG} ${ARGS}

cleancache:
	find . -name __pycache__ -print | grep -v .venv | xargs rm -rf

cleanwork:
	@rm ${WORK}/*.json ${WORK}/*.pickle ${WORK}/*.sql ${WORK}/*.csv

docker:
	docker build -t ${IMG} .

dockert:
	docker build --build-arg TESTS=tests -t ${TSTIMG} .

down:
	docker stack rm ${STACK}

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} ${EP}

run:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${CATS}:/catalogs:ro -v ${IMGS}:/images:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${WORK}:/work ${IMG} ${ARGS}

runit:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${CATS}:/catalogs:ro -v ${IMGS}:/images:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${WORK}:/work ${TSTIMG} ${ARGS}

runtep:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${CATS}:/catalogs:ro -v ${IMGS}:/images:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${WORK}:/work --entrypoint ${EP} ${TSTIMG} ${ARGS}

runt1:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${CATS}:/catalogs:ro -v ${IMGS}:/images:ro --entrypoint pytest ${TSTIMG} -vv ${TARG}

runtc:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${CATS}:/catalogs:ro -v ${IMGS}:/images:ro --entrypoint pytest ${TSTIMG} -vv --cov-report term-missing --cov ${TARG}

stop:
	docker stop ${NAME}

up:
	docker stack deploy -c docker-compose.yml ${STACK}

watch:
	docker logs -f ${NAME}
