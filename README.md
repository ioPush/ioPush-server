# ioPush-server - [![Build Status](https://travis-ci.org/ioPush/ioPush-server.svg?branch=master)](https://travis-ci.org/ioPush/ioPush-server) [![Coverage Status](https://coveralls.io/repos/ioPush/ioPush-server/badge.svg?branch=master&service=github)](https://coveralls.io/github/ioPush/ioPush-server?branch=master)
Record keeper and Android-GCM push notification server.  
It can be considered like Twitter but for the big word (world ;-) of Internet of Things

To be used with a soon to arrive Android push application

## Description
Work in progress but user management works, and API to post messages too.

Messages can be post to https://iopush.net/app/api/post with the following JSON format.  
Although, a custom header "authentication_token" must be added with the authentification token found on user's page

```json
{
   "body": "Message body",
   "badge": "E",
}
```
Badge is optionnal and can be :
* E : Error
* S : Success/OK
* I : Info
* W : Warning

See examples following for more help.


## Instructions to install
 * git clone
 * Edit setup.sh to match you site-package...To be improved
 * cp misc/config.sample.py config.py
 * Edit config.py to match your needs (SMTP server, SECRET_KEY, PASSWORD_SALT)
 * ./setup.sh
 * ./db_create.py
 * ./run.py
 * Go to http://localhost:5000/
 * Login with user 123
 
## Why this software and what it should do
It is a part of my home automation system. I previoulsy used Twitter to keep record of warning/errors but it lacks some functionnalities, and since few months notifications does not works well on my phone.

So the it should be able to:
 * Keep record of events - Done
 * Send event to push message if asked
 * Manage users - Done
 * Send push notifications to Android, maybe other OS
 * Android application -> receive notifications - Tested in the [1st version](https://github.com/Oliv4945/ioPush)
 * Android application -> display user's record
 * Obvioulsy, have a nice design. But I am far away from being a good designer, so if some people want to help or submit pull request, your are welcome !

## Examples to send data
### Curl
Just use the following:
```bash
curl -X POST -H 'authentication_token: YourAuthToken' -d '{"body": "Message send with curl", "badge": "I"}' https://iopush.net/app/api/post
```
### Node-Red
 * Paste (Menu->Import->Clipboard) the following subflow in [Node-Red](http://nodered.org).
 * Edit the subflow, then modify "Add notification data" to set your server url and your Auth_Token 
 * That's all. The message's payload will be send to the server, and you can add a badge by adding a msg.badge property
```JSON
[{"id":"adeebf25.52114","type":"subflow","name":"ioPush","in":[{"x":70,"y":70,"wires":[{"id":"43d1e4b1.bc2e1c"}]}],"out":[{"x":569,"y":108,"wires":[{"id":"a9684432.5697b8","port":0}]}]},{"id":"43d1e4b1.bc2e1c","type":"function","name":"Add notification data","func":"msg2 = {};\nmsg2.payload = {};\nmsg2.url = \"https://iopush.net/app/api/post\";\nmsg2.method = \"POST\";\nmsg2.headers = {\"authentication_token\": \"Your auth token\"};\nmsg2.payload.body = msg.payload;\nmsg2.payload.badge = msg.badge;\nreturn msg2;","outputs":1,"noerr":0,"x":220,"y":70,"z":"adeebf25.52114","wires":[["31652b4f.ce9ad4"]]},{"id":"31652b4f.ce9ad4","type":"json","name":"","x":413,"y":71,"z":"adeebf25.52114","wires":[["a9684432.5697b8"]]},{"id":"a9684432.5697b8","type":"http request","name":"","method":"use","ret":"txt","url":"","x":447,"y":113,"z":"adeebf25.52114","wires":[[]]},{"id":"939cc31a.6c634","type":"subflow:adeebf25.52114","name":"","x":205,"y":356,"z":"3c426b18.c3bd94","wires":[[]]}]
```
### Sigfox - Arduino/Akeru
Just configure the Sigfox callback like the following picture.  
The "Custom payload config" is quite helpfull to format data.  
![alt-tag](https://iobook.net/jirafeau/f.php?h=1aN00QTO&p=1&k=e80f653d99)
