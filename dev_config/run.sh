#!/bin/bash
/usr/local/python2.7/bin/uwsgi --uid nobody --gid nobody  -H /usr/local/python2.7 --chdir /vagrant/dev/im_api --http :5000 --gevent 1000 -M  -p 1 -w im --callable app -t 30 --max-requests 5000 --vacuum  --daemonize /tmp/im_api.log --pidfile /tmp/im_api.pid --touch-reload /tmp/im_api.touch

/usr/local/python2.7/bin/uwsgi --uid nobody --gid nobody  -H /usr/local/python2.7 --chdir /vagrant/dev/im_api --http :5001 --gevent 1000 -M -p 1 -w webapp  -t 300 --max-requests 5000 --vacuum  --daemonize /tmp/im_web.log --pidfile /tmp/im_web.pid --touch-reload /tmp/im_web.touch

/usr/local/python2.7/bin/uwsgi --uid nobody --gid nobody  -H /usr/local/python2.7 --chdir /vagrant/dev/im_api --http :5002 --gevent 1000 -M  -p 1 -w qr_login  -t 300 --max-requests 5000 --vacuum  --daemonize /tmp/qr_login.log --pidfile /tmp/qr_login.pid --touch-reload /tmp/qr_login.touch
