ARGS=
COLLECTION=JWST
ENVLOC=/etc/trhenv
EP=/bin/bash
IMG=imdtk:devel
IMGS=${PWD}/images
NAME=imdtk
NET=vos_net
WORKDIR=${PWD}/work
PROG=imdtk
RUN=${PWD}/runit
STACK=vos
TARG=/imdtk
TSTIMG=imdtk:test


.PHONY: help bash cleanwork docker dockert down exec run runit runtc runte stop up watch

help:
	@echo "Make what? Try: bash, cleanwork, docker, dockert, down, run, runit, runt1, runtc, runtep, stop, up, watch"
	@echo '  where:'
	@echo '     help      - show this help message'
	@echo '     bash      - run Bash in a ${PROG} container (for development)'
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
	docker run -it --rm --name ${NAME} -v ${IMGS}:/images:ro -v ${WORKDIR}:/work  -v ${RUN}:/imdtk/runit --entrypoint /bin/bash ${TSTIMG}

cleanwork:
	@rm ${WORKDIR}/*.json ${WORKDIR}/*.pickle

docker:
	docker build -t ${IMG} .

dockert:
	docker build --build-arg TESTS=tests -t ${TSTIMG} .

down:
	docker stack rm ${STACK}

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} bash

run:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro -v ${WORKDIR}:/work -v ${RUN}:/imdtk/runit ${IMG} ${ARGS}

runit:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro -v ${WORKDIR}:/work -v ${RUN}:/imdtk/runit ${TSTIMG} ${ARGS}

runtep:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro -v ${WORKDIR}:/work --entrypoint=${EP} ${TSTIMG} ${ARGS}

runt1:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro --entrypoint pytest ${TSTIMG} -vv ${TARG}

runtc:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro --entrypoint pytest ${TSTIMG} -vv --cov-report term-missing --cov ${TARG}

stop:
	docker stop ${NAME}

up:
	docker stack deploy -c docker-compose.yml ${STACK}

watch:
	docker logs -f ${NAME}
