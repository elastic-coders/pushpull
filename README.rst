########
Pushpull
########
A websocket to rabbitmq gateway
###############################

.. image:: https://travis-ci.org/elastic-coders/pushpull.svg?branch=master
    :target: https://travis-ci.org/elastic-coders/pushpull

**BETA**

Makes it easy to talk to websocket clients using rabbitmq queues.

Websocket to message broker gateway for servers::

  websocket client (browser) <---> pushpull gateway <----> message broker (rabbitmq) <---> your backend application 
                                                                                       \
                                                                                        \-> the authenticator module


Includes some standard authenticator modules


Install
#######

Requires python3.5+::

    pip install pushpull


Test
####

1. install a rabbitmq server and a mongodb server
2. run ``tox``


Usage
#####

Run the websocket server::

    pushpull-server

Run the CLI websocket client::

    pushpull-client challenge_websocket http://localhost:8080/pushpull user_token

Run the CLI rabbitmq client::

    pushpull-client challenge_amqp amqp://localhost/ user_id

Run the CLI rabbitmq authenticator::

    pushpull-client authenticate_amqp amqp://localhost/ pushpull.auth.simple_file:main,user_db.txt

The ``user_db.txt`` is a text file with one entry per line::

    user_id:username:user_token


Generating messages programmatically
####################################

To pass a message to a WebSocket client through RabbitMQ you can use `pika` Python module:

        connection = pika.BlockingConnection()
        channel = connection.channel()
        channel.basic_publish(exchange='pushpull.ws',
                              # routing_key='pushpull.ws', # broadcast to all open WebSockets
                              routing_key=('pushpull.ws.%d' % user_id),
                              body='{"test": "Test"}')
        connection.close()



Build docker image
##################

install wheel::

    pip install wheel

Build wheels for 3rd party and the project itself::

  pip wheel -r requirements.txt -w wheelhouse
  pip wheel . --no-deps -w wheelhouse-app
  docker build -t pushpull .
