#!/bin/bash
#!/bin/bash

uwsgi=/usr/local/python2.7/bin/uwsgi
home=/usr/local/python2.7
app_dir=/vagrant/production/gobelieve/gobelieve_service/api

$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5000 -M  -p 1 -w app --callable app -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/im_api.log --pidfile /tmp/im_api.pid --touch-reload /tmp/im_api.touch


$uwsgi --uid nobody --gid nobody --chdir $app_dir --http :5001 -M  -p 1 -w demo --callable app -t 60 --max-requests 5000 --vacuum --home $home --daemonize /tmp/im_demo.log --pidfile /tmp/im_demo.pid --touch-reload /tmp/im_demo.touch


