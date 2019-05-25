'''
File: SlackEventsApi.py
Description: Main Adapter use to interface with Slack's Event API adapter
Info: List of Events can be found https://api.slack.com/events. Make 
      sure to Add Bot User Event in the Slack Event Subscriptions
'''

import logging, json, queue as Queue, threading
from slackeventsapi import SlackEventAdapter
from flask import Flask, jsonify, Response, request

config = {}
with open('config/creds.json') as json_data:
    config = json.load(json_data)

financeBot = None
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(config.get("slack_signing_secret"), "/slack/events", app)

# Start listening on configuration port for Slackbot
def start(bot, debug) :
    global financeBot
    financeBot = bot
    app.run(port=config['port'])

''' Custom API Endpoints '''
# Handles all slash commands. You must configure slash commands within your app at www.api.slack.com
@app.route("/slash", methods=['POST'])
def handleSlashCommand():
    message = {}
    message = request.values.to_dict()

    message['user'] = message['user_id']
    message['channel'] = message['channel_id']

    financeBot.getSlashCommandHandler().handle(message)
    return Response(), 200

# Handles all interactive messages commands. You must configure dialog commands within your app at www.api.slack.com
@app.route("/dialog", methods=["POST"])
def handleDialog() :
    message = json.loads(request.values.to_dict()['payload'])

    message['user'] = message['user']["id"]
    message['channel'] = message['channel']["id"]
    message['text'] = "dialog"

    financeBot.route(message)
    return Response(), 200

''' Slack API Endpoints via https://api.slack.com/events '''
# A message was sent to a channel
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data.get("event")

    if message.get("subtype") is None :
        # Handles direct messages
        if message.get('channel_type') == "im" :
            financeBot.route(message)

        # Handles messages in channels
        if message.get('channel_type') == "channel":
            financeBot.route(message)

# Subscribe to only the message events that mention your app or bot
@slack_events_adapter.on("app_mention")
def handle_direct_message(event_data) :
    
    message = event_data.get("event")
    financeBot.route(message)

# Slack API event triggered by a member joining
@slack_events_adapter.on("member_joined_channel")
def handle_message(event_data):

    message = event_data.get("event")
    financeBot.route(message)

@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))