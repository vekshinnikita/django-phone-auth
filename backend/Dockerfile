FROM python:3.10

WORKDIR /usr/src/app
RUN mkdir /usr/src/app/backend
WORKDIR /usr/src/app/backend

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

RUN apt-get update
RUN apt-get upgrade -y && apt-get install postgresql gcc python3-dev musl-dev -y
RUN pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt

RUN chmod +x /usr/src/app/backend/entrypoint.sh

ENTRYPOINT ["/usr/src/app/backend/entrypoint.sh"]