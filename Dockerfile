FROM python:3.5.1

RUN mkdir /tmp/build
WORKDIR /tmp/build
ADD ./wheelhouse ./wheelhouse
ADD requirements.txt ./
RUN python3.5 -m pip install --no-cache-dir --no-index -f wheelhouse -r requirements.txt && \
    rm -rf wheelhouse
ADD /wheelhouse-app ./wheelhouse-app
RUN python3.5 -m pip install --no-cache-dir --no-index -f wheelhouse-app --no-deps -U pushpull && \
    rm -rf wheelhouse-app

RUN adduser --disabled-password --disabled-login --home /app --system -q app
WORKDIR /app
USER app
ENTRYPOINT ["pushpull-server"]
EXPOSE 8080
