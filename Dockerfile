FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

ENV PORT=9999

RUN mkdir /code
WORKDIR /code

COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt


EXPOSE 9202
CMD  gunicorn -b 0.0.0.0:9202 --workers=5 --threads=200 --env  DJANGO_SETTINGS_MODULE=inventory.settings.development -k gevent  inventory.wsgi:application
#CMD  python3 manage.py runserver 0:9202 --settings=medicalShare.settings.development
