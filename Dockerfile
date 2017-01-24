# Use Ubuntu as the OS and bash
FROM ubuntu:16.04
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

MAINTAINER James Matsumura (jmatsumura@som.umaryland.edu)

# Grab git as will need files/code from there
RUN apt-get update && apt-get install -y apt-utils \
				python3.5 \
				python3-pip \
				wget \
				git \
				iputils-ping \
				build-essential \
				chrpath \
				libssl-dev \
				libxft-dev \
				libfreetype6 \
				libfreetype6-dev \
				libfontconfig1 \
				libfontconfig1-dev

# Install phantomjs
ENV PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O /usr/bin/phantomjs-2.1.1-linux-x86_64.tar.bz2 \
				&& cd /usr/bin && tar -vxjf phantomjs-2.1.1-linux-x86_64.tar.bz2

# Use pip to grab Selenium
RUN python3.5 -m pip install selenium

# Make a directory for files to compare Manatee downloads with
RUN mkdir /manatee_testing \
				&& chmod 777 /manatee_testing

# Grab the relevant code/files
RUN git clone https://github.com/jmatsumura/auto_debug_mana.git /manatee_testing

# Must insert username,password,db as three space-separated arguments after headless_manatee_check.py
#CMD ["/bin/bash /usr/bin/python3.5 /manatee_testing/headless_manatee_check.py"]
