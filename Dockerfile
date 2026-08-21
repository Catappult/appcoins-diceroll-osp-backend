# Stage 1: Build Environment
FROM docker.io/python:3.12-slim AS build-env

USER root

RUN mkdir -p /install && \
    chown -R 10001:0 /install && \
    chgrp -R 0 /install && \
    chmod -R g=u /install

USER 10001:0

WORKDIR /usr/src/app

ARG CACHE_DATE=1970-01-01

COPY requirements.txt ./
RUN PYTHONUSERBASE=/install pip3 install --no-cache-dir --upgrade --user -r requirements.txt

COPY main.py ./

# Stage 2: Final Image
FROM docker.io/python:3.12-slim

USER root

WORKDIR /usr/src/app

COPY --from=build-env /install /usr/local
COPY --from=build-env /usr/src/app /usr/src/app

RUN chown -R 10001:0 /usr/src/app /usr/local && \
    chgrp -R 0 /usr/src/app /usr/local && \
    chmod -R g=u /usr/src/app /usr/local

ENV PATH=/usr/src/app:/usr/local/bin:$PATH
ENV PYTHONPATH=/usr/src/app

USER 10001:0

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
