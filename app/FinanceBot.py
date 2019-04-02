'''
File: FinanceBot.py
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

class FinanceBot(Thread) :
    def __init__(self, config, sConfig, debug) :
        Thread.__init__(self)
        self.slackclient = SlackWebApi(config.get("slack_bot_token"))

        # TODO Research Observer pattern to allow handlers to subscribe.
        # TODO Research method to dynamically instatiate Handlers
        self.messageHandlerQueue = Queue.Queue()
        self.serviceHandlerQueue = Queue.Queue()
        self.schedulerQueue = Queue.Queue()

        self.messageHandler = MessageHandler(self, config, debug)
        self.serviceHandler = ServiceHandler(self, sConfig, debug)
        self.scheduler = Scheduler(self, config, debug)
        self.slashCommandHandler = SlashCommandHandler(self)
        self.startUpThreads()

    # Direct requests to correct handler
    # NOTE: This maybe method to perform single cast updates
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

    # TODO: Use Finance Bot message to prepare handler data and send single object ot slackClient to use
    def updateMessage(self, response, channel=None, ts=None, text=None, attachments=None) :
        
        response['text'] = text if text != None else response.get('text')
        response['channel'] = channel if channel != None else response.get('channel')
        response['ts'] = ts if ts != None else response.get('ts')
        response['attachments'] = attachments if attachments != None else response.get('attachments')

        self.slackclient.updateMessage(response.get("channel"), response.get("ts"), text=response.get("text"), attachments=response.get("attachments"))

    # Responds back to Slack
    def respond(self, response, text=None, rType=None, channel=None, user=None, trigger=None, dialog=None, attachments=[], blocks=[]) :

        response['text'] = text if text != None else response.get('text')
        response['type'] = rType if rType != None else response.get('type')
        response['channel'] = channel if channel != None else response.get('channel')
        response['user'] = user if user != None else response.get('user')

        channel = response.get("channel")
        text = response.get("text")

        if(response.get('type') == 'text') :
            self.slackclient.writeToSlack(channel, text, attachments, blocks)
        elif(response.get('type') == 'file') :
            filepath = response.get('text')
            self.slackclient.writeToFile(channel, filepath)
        elif(response.get('type') == 'dialog') :
            self.slackclient.writeToDialog(trigger=trigger, dialog=dialog)
        else :
            print("Response object has an unknown type.")

if __name__ == "__main__":
    pass