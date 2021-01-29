# Webex Call Status
## MQTT Bridge

This container will allow you to subscribe to call status events 
on a Webex Desk Pro (and possibly others, that's all I have). 

It will then send MQTT messages to a broker so that you can then 
take action based on whether or not your endpoint is in a call.

I built this specifically for use with Home Assistant and the instructions
will reflect that.

## Setup

You will need to have the API available on your endpoint. If your
endpoint is cloud managed, you'll need a local user.

Next you will need a basic auth token. You may find that 
[this](https://www.blitter.se/utils/basic-authentication-header-generator/) 
works for you to make one. If you worry about sending your password
to a random website, then make one via the method of your choice.

Finally, build and run the container.

Once this is stable I'll build it and get it on Docker Hub, for now
build your own. 

## Running
``` bash
docker run -d 