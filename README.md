# Pushpull

**AN EXPERIMENT**

[![Build Status](https://travis-ci.org/elastic-coders/pushpull.svg?branch=master)](https://travis-ci.org/elastic-coders/pushpull)

Websocket to message broker gateway for servers

```

    websocket client (browser) <---> pushpull gateway <----> message broker <--->(pushpull sdk) application tier

```

## Install

    pip install pushpull


## Test

1. install a rabbitmq server and a mongodb server
2. run `tox`


## Usage

Run the websocket server:

    pushpull-server

Run the CLI websocket client:

    pushpull-client challenge_websocket http://localhost:8080/ mario

Run the CLI rabbitmq client:

    pushpull-client challenge_amqp amqp://localhost/ mario

# Build docker image

use python3.5

install wheel

    pip install wheel

Build wheels for 3rd party and the project itself

``` bash
pip wheel -r requirements.txt -w wheelhouse
pip wheel . --no-deps -w wheelhouse-app
docker build -t pushpull .
```
