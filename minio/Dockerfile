FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl wget dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://dl.min.io/server/minio/release/linux-amd64/minio && \
    chmod +x minio && \
    mv minio /usr/local/bin/

RUN pip install minio --no-cache-dir

RUN useradd -r -u 1000 -g root minio && \
    mkdir -p /model /audio && \
    chown -R minio:root /model /audio && \
    chmod -R u+rxw /model /audio

COPY model /model
COPY init.sh /usr/local/bin/
COPY init_minio.py /usr/local/bin/

RUN dos2unix /usr/local/bin/init.sh && \
    chmod +x /usr/local/bin/init.sh && \
    chmod +x /usr/local/bin/init_minio.py && \
    chown -R minio:root /model /audio && \
    chmod -R u+rxw /model /audio && \
    chown minio:root /usr/local/bin/init.sh && \
    chown minio:root /usr/local/bin/init_minio.py

USER minio
EXPOSE 9000 9001

ENTRYPOINT ["/usr/local/bin/init.sh"]