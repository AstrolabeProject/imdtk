TOPLVL=${PWD}
SCRIPTS=${TOPLVL}/scripts
VOS=/usr/local/data/vos
WORK=${TOPLVL}/work

ARGS=
APP_ROOT=/imdtk
CONCATS=${VOS}/catalogs
CONIMGS=${VOS}/images
CONIRODS=${APP_ROOT}/.irods
CONSCRIPTS=${APP_ROOT}/scripts
COLLECTION=JWST
ENVLOC=/etc/trhenv
EP=/bin/bash
IGNORE='tests/imdtk/core/*irods_helper.py'
IMG=astrolabe/imdtk:imgmd
NAME=imdtk
NET=vos_net
ONLY=
PROG=imdtk
SCOPE=imdtk
SHELL=/bin/bash
TARG=/imdtk
TESTS=tests
TSTIMG=astrolabe/imdtk:test


.PHONY: help bash cleancache cleanwork docker dockert exec run runit runt1 runtc runtep stop testall test1 tests watch

help:
	@echo "Make what? Try: bash, cleancache, cleanwork, docker, dockert, exec, run, runit, runt1, runtc, runtep,"
	@echo "                stop, testall, test1, tests, watch"
	@echo '  where:'
	@echo '     help      - show this help message'
	@echo '     bash      - run Bash in a ${PROG} container (for development)'
	@echo '     cleancache - REMOVE ALL __pycache__ dirs from the project directory!'
	@echo '     cleanwork - REMOVE ALL input and output files from the work directory!'
	@echo '     docker    - build a production container image'
	@echo '     dockert   - build a container image with tests (for testing)'
	@echo '     exec      - exec into running development server (CLI arg: NAME=containerID)'
	@echo '     run       - start a container (CLI: ARGS=args)'
	@echo '     runit     - run the runit program in a test container'
	@echo '     runt1     - run a test/test-dir in a container (CLI: TARG=testpath)'
	@echo '     runtc     - run all tests and code coverage in a container'
	@echo '     runtep    - run a test container with alternate entrypoint (CLI: EP=entrypoint, ARGS=args)'
	@echo '     stop      - stop a running container'
	@echo '     testall   - run ALL tests but stop at the first failure (CLI: TESTS=test_module)'
	@echo '     test1     - run tests with a single name prefix (CLI: ONLY=tests_name_prefix)'
	@echo '     tests     - run one or all unit tests in the tests directory (CLI: TESTS=test_module)'
	@echo '     watch     - show logfile for a running container'

bash:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${CONCATS}:${CONCATS}:ro -v ${CONIMGS}:${CONIMGS}:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${HOME}/.irods:${CONIRODS}:ro -v ${WORK}:/work --entrypoint ${SHELL} ${TSTIMG} ${ARGS}

cleancache:
	find . -name __pycache__ -print | grep -v .venv | xargs rm -rf

cleanwork:
	@rm ${WORK}/*.json ${WORK}/*.pickle ${WORK}/*.sql ${WORK}/*.csv

docker:
	docker build -t ${IMG} .

dockert:
	docker build --build-arg TESTS=tests -t ${TSTIMG} .

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} ${EP}

run:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${CONCATS}:${CONCATS}:ro -v ${CONIMGS}:${CONIMGS}:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${HOME}/.irods:${CONIRODS}:ro -v ${WORK}:/work ${IMG} ${ARGS}

runit:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${CONCATS}:${CONCATS}:ro -v ${CONIMGS}:${CONIMGS}:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${HOME}/.irods:${CONIRODS}:ro -v ${WORK}:/work ${TSTIMG} ${ARGS}

runt1:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${CONCATS}:${CONCATS}:ro -v ${CONIMGS}:${CONIMGS}:ro -v ${HOME}/.irods:${CONIRODS}:ro --entrypoint pytest ${TSTIMG} -vv ${TARG}

runtc:
	docker run -it --rm --network ${NET} --name ${NAME} -v ${CONCATS}:${CONCATS}:ro -v ${CONIMGS}:${CONIMGS}:ro -v ${HOME}/.irods:${CONIRODS}:ro --entrypoint pytest ${TSTIMG} -vv --cov-report term-missing --cov ${TARG}

runtep:
	@docker run -it --rm --network ${NET} --name ${NAME} -v ${CONCATS}:${CONCATS}:ro -v ${CONIMGS}:${CONIMGS}:ro -v ${SCRIPTS}:${CONSCRIPTS} -v ${HOME}/.irods:${CONIRODS}:ro -v ${WORK}:/work --entrypoint ${EP} ${TSTIMG} ${ARGS}

stop:
	docker stop ${NAME}

testall:
	pytest -vv -x ${TESTS} ${ARGS} --cov-report term-missing --cov=${SCOPE}

test1:
	pytest -vv ${TESTS} -k ${ONLY} --cov-report term-missing --cov=${SCOPE}

tests:
	pytest -vv --ignore-glob ${IGNORE} ${TESTS} ${ARGS} --cov-report term-missing --cov=${SCOPE}

watch:
	docker logs -f ${NAME}
