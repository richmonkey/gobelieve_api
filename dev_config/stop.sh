#!/bin/bash
uwsgi=/usr/local/bin/uwsgi

$uwsgi --stop /tmp/im_api.pid
$uwsgi --stop /tmp/im_client_api.pid


