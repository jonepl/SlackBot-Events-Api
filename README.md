# Slackbot Events Api Example
This is a basic example of how to build a slack bot using the events API.

## Main Features
1. Create runnable services by running custom scripts
2. Run single or reoccurring services via slash command or keywords
3. Google Document Reader (Soon to come)

## Explanation of Files
1. main.py: Entrypoint for the Slackbot application.
2. SlackEventHandler.py: Handler for events from the Slack Server
3. app/: Holders all application files
4. config/: Holds all configuration information
5. services/: Holds external services scripts and files

## How to Configure the Slack Bot Template
In order for this slack bot to work it will need a few keys to authenticate to slack, the contents of the config file as well as what they are can be found below. 
### creds.json
```json
{
    "slack_bot_token" : "Your SlackBot Token",
    "slack_signing_secret" : "Signing Secret",
    "port" : 8080,
    "mongoDB" : {
        "dbName" : "DB Name",
        "uri" : "DB uri",
        "collectionName" : "Collection Name"
    }
}
```

1. slack_bot_token: This is the token of the bot user configured in slack
2. slack_signing_secret: This is the signing secret that the bot will use to authenticate to the channel sent by the events subscription.

## Application Information

### Ngrok
In order to run this bot locally you are first going to need a tunneling software set up and configured. When you post a message in slack, the slack event handler will send a message to your server. As you will be running this locally you will need a way to forward that request to your local host. For this example I have used ngrok.


1. Create an application in slack via https://api.slack.com/
2. Add a bot user to the slack application
3. Navigate OAuth & Permissions and enable bot user. Don't for get to grab the Bot User *OAuth Access Token* and save it as your **slack_bot_token** and save it to your creds.json file
4. Grant the bot user chat:write:bot scope
5. Navigate to *Event subscriptions* and to on events for your app
6. Grant the subscribe to bot events the message.channels scope
7. Navigate to the *Basic Information* tab and grab your **slack_signing_secret** and save it to your creds.json file 
8. In terminal session a, launch ngrok 
    ```bash
    ./ngrok http 3000
    ```
9. In terminal session b, launch the slack bot
    ```bash
    pip3 install -r requirements.txt
    python3 slackbot_events_api_example.py
    ```

### DB Setup

Currently this application use MongoDB to store service data. You can get a 0.5 GB space at https://mlab.com or you may use any MongoDB Database as you wish. Setup your DB environment and add your **dbName**, **uri** and **collectionName** to you **creds.json** file



## References
[Coming Soon](https://www.youtube.com/watch?v=EYxAhK_eDx0)

Helpful Video: https://www.youtube.com/watch?v=EYxAhK_eDx0&t=168s
Thanks: https://github.com/CoffeeCodeAndCreatine
