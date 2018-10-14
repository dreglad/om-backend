FROM jrottenberg/ffmpeg:4.0-centos

RUN \
  yum -y upgrade && \
  rpm -ihv http://installrepo.kaltura.org/releases/kaltura-release.noarch.rpm && \
  yum install -y kaltura-nginx


RUN rm /etc/nginx/conf.d/*
ADD conf.d/ /etc/nginx/conf.d
ADD certs/ /etc/nginx
ADD nginx.conf /etc/nginx/nginx.conf

RUN \
  ln -sf /dev/stdout /var/log/nginx/access.log && \
  ln -sf /dev/stderr /var/log/nginx/error.log

STOPSIGNAL SIGTERM

EXPOSE 80
EXPOSE 443

# reset image's default entrypoint (ffmpeg)
ENTRYPOINT []

CMD ["nginx", "-g", "daemon off;"]