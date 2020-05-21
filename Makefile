ARGS=
COLLECTION=JWST
ENVLOC=/etc/trhenv
IMG=imdtk:devel
IMGS=${PWD}/images
NAME=imdtk
NET=vos_net
OUTDIR=${PWD}/out
PROG=imdtk
STACK=vos
TARG=/imdtk
TSTIMG=imdtk:test
# TSTRES=${PWD}/tests/resources

.PHONY: help bash cleanout docker dockert down exec run runt runtc stop up watch

help:
	@echo "Make what? Try: bash, cleanout, docker, dockert, down, run, runt, runtc, stop, up, watch"
	@echo '  where:'
	@echo '     help     - show this help message'
	@echo '     bash     - run Bash in a ${PROG} container (for development)'
	@echo '     cleanout - remove all result SQL files from the output directory'
	@echo '     docker   - build a production container image'
	@echo '     dockert  - build a container image with tests (for testing)'
	@echo '     down     - stop the ${PROG} container, which is running in the VOS stack'
	@echo '     exec     - exec into running development server (CLI arg: NAME=containerID)'
	@echo '     run      - start a standalone container (CLI: ARGS=args)'
	@echo '     runt     - run a standalone container in test mode (CLI: ARGS=args)'
	@echo '     runt1    - run a test/test-dir in a standalone container (CLI: TARG=testpath)'
	@echo '     runtc    - run tests and code coverage in a standalone container'
	@echo '     sql      - generate SQL only for a catalog (do not load it)'
	@echo '     stop     - stop a running standalone container'
	@echo '     up       - start a ${PROG} container, running in the VOS stack'
	@echo '     watch    - show logfile for a running container'

bash:
	docker run -it --rm --name ${NAME} -v ${IMGS}:/images:ro -v ${OUTDIR}:/out --entrypoint /bin/bash ${TSTIMG}

cleanout:
	rm -f ${OUTDIR}/imdtk*

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
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro ${IMG} ${ARGS}

runt:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro -v ${OUTDIR}:/out ${TSTIMG} ${ARGS}

runt1:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro --entrypoint pytest ${TSTIMG} -vv ${TARG}

runtc:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro --entrypoint pytest ${TSTIMG} -vv --cov-report term-missing --cov ${TARG}

sql:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${IMGS}:/images:ro ${IMG} load --sql-only --table ${TABLE}

stop:
	docker stop ${NAME}

up:
	docker stack deploy -c docker-compose.yml ${STACK}

watch:
	docker logs -f ${NAME}
