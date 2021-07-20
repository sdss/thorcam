FROM ubuntu:20.04

LABEL maintainer="gallegoj@uw.edu"

WORKDIR /opt

# Need to install libusb
RUN apt-get -y update
RUN apt-get -y install libusb-1.0-0 libusb-1.0-0-dev python3 python3-pip

# This Dockerfile is meant to be run with context the root of thorcam
COPY . thorcam

RUN rm -f thorcam/libfli*.so
RUN pip3 install -U pip wheel setuptools
RUN cd thorcam && pip3 install .

# This is the default port but the real port can be changed when
# starting the service.
EXPOSE 19995

# Default actor name. Can be overriden when running the container.
ENV ACTOR_NAME=thorcam

# Connect repo to package
LABEL org.opencontainers.image.source https://github.com/sdss/thorcam

# Need to use --host 0.0.0.0 because the container won't listen to 127.0.0.1
# See https://bit.ly/2HUwEms
ENTRYPOINT thorcam actor --host 0.0.0.0 \
           --actor-name $ACTOR_NAME start --debug
