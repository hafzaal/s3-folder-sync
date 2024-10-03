FROM python:3.12

ARG PYTHON_ENV=my_env

ENV PYTHON_ENG=$PYTHON_ENV

RUN mkdir requirements

COPY requirements.txt set_python_env.sh /requirements/

RUN bash ./requirements/set_python_env.sh $PYTHON_ENV