# ioPush-server - [![Build Status](https://travis-ci.org/ioPush/ioPush-server.svg?branch=master)](https://travis-ci.org/ioPush/ioPush-server) [![Coverage Status](https://coveralls.io/repos/ioPush/ioPush-server/badge.svg?branch=master&service=github)](https://coveralls.io/github/ioPush/ioPush-server?branch=master)
Record keeper and Android-GCM push notification server.  
It can be considered like Twitter but for the big word (world ;-) of Internet of Things

To be used with a soon to arrive Android push application

## Description
Work in progress but user management works, and API to post messages too.

Messages can be post to http://siteAddress.xxx/api/post with the following JSON format.  
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
