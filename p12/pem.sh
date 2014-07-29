#!/bin/sh
openssl pkcs12 -clcerts -nodes -out apns_dev_cert.pem -in apns_dev_cert.p12
cp apns_dev_cert.pem cert.pem
