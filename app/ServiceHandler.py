'''
File: ServiceHandler
Description: Handlers service request and service subscription sent through a thread safe Queue
'''

import sys, os, subprocess, re, json, time, datetime, bson
from threading import Thread
from app.SlackMessage import SlackMessage

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

SUPPORTED_LANGUAGES = ["python", "python3", "node"]

# TODO: Consider extracting ServiceHandler functionality out other classes
class ServiceHandler(Thread) :

    def __init__(self, financeBot=None, sConfig=None, debug=False) :
        Thread.__init__(self)
        self.financeBot = financeBot
        self.debug = debug
        self.validateConfig(sConfig)
        self.services = sConfig
        self.serviceNames = self.getServicesNames()
        self.runnableServices = _initRunnableServices(self.serviceNames)
        self.message = SlackMessage()

    def run(self) :
        self.running = True
        # TODO: Figure out multi-threaded solution
        while(self.running) :
            try :
                if(self.financeBot.getServiceHandlerQueue().qsize() > 0) : 

                    message = self.financeBot.getServiceHandlerQueue().get()
                    self.financeBot.getServiceHandlerQueue().task_done()
                    if(self.debug) : logger.debug("Message requested received from Bot {}".format(str(message)))
                    self.handleService(message)

                time.sleep(0.5)

            except(KeyboardInterrupt, SystemError) :
                if(self.debug) : logger.debug("\n~~~~~~~~~~~ ServiceHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n")
                self.running = False
    
    def handleService(self, message) :

        response = message

        # Text based requests using interactive blocks actions
        if(self.isListAllServiceRequest(message)) :
            response = self.message.listAllServices(message, self.services)
            status = self.financeBot.respond(response)

        # Text based request using interactive block actions
        elif(self.isListMyServicesRequest(message)) :
            usersServices = self.financeBot.getScheduler().getFullSubscriptions(message.get("user"))
            response = self.message.listMyServices(message, usersServices)
            status = self.financeBot.respond(response)
        
        # Text based request using interactive select actions in attachment
        elif(self.isSingleServiceRequest(message)) :
            response = self.message.singleService(message, action="service", serviceOptions=self.services)
            status = self.financeBot.respond(response)

        # Unsubscribe, subscribe using integactive select action
        elif(self.isSubscriptionRequest(message)) :
            if("unsubscribe" in message.get('text')) :

                usersServices = self.getServicesListForUsersId(message.get('user'))
                response =  self.message.unsubscribe(message, "unsubscribe", usersServices)
                self.financeBot.respond(response)

            elif ("subscribe" in message.get("text").lower()) :
                response =  self.message.subscribe(message, "subscribe", self.services)
                self.financeBot.respond(response)
            
            #self.handleSubscription(message)

        elif(self.isInteractiveMessage(message)) :
            self.handleInteractiveMessaege(message)

        elif(self.isDialogMessage(message)) :
            self.handleDialogMessage(message)

        else :
            response = self.message.simpleText(message, text="Not sure how to handle your service request")
            self.financeBot.respond(response)

    # Handles interaction slack action and block actions
    def handleInteractiveMessaege(self, message) :

        if("interactive_message" in message.get("type").lower()) :
            serviceName = message.get('actions')[0]["selected_options"][0].get("value")
            arguments = self.getServiceArguments(serviceName)

            # Handles subscription interactive message request
            if(message.get('actions')[0]["name"] == "subscribe") :
                response = self.message.interactiveSubscription(message, self.financeBot.getScheduler().getPeriodicity(), arguments, serviceName)
                self.financeBot.respond(response)

            # Runs service interactive message request
            elif(message.get('actions')[0]["name"] == "service") :
                if(len(arguments) == 0) :
                    message["state"] = serviceName
                    self.handleSubmission(message)

                else :
                    response = self.message.requestUserArgs(message, arguments, serviceName)
                    self.financeBot.respond(response)

            # Handles unsubscription interactive message request
            elif(message.get("actions")[0]["name"] == "unsubscribe") :
                _id = message.get('actions')[0]["selected_options"][0].get("value")
                subscription = self.financeBot.getScheduler().getSubscriptionById(message.get("user"), _id)
                serviceName = subscription.get("name")
                successful = self.financeBot.getScheduler().removeSubscription(subscription)

        elif ("block_actions" in message.get("type")) :

            if("info" in message.get("actions")[0].get("action_id")) :
                # Can be an id
                _id = message.get("actions")[0].get("value")
                service = self.getService(message.get("user"), _id)
                serviceName = service.get("name")

                response = self.message.blockActionServiceInfo(message, service)
                self.financeBot.respond(response)

            elif("remove" in message.get("actions")[0].get("action_id")) :
                
                # Prepare service object
                _id = message.get("actions")[0].get("value")
                user = message.get("user")
                service = self.getService(user, _id)
                service["user"] = message.get("user")
                successful = self.financeBot.getScheduler().removeSubscription(service)
                
                # Updates a message in slack
                usersServices = self.financeBot.getScheduler().getFullSubscriptions(message.get("user"))
                response = self.message.blockActionRemove(message, usersServices, service, successful)
                self.financeBot.respond(response)

            elif("no thanks" in message.get("actions")[0].get("action_id")) : 
                response = self.message.blockActionSubscribe(message, self.services, False)
                self.financeBot.respond(response)

            elif("sure" in message.get("actions")[0].get("action_id")) :
                response = self.message.blockActionSubscribe(message, self.services, True)
                self.financeBot.respond(response)

            # TODO: handle no thanks response from my subscriptions, not subscribed no thanks and sure case
            elif("subscribe" in message.get("actions")[0].get("action_id")) :
                resp = message.get("actions")[0].get("text")
                if( "subscribe" in resp.get("text").lower() ) :
                    # FIXME Bad code
                    serviceName = message.get("actions")[0].get("value")
                    arguments = self.getServiceArguments(serviceName)
                    response = self.message.interactiveSubscription(message, self.financeBot.getScheduler().getPeriodicity(), arguments, serviceName)
                    self.financeBot.respond(response)

        else :
            print("Some thing bad happened")

    def handleDialogMessage(self, message) :
        dialogType = message.get('type')
        if (dialogType == "dialog_submission") :
            successful = self.handleSubmission(message)

            if(not successful) :
                self.financeBot.respond({}, text="Something went wrong with your submission", rType='text', channel=message.get("channel"))
        elif(dialogType == "dialog_suggestion") :
            pass
        
        elif(dialogType == "dialog_cancellation") :
            pass

    # handles dialog submission. Use callback_id to distingush subscribe from service request
    def handleSubmission(self, message) :
        # runServices
        if(message.get("callback_id") == "service" ) :
            serviceName = message.get("state")

            request = {}
            request["name"] = serviceName
            request["user"] = message.get("user")
            request["channel"] = message.get("channel")
            request["submission"] = message.get("submission") if message.get("submission") != None else {}

            self.runService(request)

            return True
        # subscribe
        elif(message.get("callback_id") == "subscribe") :

            request = {
                "user" : message.get("user"),
                "channel" : message.get("channel"),
                "name" : message.get("state"),
                "submission" : message.get("submission")
            }

            successful = self.financeBot.getScheduler().addSubscription(request)
            if(successful) :
                response = {
                    "type" : "text",
                    "user" : message.get("user"),
                    "channel" : message.get("channel"),
                    "text" : ":white_check_mark: Success... You've been subscribed.",
                    "ts" : message.get("action_ts")
                }
                self.financeBot.respond(response)
                #self.financeBot.respond({}, text=":white_check_mark: Success... You've been subscribed.", rType='text', channel=message.get("channel"))
            return True

        else :
            print("Unknown Dialog Submission")
            return False

    #     
    def getServiceArguments(self, serviceName) :

        arguments = []
        for service in self.services :
            if(service.get("name") == serviceName) :
                arguments = service.get("arguments")
                break
        return arguments

    # Gets Service Names for Service
    def getServicesNames(self) :
        serviceNames = []
        for services in self.services :
            serviceNames.append(services['name'])
        return serviceNames

    # TODO: Finance bot use this
    def getServices(self) :
        return self.services

    # TODO: Utilize these 
    # Determines if a service is runnable
    def isRunnableService(self, serviceName) :

        if (serviceName in self.serviceNames) :
            return self.runnableServices[serviceName]
        return False

    # Set a service status status to not runnable
    def makeUnrunnableService(self, serviceName) :

        if(serviceName in self.runnableServices) :
            self.runnableServices[serviceName] = False

    # Set a service status status to runnable
    def makeRunnableService(self, serviceName) :

        if(serviceName in self.runnableServices) :
            self.runnableServices[serviceName] = True

    # Validate configuration file
    def validateConfig(self, configServices=None) :

        services = configServices if configServices != None else self.services
        
        for service in services :
            try:
                _isValidName(service.get("name"))
                _isValidType(service.get("type"))
                _isValidLanguage(service.get("language"))
                _isValidFilepath(service.get("filepath"))
                _isValidDescription(service.get("description"))
                _isValidateArguments(service.get("arguments"))
                #_validateCommands(service)
            except Exception as e:
                print("Exception: {} for service: {}".format(e, service))
                sys.exit(1)

    # Gets the details for a single service by name
    def getServiceDetailsByName(self, serviceName) :
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service
        return None

    def isValidServiceOutput(self, output) :
        valid = True
        if('responseType' in output and 'contents' in output) :

            if(output['responseType'].lower() == 'file') :
                try:
                    _isValidFilepath(output['contents'])
                except Exception as e:
                    valid = False
                    print("Invalid Path: " + str(e))

            elif(output['responseType'].lower() == 'text') :
                pass

            elif(output['responseType'].lower() == 'sharedfile') :
                pass
            
            else :
                valid = False
                print("Invalid responseType")
                #raise Exception("Invalid responseType")
        else :
            valid = False
            print("Output {} is malformed".format(output))
            #raise Exception("Output {} is malformed".format(output))
        
        return valid

    #TODO: Finsh this
    def runService(self, request) :
        # Write so runs without args works
        service = self.getServiceDetailsByName(request.get("name"))
        service["user"] = request.get("user")
        service["channel"] = request.get("channel")
        
        filePath = service.get("filepath")
        cmd = service.get("language")
        popenargs = [cmd, filePath]

        # FIXME: COntinue
        for key, value in request.get("submission").items() :
            for argument in service.get("arguments") :
                if(key.lower() in argument.get("name").lower()):
                    popenargs.append("-" + argument.get("flag"))
                    popenargs.append(value)
                    continue

        # additionalArg conditional argument
        if(service.get("additionalArgs")) :
            for argumnet in service.get("additionalArgs") :
                popenargs.append("-" + argumnet)

        # TODO Try catch return 
        output = subprocess.check_output(popenargs)
        
        response = self.validateServiceOutput(output)

        if(response is not None) :
            if(response.get("type") == "text") :

                self.financeBot.respond({}, text = response.get("content"), rType="text", user=service.get("user"), channel=service.get("channel"))
            if(response.get("type") == "file") :
                self.financeBot.respond({}, text = response.get("content"), rType="file", user=service.get("user"), channel=service.get("channel"))
        else :

            self.financeBot.respond({}, text = "There was an issue running {} Service".format(request.get("name")), rType="text", user=service.get("user"), channel=service.get("channel"))

    def validateServiceOutput(self, output) :
        output = output.decode('utf-8').replace("'", "\"").rstrip()
        outputJson = json.loads(output)

        if('type' in outputJson and 'content' in outputJson) :
            if(outputJson['type'].lower() == 'file') :
                try:
                    _isValidFilepath(outputJson['content'])

                except Exception as e:
                    print("Invalid Path: " + str(e))
                    return {}

            return outputJson
                
        else :
        
            print("Invalid responseType")
            return None  

    # TODO: Move to sevices
    def getAllServices(self) :
        serviceList = self.getServicesNames()
        text = "Available Services\n"
        for index, service in enumerate(serviceList) :
            text += "\t{}. {}\n".format(index+1, service)
        
        if(self.debug) : logger.debug("Service List Request found {}".format(text))
        return text
        
    # List of the services link to a userId
    def getServicesListForUsersId(self, userId) :
        usersSubscriptions = self.financeBot.getScheduler().getUsersSubscriptions()
        if(userId in usersSubscriptions) :
            return usersSubscriptions[userId]
        else :
            return []

    # Consider removing
    def getUsersSubscriptionsByUserId(self, user) :
        subscriptions = []
        usersSubscriptions = self.financeBot.getScheduler().getUsersSubscriptions()
        for usersSubscription in usersSubscriptions[user] :
            subscription = usersSubscription
            subscription["user"] = user
            subscriptions.append(subscription)
        return subscriptions

    def getServiceByName(self, serviceName) :
        for service in self.services :
            if(service.get("name") == serviceName) :
                return service

    def getService(self, user, _id) :
        # if id is an id
        service = None
        if( bson.objectid.ObjectId.is_valid(_id) ) :
            service = self.financeBot.getScheduler().getSubscriptionById(user, _id)
        else :
            for svc in self.services :
                if(svc.get("name") == _id) :
                    service = svc
                    break
        return service

    def isSubscriptionRequest(self, message) :
        text = message.get("text")
        if("subscribe" in text.lower() or "unschedule" in text.lower()) : return True
        else : return False

    def isInteractiveMessage(self, message) :
        cmd = message.get("type")
        if("interactive_message" in cmd.lower() or "block_actions" in cmd.lower()) : return True
        else : return False

    def isDialogMessage(self, message) :
        cmd = message.get("type")
        text = message.get("text")
        if("dialog_submission" in cmd.lower() or "dialog" in text.lower()) : return True
        else : return False

    def isSingleServiceRequest(self, message) : 
        text = message.get('text')
        if("run" in text.lower() or "service" in text.lower()) : return True
        else : return False

    def isListAllServiceRequest(self, message) :
        text = message.get('text')
        if('list' in text.lower() and 'services' in text.lower()) : return True
        else : return False

    def isListMyServicesRequest(self, message) :
        text = message.get('text')
        if('my' in text.lower() and 'services' in text.lower()) : return True
        else : return False

