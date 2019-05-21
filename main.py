'''
File: main.py
Description: Entry point for Events API Slack application
'''

import SlackEventsApi
from app.Slackbot import Slackbot
import json, argparse, sys, os

config = {}
with open('config/creds.json') as json_data:
    config = json.load(json_data)

sConfig = []
with open('config/serviceConfig.json') as json_data:
    sConfig = json.load(json_data)

if not os.path.exists("./logs"): os.makedirs("./logs")

def main():

    args = prepCmdArgs()
    try:
        # TODO: figure out how to integration SlackEventsApi and SlackBot
        myBot = Slackbot(config, sConfig, args.debug)
        myBot.getServiceHandler().validateConfig()
        SlackEventsApi.financeBot = myBot
        SlackEventsApi.listen(args.debug)

    except Exception as e:
        print("Exception: " + str(e))
        sys.exit(1)

def prepCmdArgs() :
    
    parser = argparse.ArgumentParser(description='Kicks off an instance of of a Slackbot')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    main()