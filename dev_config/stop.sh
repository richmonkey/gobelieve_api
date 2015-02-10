#!/bin/bash
/usr/local/python2.7/bin/uwsgi --stop /tmp/im_api.pid
/usr/local/python2.7/bin/uwsgi --stop /tmp/im_web.pid
/usr/local/python2.7/bin/uwsgi --stop /tmp/qr_login.pid
