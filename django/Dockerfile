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
ENV SENTRY_DSN https://488be2a352da469e8d0c67c47b601519@sentry.io/1368034

RUN mkdir /src
COPY . /src/

WORKDIR /src
RUN pip3 install --upgrade -r requirements.txt

# reset image's default entrypoint (ffmpeg)
ENTRYPOINT []
