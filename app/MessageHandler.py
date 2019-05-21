'''
File: MessageHandler.py
Description: Handles raw input and determines an appropriate response to send back to the user
'''

import random, logging, json, threading, time, queue as Queue
from threading import Thread

from app.ServiceHandler import ServiceHandler
from app.SlackMessage import SlackMessage

# if not __name__ == '__main__':
#     from app.SubscriptionHandler import SubscriptionHandler
#     import app.ServiceHandler

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(levelname)s : %(name)s : %(message)s')

# file_handler = logging.FileHandler('logs/MessageHandler.log')
# stream_handler = logging.StreamHandler()

# file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.INFO)

# stream_handler.setFormatter(formatter)
# stream_handler.setLevel(logging.DEBUG)

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

GREETING_KEYWORDS = ["hey", "hi", "greetings", "sup", "hello"]
SERVICE_KEYWORDS = ["service", "subscribe", "dialog"]
GREETING_RESPONSES = ["Sup bro.", "Hey.", "What it do!", "What up homie?", "Howdy."]
SERVICES_TYPES = [{"tempservice" : "hello_world"}, { "file" : "file_service"}]
SUBSCRIPTION_KEYWORDS = ["unsubscribe", "subscribe"]

class MessageHandler(Thread):
    
    def __init__(self, financeBot=None, config=None, debug=False) :
        Thread.__init__(self)

        self.financeBot = financeBot
        self.debug = debug
        self.message = SlackMessage()
        
        if(self.debug) : logger.debug('MessageHandler successfully created')

    # Entry point for thread
    def run(self) :
        self.running = True

        while(self.running) :
            try :
                if(self.financeBot.getMessageHandlerQueue().qsize() > 0) : 
                    message = self.financeBot.getMessageHandlerQueue().get()
                    self.financeBot.getMessageHandlerQueue().task_done()
                    #if(self.debug) : logger.debug("Message requested received from Bot {}".format(str(message)))
                    self.handle(message)

                time.sleep(0.5)

            except(KeyboardInterrupt, SystemError) :
                if(self.debug) : logger.debug("\n~~~~~~~~~~~ MessageHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n")
                #self.subscriptionHandler.kill()
                self.running = False

    # Parses all raw input from Slack
    def handle(self, message) :
        print(message)
        self.parseMessage(message)
        #if(self.debug) : logger.info("MessageHandler 2")

    # Kills Thread run method
    def kill(self) :
        self.running = False
        #if(self.debug) : logger.info("Terminating MessageHandler")

    # Parses the raw slack input into parts
    def parseMessage(self, message) :

        # NLP Logic can be add here before determining action #
        self.determineAction(message)

    # Determine what action to take depending on the message
    def determineAction(self, message) :

        userID = message.get('user')
        userMessage = message.get('text')
        channel = message.get('channel')

        text = None
        response = {}

        if(self.isGreeting(userMessage)) :
            #if(self.debug) : logger.debug("Greeting found return random choice")
            text = random.choice(GREETING_RESPONSES)
            response = self.message.simpleText(message, text)
            self.financeBot.respond(response)
        
        elif(self.isNewMember(message)) :
            response = self.message.simpleText(message, "Welcome to our slack Group.")
            self.financeBot.respond(response)

        elif(self.isServiceRequest(userMessage)) :
            self.financeBot.getServiceHandlerQueue().put(message)

        elif(self.isGoogleDocRequest(userMessage)) :
            self.financeBot.getGoogleDocHandlerQueue().put(message)
        
        else :
            response =  self.message.simpleText(message, "Im not sure how to decipher \"" + self.stripTag(userMessage) + "\".")
            self.financeBot.respond(response)

    # Determines if a message contains a greeting word
    def isGreeting(self, userMessage) :
        for greeting in GREETING_KEYWORDS :
            if(greeting in userMessage.lower()) :
                return True
        return False

    def isSlashCommand(self, text) :
        if("slash" in text.lower()) : return True
        else : return False

    def isServiceRequest(self, message) :
        for command in SERVICE_KEYWORDS :
            if(command in message.lower()) :
                return True
        return False

    def isGoogleDocRequest(self, message) :
        pass

    def isNewMember(self, message) :
        if(message.get('type') == 'member_joined_channel') :
            return True
        return False

    def isSubscriptionRequest(self, message) :
        for command in SUBSCRIPTION_KEYWORDS :
            if(command in message.lower()) :
                return True
        return False

    # TODO: Fix Me
    # Removes the Slack bot ID from a message
    def stripTag(self, message) :
        return message.replace('<@UF4GUF5H8>', '').rstrip()

if __name__ == '__main__' :
    pass