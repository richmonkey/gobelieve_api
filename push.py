import time
from apns import APNs, Frame, Payload

apns = APNs(use_sandbox=True, cert_file='./p12/cert.pem', key_file='./p12/key.pem')

token_hex = "3de24300ad38763e57b529b4c0ada31d23080681bdc3739605e69347106bc00d"
payload = Payload(alert="Hello World!", sound="default", badge=1)
apns.gateway_server.send_notification(token_hex, payload)

#for (token_hex, fail_time) in apns.feedback_server.items():
#    print token_hex, fail_time