def _initRunnableServices(serviceNames) :

    runnableServices = {}

    for serviceName in serviceNames :
        runnableServices[serviceName] = True
    
    return runnableServices

def _isValidName(name) :
    #TODO Determine string length
    if(not name) :
        raise Exception("{} is an invalid service name".format(name))

def _isValidType(sType) :
    if(sType.lower() != "script" and sType.lower() != "api") :
        raise Exception("{} is an invalid service type".format(sType))

def _isValidLanguage(language) :
    if(language not in SUPPORTED_LANGUAGES) : 
        raise Exception("{} is not a supported language".format(language))

# TODO: Is this needed
def _isValidFilepath(path) :
    if(not os.path.exists(path)) :
        raise Exception("{} is an invalid fil path".format(path))   

def _isValidDescription(description) :
    if(not description) :
        raise Exception("{} is an invalid service description".format(description))

def _isValidateArguments(arguments) :
    for argument in arguments :
        if(argument.get("name") == None or argument.get("dataType") == None or argument.get("flag") == None or argument.get("placeholder") == None) :
            raise Exception("{} must have name, dataType and placeholder".format(arguement))
        if(argument.get("name") == "" or argument.get("dataType") not in ["string", "int"]) :
            raise Exception("{} is an invalid service type".format(arguement))

def _validateCommands(service):

    if('python' in service['language'].lower()) :

        languageVersion = subprocess.check_output(['python3', '--version'])
        version = languageVersion.decode('utf-8')

        if('Python' in version) :

            match = re.match(r'Python 3.[1-9].*', version)

            if(match == None) :
                raise Exception('Python version {} not supported.'.format(version.strip("\n")))
            
            else :
                print("Successfully validated {}".format(service['name']))
        else :
            raise Exception('Python is not supported on this machine')

def _checkFileInfo(service) :

    runnable = service['fileInfo']['runnable']
    dateModified = service['Info']['dateModified']

    if( isinstance(runnable, bool) and isinstance(dateModified, float) ) :
        if(service['path'].lower() != 'internal') :
            modified = os.path.getmtime('{}/{}'.format(service['path'], service['entrypoint']))
            if(modified > service['dateModified']) :
                service['runnable'] = True
                service['dateModified'] = modified
            elif(modified < service['dateModified']) :
                service['dateModified'] = modified
    else :
        raise Exception('Error in services.fileInfo. Set')

if __name__ == '__main__':
    pass