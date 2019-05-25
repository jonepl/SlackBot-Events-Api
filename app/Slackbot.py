'''
File: Slackbot.py
Description: Core class of the SlackBot application. All handlers and Scheduler class
             communicate to the Slack Servers using this class
'''

import threading, queue as Queue
from threading import Thread
from app.MessageHandler import MessageHandler
from app.Scheduler import Scheduler
from app.ServiceHandler import ServiceHandler
from app.SlackWebApi import SlackWebApi
from app.SlashCommandHandler import SlashCommandHandler
from app.SlackMessageBuilder import SlackMessageBuilder

class Slackbot(Thread) :
    def __init__(self, config, sConfig, debug) :
        Thread.__init__(self)
        self.slackclient = SlackWebApi(config.get("slack_bot_token"))

        # TODO Research Observer pattern to allow handlers to subscribe.
        # TODO Research method to dynamically instatiate Handlers
        self.messageHandlerQueue = Queue.Queue()
        self.serviceHandlerQueue = Queue.Queue()
        self.schedulerQueue = Queue.Queue()
        self.slackMessageBuilder = SlackMessageBuilder()
        self.messageHandler = MessageHandler(self, config, debug)
        self.serviceHandler = ServiceHandler(self, sConfig, debug)
        self.scheduler = Scheduler(self, config, debug)
        self.slashCommandHandler = SlashCommandHandler(self)
        self.startUpThreads()

    # Direct requests to correct handler
    # TODO: This maybe method to perform single cast updates
    def route(self, message) :

        handler = message.get("handler")
        if(handler is not None) :

            if(handler == 'messageHandler') :
                self.messageHandlerQueue.put(message)
            elif (handler == 'scheduler') :
                self.scheduler.put(message)
            elif(handler == 'serviceHandler') :
                self.serviceHandlerQueue.put(message)
            elif(handler == 'googleDocHandler') :
                pass
            else : 
                print("Unknown handler "+  handler)
        else :

            message["handler"] = "messageHandler"

            self.messageHandlerQueue.put(message)

    # TODO Research for loop approach for initiailze these
    def startUpThreads(self) :
        self.messageHandler.daemon = True
        self.scheduler.daemon = True
        self.serviceHandler.daemon = True
        self.messageHandler.setName("MessageHandler Thread")
        self.scheduler.setName("Scheduler Thread")
        self.serviceHandler.setName("ServiceHandler Thread")
        self.messageHandler.start()
        self.scheduler.start()
        self.serviceHandler.start()

    def getMessageHandlerQueue(self) :
        return self.messageHandlerQueue

    def getSchedulerQueue(self) :
        return self.schedulerQueue

    def getServiceHandlerQueue(self) :
        return self.serviceHandlerQueue

    def getMessageHandler(self) :
        return self.messageHandler

    def getSlashCommandHandler(self) :
        return self.slashCommandHandler

    def getServiceHandler(self) :
        return self.serviceHandler

    def getScheduler(self) :
        return self.scheduler

    def getHistory(self, channel) :
        return self.slackclient.getHistory(channel)

    def getSlackMessageBuilder(self) :
        return self.slackMessageBuilder

    # Responds back to Slack
    def respond(self, response, text=None, rType=None, channel=None, user=None, trigger=None, dialog=None, attachments=[], blocks=[], ts=None) :

        status = None

        response['text'] = text if text != None else response.get('text')
        response['type'] = rType if rType != None else response.get('type')
        response['channel'] = channel if channel != None else response.get('channel')
        response['user'] = user if user != None else response.get('user')

        # Required Values
        channel = response.get("channel")
        text = response.get("text")
        # Optional Values
        if(response.get("blocks") != None) : blocks = response.get("blocks")
        if(response.get("attachments") != None) : attachments = response.get("attachments")
        if(response.get("filepath") != None) : filepath = response.get("filepath")
        if(response.get("trigger") != None) : trigger = response.get("trigger")
        if(response.get("dialog") != None) : dialog = response.get("dialog")
        if(response.get("ts") != None) : ts = response.get("ts")

        if(response.get("ts") != None) :
            status = self.slackclient.updateMessage(channel, ts, text=text, attachments=attachments, blocks=blocks)

        elif(response.get('type') == 'text') :
            status = self.slackclient.writeToSlack(channel, text, attachments, blocks)
        elif(response.get('type') == 'file') :
            filepath = response.get('text')
            status = self.slackclient.writeToFile(channel, filepath)
        elif(response.get('type') == 'dialog') :
            status = self.slackclient.writeToDialog(trigger=trigger, dialog=dialog)
        else :
            print("Response object has an unknown type.")

        return status

if __name__ == "__main__":
    pass