 FROM python:3

 ENV PYTHONUNBUFFERED 1
 
 RUN mkdir /app
 ADD . /app/
 
 WORKDIR /app
 RUN pip install -r requirements.txt
 RUN chmod +x docker-entrypoint.sh