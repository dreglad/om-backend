# FROM python:3
 FROM jrottenberg/ffmpeg

 RUN apt-get -qq update
 RUN apt-get -qqy install python3 python3-pip

 ENV PYTHONUNBUFFERED 1
 
 RUN mkdir /app
 ADD . /app/
 
 WORKDIR /app
 RUN pip3 install --upgrade pip
 RUN pip3 install -r requirements.txt
 
 RUN chmod +x docker-entrypoint.sh
 ENTRYPOINT []