FROM jrottenberg/ffmpeg:4.0-ubuntu

RUN \
  apt-get -y install wget && \
  wget -O - http://installrepo.kaltura.org/repo/apt/xenial/kaltura-deb-256.gpg.key|apt-key add - && \
  echo "deb [arch=amd64] http://installrepo.kaltura.org/repo/apt/xenial naos main" > /etc/apt/sources.list.d/kaltura.list && \
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get -y install kaltura-nginx

WORKDIR /opt/kaltura/nginx
ADD nginx.conf ./conf
ADD vod.conf ./conf

RUN \
  ln -sf /dev/stdout /opt/kaltura/nginx/logs/access.log && \
  ln -sf /dev/stderr /opt/kaltura/nginx/logs/error.log

STOPSIGNAL SIGTERM

EXPOSE 4010

# # reset image's default entrypoint (ffmpeg)
ENTRYPOINT []

# CMD ["nginx", "-g", "daemon off;"]
CMD ["/opt/kaltura/nginx/sbin/nginx", "-g", "daemon off;"]