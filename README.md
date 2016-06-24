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

    python -m pushpull.cli.server

Run the CLI websocket client:

    python -m pushpull.cli.client challenge_websocket http://localhost:8080/sock

Run the CLI rabbitmq client:

    python -m pushpull.cli.client challenge_amqp

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
