#!/bin/bash

uwsgi=/usr/local/bin/uwsgi
home=/usr/local/
app_dir=/vagrant/production/gobelieve/gobelieve_api

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5000 -M  -p 1 -w app --callable app -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/im_api.log --pidfile /tmp/im_api.pid --touch-reload /tmp/im_api.touch



$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5001 -M  -p 1 -w client --callable app -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/im_client_api.log --pidfile /tmp/im_client_api.pid --touch-reload /tmp/im_client_api.touch
