#!/bin/sh
openssl pkcs12 -clcerts -nokeys -out apns_dev_cert.pem -in apns_dev_cert.p12
openssl pkcs12 -nocerts -out apns_dev_key.pem -in apns_dev_key.p12 -nodes
cp apns_dev_cert.pem cert.pem
cp apns_dev_key.pem key.pem
