#!/bin/bash
uwsgi=/data/envs/test/bin/uwsgi

$uwsgi --stop /tmp/im_api.pid
$uwsgi --stop /tmp/im_web.pid
$uwsgi --stop /tmp/qr_login.pid
