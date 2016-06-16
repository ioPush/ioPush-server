#!/usr/bin/env python
"""A noddy fake smtp server."""

import smtpd
import asyncore
import email
import requests
import json

class FakeSMTPServer(smtpd.SMTPServer):
    """A Fake smtp server""" 
    def __init__(*args, **kwargs):
        print("Running fake smtp server on port 25")
        smtpd.SMTPServer.__init__(*args, **kwargs)
    def process_message(self, peer, mailfrom, rcpttos, data):
        print('Peer :', peer)
        print('mailFrom :', mailfrom)
        print('rcpttos :',rcpttos[0])
        key = rcpttos[0].rsplit('@', 1)[0]
        print('key :', key)
        payload = {'body': email.header.decode_header(email.message_from_string(data).get('subject', None))[0][0].decode("utf-8"), 'push': 'True', 'httpcallback': 'True', 'httpcallback': 'True'}
        print('payload :', payload)
        header = {'authentication_token': key}
        r = requests.post('http://localhost/app/api/post', data=json.dumps(payload), headers=header)
        data = r.text
        print('data :', data)
        print('status :', r.status_code) 
        print("             ----------------------------               --------------------")
        '''
        b = email.message_from_string(data)
        subject = b.get('subject', None)
        if subject is not None:
          print('Suject type :', type(subject))
          print('Subject :', subject)
          print('Subject decoded :', email.header.decode_header(subject)[0][0])
        if b.is_multipart():
            for payload in b.get_payload():
                
                print(payload.get_payload(decode=True))
        else:
            print(b.get_payload(decode=True))
        '''
        
if __name__ == "__main__":
    smtp_server = FakeSMTPServer(('', 25), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        smtp_server.close()
