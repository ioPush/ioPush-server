# ioPush-server - [![Build Status](https://travis-ci.org/ioPush/ioPush-server.svg?branch=master)](https://travis-ci.org/ioPush/ioPush-server) [![Coverage Status](https://coveralls.io/repos/ioPush/ioPush-server/badge.svg?branch=master&service=github)](https://coveralls.io/github/ioPush/ioPush-server?branch=master)
IoT logbook and Android push notification server.  
It can be considered like Twitter but for the big word (world ;-) of Internet of Things

To be used with a soon to arrive Android push application

## Description
Work in progress but basic service works :
 * User management
 * Device management
 * Push notifications to Android-GCM
A test server is in place : [ioPush.net](https://iopush.net/app)

## Usage
Messages can be posted with a POST request to `https://iopush.net/app/api/post` with the following JSON format.  
Although, a custom header `authentication_token` must be added with the authentication token found on user's page.

```json
{
   "body": "Message body",
   "badge": "E",
   "push": "True"
}
```
Badge is optional and can be :
* E : Error
* S : Success/OK
* I : Info
* W : Warning  
Push is optional, if set to `True` a push notification will be send to all user's devices.

See [examples](#examples-to-send-data) for more help, a GET request also works.  
Insecure `http://` connection is accepted only for `/app/api/post` endpoint, in order to allow devices that don't support SSL to post messages. If feasible, use `https://` secured connection.


## Instructions to install
 * git clone
 * Edit setup.sh to match you site-package...To be improved
 * cp misc/config.sample.py config.py
 * Edit config.py to match your needs (SMTP server, SECRET_KEY, PASSWORD_SALT, GCM API Key)
 * Change email address in index.html template
 * ./setup.sh
 * ./db_create.py
 * ./run.py
 * Go to http://localhost:5000/
 * Login with user 123
 
## Why this software
It is a part of my home automation system. I previously used Twitter as a logbook of warning/errors but it lacks some functionalities, and since few months notifications does not works well on my phone.

So the it should be able to:
 * Keep record of events - Done
 * Send event to push message if asked
 * Manage users - Done
 * Send push notifications to Android, maybe other OS - Done, Android app to be published
 * Android application -> receive notifications - Tested in the [1st version](https://github.com/Oliv4945/ioPush)
 * Android application -> display user's record
 * Obviously, have a nice design. But I am far away from being a good designer, so if some people want to help or submit pull request, your are welcome !

## Examples to send data
All examples are for POST request as issue a GET is most often simple. If you need some help just ask me or open an issue.
### Get
Test it in a browser with the following URL.  
When you implement a get request, be sure that the URL is percent encoded. The authentification token parameter must be `auth_token`
```
https://iobook.net/api/post?auth_token=YourAuthToken&body=Message&badge=S
```
### Curl
Just use the following:
```bash
curl -X POST -H 'authentication_token: YourAuthToken' -d '{"body": "Message send with curl", "badge": "I", "push": "True"}' https://iopush.net/app/api/post
```

### Node-Red
 * Paste (Menu->Import->Clipboard) the following subflow in [Node-Red](http://nodered.org).
 * Edit the subflow, then modify "Add notification data" to set your server url and your Auth_Token 
 * That's all
   * The message's payload will be send to the server
   * Add a badge : set a `msg.badge` property
   * Notify by push message : set a `msg.push` property to `True`
```JSON
[{"id":"adeebf25.52114","type":"subflow","name":"ioPush","in":[{"x":70,"y":70,"wires":[{"id":"43d1e4b1.bc2e1c"}]}],"out":[{"x":569,"y":108,"wires":[{"id":"a9684432.5697b8","port":0}]}]},{"id":"43d1e4b1.bc2e1c","type":"function","name":"Add notification data","func":"msg2 = {};\nmsg2.payload = {};\nmsg2.url = \"https://iobook.net/app/api/post\";\nmsg2.method = \"POST\";\nmsg2.headers = {\"authentication_token\": \"YourAuthToken\"};\nmsg2.payload.body = msg.payload;\nmsg2.payload.badge = msg.badge;\nmsg2.payload.push = msg.push;\nreturn msg2;","outputs":1,"noerr":0,"x":220,"y":70,"z":"adeebf25.52114","wires":[["31652b4f.ce9ad4"]]},{"id":"31652b4f.ce9ad4","type":"json","name":"","x":413,"y":71,"z":"adeebf25.52114","wires":[["a9684432.5697b8"]]},{"id":"a9684432.5697b8","type":"http request","name":"","method":"use","ret":"txt","url":"","x":447,"y":113,"z":"adeebf25.52114","wires":[[]]},{"id":"939cc31a.6c634","type":"subflow:adeebf25.52114","name":"","x":205,"y":356,"z":"3c426b18.c3bd94","wires":[["401e9113.bfe17"]]}]
```

### Arduino
See [this code](https://gist.github.com/Oliv4945/90a24612998153e7ae0d)

### Sigfox - Arduino/Akeru
Just configure the Sigfox callback like the following picture.  
The "Custom payload config" is quite helpful to format data.  
![alt-tag](https://iobook.net/jirafeau/f.php?h=1aN00QTO&p=1&k=e80f653d99)  
This screenshot is without notifications, but you can add it easily : add a comma at the end of the `"body"` line, then write `"push": "True"`
