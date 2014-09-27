#!/bin/sh
openssl pkcs12 -clcerts -nodes -out apns_dev_cert.pem -in sdk_demo_aps_dev.p12
openssl pkcs12 -clcerts -nodes -out apns_pro_cert.pem -in apns_pro_cert.p12
cp apns_pro_cert.pem cert.pem
