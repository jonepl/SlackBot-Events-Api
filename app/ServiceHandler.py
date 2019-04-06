'''
File: ServiceHandler
Description: Handlers service request and service subscription sent through a thread safe Queue
'''

import sys, os, subprocess, re, json, time, datetime
from threading import Thread

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

SUPPORTED_LANGUAGES = ["python", "python3", "node"]
PERIOD_MAPPER = {
        "second" :("second", 20),
        "hour" : ("hour", 1),
        "dai" : ('day', 1),
        "day" : ('days', 1),
        "week" : ('week', 1),
        "month" : ('weeks', 4),
        "annual" : ('weeks', 52),
        "quarter" : ('weeks', 13),
        "year" : ('weeks', 52)
    }

# TODO: Consider extracting ServiceHandler functionality out other classes
class ServiceHandler(Thread) :

    def __init__(self, financeBot=None, sConfig=None, debug=False) :
        Thread.__init__(self)
        self.financeBot = financeBot
        self.debug = debug
        self.services = sConfig
        self.serviceNames = self.getServicesNames()
        self.runnableServices = _initRunnableServices(self.serviceNames)

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

        if(self.isListAllServiceRequest(message)) :
            self.financeBot.respond(response, text=self.getAllServices(), rType='text')

            # NOTE: Cooler way to list Services
            # self.financeBot.respond(response, text="Fetching services", rType='text', blocks=self.financeBot.getSlashCommandHandler().createServiceBlock(self.services))

        elif(self.isListMyServicesRequest(message)) :
            self.financeBot.respond(response, text=self.getMyServices(message), rType='text')

        elif(self.isSingleServiceRequest(message)) :
            self.handleSingleService(message)

        elif(self.isInteractiveMessage(message)) :
            self.handleInteractiveMessaege(message)

        elif(self.isSubscriptionRequest(message)) :
            self.handleSubscription(message)
        
        else :
            self.financeBot.respond(response, text = "Not sure how to handle your service request", rType="text")

    def handleSingleService(self, message) :
        
        attachments = self.financeBot.getSlashCommandHandler().createAttachments(action="service")
        self.financeBot.respond({}, text="Which service would you like to run?", rType="text", channel=message.get("channel"), attachments=attachments)

    # TODO Prevent subscribing to services already subscribed to
    def handleInteractiveMessaege(self, message) :

        if(message.get('type') == "interactive_message") :
            dialog = {}
            #FIXME: Bad Code
            serviceName = message.get('actions')[0]["selected_options"][0].get("value")
            arguments = self.getServiceArguments(serviceName)

            if(message.get('actions')[0]["name"] == "subscribe") :
                dialog = self.financeBot.getSlashCommandHandler().createSubscriptionDialog(arguments=arguments, serviceName=serviceName)
                
            elif(message.get('actions')[0]["name"] == "service") :
                if(len(arguments) == 0) :
                    message["state"] = serviceName
                    self.handleSubmission(message)

                else :
                    dialog = self.financeBot.getSlashCommandHandler().createServiceDialog(arguments=arguments, serviceName=serviceName)

            elif(message.get("actions")[0]["name"] == "unsubscribe") :
                _id = message.get('actions')[0]["selected_options"][0].get("value")
                subscription = self.financeBot.getScheduler().getSubscriptionById(message.get("user"), _id)
                serviceName = subscription.get("name")
                successful = self.financeBot.getScheduler().removeSubscription(subscription)

            else :
                print("Some thing bad happened")

            self.financeBot.updateMessage({}, message.get("channel"), message.get("original_message").get("ts"), attachments=[{ "text" : "You have selected {}".format(serviceName)}])

            self.financeBot.respond({}, text="text", rType="dialog", channel=message.get("channel"), user=message.get("user"), dialog=dialog, trigger=message.get("trigger_id"))

        elif (message.get('type') == "dialog_submission") :
            successful = self.handleSubmission(message)

            if(successful) :
                self.financeBot.respond({}, text="Success... You're subscribed", rType='text', channel=message.get("channel"))
            else :
                self.financeBot.respond({}, text="Something went wrong with your submission", rType='text', channel=message.get("channel"))

        else :
            print("Failed to handle Interactive Message")
    
    def handleSubscription(self, message) :

        # TODO: Uniquely identify unsubscriptions somehow
        if('unsubscribe' in message.get('text')) :

            usersServices = self.getServicesListForUsersId(message.get('user'))
            if(len(usersServices) != 0) :

                attachments = self.financeBot.getSlashCommandHandler().createAttachments(text="Select which service you would like to unsubscribe from.", options=usersServices, action="unsubscribe")
                self.financeBot.respond({}, text="Which service would you like to unsubscribe to?", rType="text", channel=message.get("channel"), attachments=attachments)
            else :
                self.financeBot.respond({}, text="You are not currently subscribed to any services.", rType="text", channel=message.get('channel'), user=message.get('user'))

        elif ("subscribe" in message.get("text").lower()) :
            attachments = self.financeBot.getSlashCommandHandler().createAttachments(text="Select which service you would like to subscribe to.", action="subscribe")
            self.financeBot.respond({}, text="Which service would you like to subscribe to?", rType="text", channel=message.get("channel"), attachments=attachments)
        
        else :
            print("Damn Freddy")
    
    def runSingleService(self, message) :
        attachments = self.financeBot.getSlashCommandHandler().createAttachments(action="service")
        self.financeBot.respond({}, text="Which service would you like to subscribe to?", rType="text", channel=message.get("channel"), attachments=attachments)
        
    def getServiceArguments(self, serviceName) :

        arguments = []
        for service in self.services :
            if(service.get("name") == serviceName) :
                arguments = service.get("arguments")
                break
        return arguments

    # handles dialog submission. Use callback_id to distingush subscribe from service request
    def handleSubmission(self, message) :
        #TODO have all time base fields and the fields from the service
        if(message.get("callback_id") == "service" ) :
            serviceName = message.get("state")

            request = {}
            request["name"] = serviceName
            request["user"] = message.get("user")
            request["channel"] = message.get("channel")
            request["submission"] = message.get("submission") if message.get("submission") != None else {}

            self.runService(request)

            return True

        elif(message.get("callback_id") == "subscribe") :

            request = {
                "user" : message.get("user"),
                "channel" : message.get("channel"),
                "name" : message.get("state"),
                "submission" : message.get("submission")
            }

            successful = self.financeBot.getScheduler().addSubscription(request)

            return True

        else :
            print("Unknown Dialog Submission")

    # Returns a function for a give serviceName
    def getFunction(self, methodName) :
        if(callable(getattr(self, methodName))) :
            return getattr(self, methodName)
        else :
            return None

    # Gets Service Names for Service
    def getServicesNames(self) :
        serviceNames = []
        for services in self.services :
            serviceNames.append(services['name'])
        return serviceNames

    def getServices(self) :
        return self.services

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
                _isValidPath(service.get("filepath"))
                _isValidType(service.get("type"))
                _isValidateArguments(service.get("arguments"))
                _hasDuplicatedName(self.serviceNames)
                #_validateCommands(service)
            except Exception as e:
                print("Exception: {} for service: {}".format(e, service))
                sys.exit(1)

    # Gets the details for a single service by name
    def getServiceDetails(self, serviceName) :
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service
        return None

    def getServiceFilePath(self, serviceName):
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service['filepath']
        return None

    def getSupportedLanguages(self) :
        return SUPPORTED_LANGUAGES

    def isValidServiceOutput(self, output) :
        valid = True
        if('responseType' in output and 'contents' in output) :

            if(output['responseType'].lower() == 'file') :
                try:
                    _isValidPath(output['contents'])
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

    # TODO fix messageInfo and response type
    def generateSlackResponseOutput(self, output, subscription) :
        
        outputJson = json.loads(output.decode('utf-8'))

        if('type' in outputJson and 'content' in outputJson) :
            
            if(outputJson['type'].lower() == 'file') :
                try:
                    _isValidPath(outputJson['content'])
                except Exception as e:
                    print("Invalid Path: " + str(e))
                    return None

            subscription['type'] = outputJson['type']
            subscription['text'] = outputJson['content']

            return subscription

        else :
            print("Invalid responseType")
            return None  

    # Produces an job identifier
    def produceTag(self, subscription) :
        return subscription.get('user') + "_" + subscription.get('name')

    #TODO: Finsh this
    def runService(self, request) :
        # Write so runs without args works
        service = self.getServiceDetails(request.get("name"))
        service["user"] = request.get("user")
        service["channel"] = request.get("channel")

        for i, value in enumerate(service.get("arguments")) :
            service.get("arguments")[i]["userValue"] = request.get("submission").get(value.get("name").lower())

        filePath = service.get("filepath")
        cmd = service.get("language")

        # TODO Try catch
        output = subprocess.check_output([cmd, filePath])
        
        response = self.validateServiceOutput(output)

        if(response is not None) :
            if(response.get("type") == "text") :

                self.financeBot.respond({}, text = response.get("content"), rType="text", user=service.get("user"), channel=service.get("channel"))
            if(response.get("type") == "file") :
                self.financeBot.respond({}, text = response.get("content"), rType="file", user=service.get("user"), channel=service.get("channel"))
        else :

            self.financeBot.respond({}, text = "There was an issue running {} Service".format(request.get("name")), rType="text", user=service.get("user"), channel=service.get("channel"))

    def validateServiceOutput(self, output) :

        outputJson = json.loads(output.decode('utf-8'))

        if('type' in outputJson and 'content' in outputJson) :
            if(outputJson['type'].lower() == 'file') :
                try:
                    _isValidPath(outputJson['content'])

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
        
    # TODO: Move to sevices
    def getMyServices(self, message) :

        myServices = self.getServicesListForUsersId(message.get('user'))

        if(len(myServices) == 0) :
            text = "You are not subscribed to any services."
        else :
            text = "You are currently Subscribed to:\n"
            for index, myService in enumerate(myServices) :
                text += "\t{}. {}\n".format(index+1, myService.get("name"))
        return text

    # List of the services link to a userId
    def getServicesListForUsersId(self, userId) :
        usersSubscriptions = self.financeBot.getScheduler().getUsersSubscriptions()
        if(userId in usersSubscriptions) :
            return usersSubscriptions[userId]
        else :
            return []

    def isSubscriptionRequest(self, message) :
        text = message.get("text")
        if("subscribe" in text.lower() or "unschedule" in text.lower() or "dialog" in text.lower()) : return True
        else : return False

    def isInteractiveMessage(self, message) :
        cmd = message.get("type")
        if("interactive_message" in cmd.lower() or "dialog_submission" in cmd.lower()) : return True
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
    if(not name) :
        raise Exception("{} is an invalid name".format(name))

