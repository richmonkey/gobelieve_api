#!/bin/bash
uwsgi=/usr/local/python2.7/bin/uwsgi

$uwsgi --stop /tmp/im_api.pid
$uwsgi --stop /tmp/im_demo.pid

