FROM jrottenberg/ffmpeg:4.0

RUN \
  apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y \
  python3 \
  python3-dev \
  python3-setuptools \
  python3-pip \
  git

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
ADD . /app/

WORKDIR /app
RUN pip3 install --upgrade -r requirements.txt


# reset image's default entrypoint (ffmpeg)
ENTRYPOINT []
