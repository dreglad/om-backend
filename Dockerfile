# FROM python:3
 FROM jrottenberg/ffmpeg

RUN apt-get update && \
    apt-get upgrade -y && \ 
    apt-get install -y \
    python3 \
    python3-dev \
    python3-setuptools \
    python3-pip \
    uwsgi
    nginx

 ENV PYTHONUNBUFFERED 1
 
 RUN mkdir /app
 ADD . /app/
 
 WORKDIR /app
 RUN pip3 install --upgrade pip
 RUN pip3 install -r requirements.txt
 
 RUN chmod +x docker-entrypoint.sh
 ENTRYPOINT []