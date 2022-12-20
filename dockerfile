FROM tensorflow/tensorflow:2.3.0-gpu

# Ralph Brecheisen <r.brecheisen@maastrichtuniversity.nl>

COPY src/mosamatic/web/mosamatic /src
COPY requirements-web.txt /requirements.txt
COPY create-users.txt /
COPY docker-entrypoint.sh /

# RUN useradd --create-home mosamatic

# apt-get update -y gave errors regarding NVIDIA public key
# https://chrisjean.com/fix-apt-get-update-the-following-signatures-couldnt-be-verified-because-the-public-key-is-not-available/
# Libraries libgl1-mesa-glx and libxrender1 are needed for TotalSegmentator
# Libraries pigz and dcm2niix are needed to convert DICOM to (compressed) NIFTI
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC && \
    apt-get update -y && \
    apt-get install -y vim libpq-dev pkg-config cmake openssl wget git vim && \
    apt-get install -y libgl1-mesa-glx libxrender1 && \
    apt-get install -y pigz dcm2niix && \
    pip install --upgrade pip && \
    pip install -r /requirements.txt && \
    pip install uwsgi gunicorn && \
    mkdir -p /data/static && \
    mkdir -p /data/datasets && \
    mkdir -p /data/uploads/{0..9} && chmod 777 -R /data/uploads

# RUN chown -R mosamatic: /data

WORKDIR /src

EXPOSE 8001

RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Hack to prevent users from seeing source code when entering the container
# ENV ENV=/root/.profile
# RUN echo "rm -rf /src/* && rm /root/.bashrc && rm /root/.profile" > /root/.bashrc
# RUN echo "rm -rf /src/* && rm /root/.bashrc && rm /root/.profile" > /root/.profile

# USER mosamatic

CMD ["/docker-entrypoint.sh"]
