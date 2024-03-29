FROM python:3.7.9

LABEL maintainer="Tom Hicks hickst@email.arizona.edu"

ARG TESTS=notests

ENV RUNNING_IN_CONTAINER True
ENV INSTALL_PATH /imdtk

RUN mkdir -p $INSTALL_PATH $INSTALL_PATH/scripts /vos/catalogs /vos/images /work

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY setup.py setup.py
COPY .bash_env /etc/trhenv
COPY imdtk imdtk
COPY config config
COPY $TESTS $TESTS

# following line runs setup.py to setup CLI scripts:
RUN pip install .

ENTRYPOINT [ "./scripts/runit" ]
CMD [ "-v", "-h" ]
