FROM tensorflow/tensorflow:2.3.0-gpu

MAINTAINER Ralph Brecheisen <r.brecheisen@maastrichtuniversity.nl>

COPY src/mosamatic/web/mosamatic /src
COPY requirements-web.txt /requirements.txt
COPY create-users.txt /
COPY docker-entrypoint.sh /

# apt-get update -y gave errors regarding NVIDIA public key
# https://chrisjean.com/fix-apt-get-update-the-following-signatures-couldnt-be-verified-because-the-public-key-is-not-available/
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC && \
    apt-get update -y && \
    apt-get install -y vim libpq-dev pkg-config cmake openssl wget git vim && \
    pip install --upgrade pip && \
    pip install -r /requirements.txt && \
    pip install uwsgi gunicorn && \
    mkdir -p /data/static && \
    mkdir -p /data/uploads/{0..9} && chmod 777 -R /data/uploads

WORKDIR /src

EXPOSE 8001

RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Hack to prevent users from seeing source code when entering the container
# ENV ENV=/root/.profile
# RUN echo "rm -rf /src/* && rm /root/.bashrc && rm /root/.profile" > /root/.bashrc
# RUN echo "rm -rf /src/* && rm /root/.bashrc && rm /root/.profile" > /root/.profile

CMD ["/docker-entrypoint.sh"]