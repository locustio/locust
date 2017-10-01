#!/bin/bash
# NOTICE: 
#
# This file must be saved with unix-style line endings or it will fail.
# 

# Update and install some dependencies
apt-get -y update 
apt-get -y install build-essential python-pip python-dev libev-dev libzmq-dev supervisor
cd /vagrant

pip install --use-mirrors pyzmq supervisor

# Checkout and install latest Locust from Github
python setup.py develop

# Starting supervisor which is configured to start Locust
supervisord -c examples/vagrant/supervisord.conf
