#!/bin/bash

uwsgi=/data/envs/test/bin/uwsgi
home=/data/envs/test
app_dir=/data/im_api

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5000 -M  -p 1 -w im --callable app -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/im_api.log --pidfile /tmp/im_api.pid --touch-reload /tmp/im_api.touch

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5001 --gevent 1000 -M -p 1 -w webapp  -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/im_web.log --pidfile /tmp/im_web.pid --touch-reload /tmp/im_web.touch

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5002 --gevent 1000 -M  -p 1 -w qr_login  -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/qr_login.log --pidfile /tmp/qr_login.pid --touch-reload /tmp/qr_login.touch
