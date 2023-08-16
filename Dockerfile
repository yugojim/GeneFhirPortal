# Set default image base
FROM python:3.9.15

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor

ADD . /server
WORKDIR /server

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN useradd --no-create-home nginx

COPY nginx.conf /etc/nginx/sites-enabled/
#COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY uwsgi.ini /etc/
COPY supervisord.conf /etc/
#COPY ssl.csr /etc/nginx/ssl.csr
#COPY ssl.key /etc/nginx/ssl.key
CMD ["/usr/bin/supervisord"]

EXPOSE 8000
#EXPOSE 443