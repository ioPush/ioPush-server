# ioPush-server
Log keeper and Android-GCM push notification server (Python)

## Description
Work in progress but registration works, and API to post messages too.

The messages can be posts to http://siteAddress.xxx/api/post with the following JSON format:
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
 