def _isValidType(sType) :
    if(sType.lower() != "script" and sType.lower() != "api") :
        raise Exception("{} is an invalid service type".format(sType))

def _isValidateArguments(arguments) :
    for argument in arguments :
        if(argument.get("name") == None and argument.get("dataType") == None) :
            raise Exception("{} is an invalid service type".format(sType))
        if(argument.get("name") == "" or argument.get("dataType") not in ["string", "int"]) :
            raise Exception("{} is an invalid service type".format(sType))

def _isValidPath(path) :
    if(not os.path.exists(path) and 'internal' != path.lower()) :
        raise Exception("{} is an invalid fil path".format(path))
    
def _isValidLanguage(language) :
    if(not language in SUPPORTED_LANGUAGES) :
        raise Exception("{} is an unsupported language".format(language))

def _isValidEntrypoint(path, entrypoint) :
    fullpath = "{}/{}".format(path, entrypoint)
    if(not os.path.isfile(fullpath) and 'internal' != path.lower()) :
        raise Exception("{} is an invalid entrypoint point".format(fullpath))

def _hasDuplicatedName(services) :
    if(len(services) != len(set(services))) :
        raise Exception("Duplicate Service names found. Please use unique Service Names.")

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

def main():
    sh = ServiceHandler(sConfig=[])

if __name__ == '__main__':
    main()