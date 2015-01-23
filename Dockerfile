FROM debian:wheezy
MAINTAINER Chris <c@crccheck.com>

RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python2.7 \
  python-dev \
  python-pip \
  libpq-dev > /dev/null

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt
