 FROM jrottenberg/ffmpeg:centos

 RUN yum -y upgrade
 RUN rpm -ihv http://installrepo.kaltura.org/releases/kaltura-release.noarch.rpm
 RUN yum install -y kaltura-nginx
 
 COPY ./media-nginx.conf /etc/nginx/nginx.conf
 COPY ./media-vod.conf /etc/nginx/conf.d/vod.conf

 RUN ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log

 STOPSIGNAL SIGTERM

 EXPOSE 80
 EXPOSE 443

 ENTRYPOINT []
 CMD ["nginx", "-g", "daemon off;"]
 # CMD ['bash']
