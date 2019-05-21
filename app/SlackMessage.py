""" SlackMessage.py is a set of predefined slack messages built from Slack Message Builder 
    for a specific SlackBot App project

This exports:
    - SlackMessage: contians predefine functions for the SlackBot App
"""

from app.SlackMessageBuilder import SlackMessageBuilder

class SlackMessage():
    
    def __init__(self) :
        self.messageBuilder = SlackMessageBuilder()

    def simpleText(self, message, text) :
        """ Creates response object to write simple text to Slack
        Parameters
            message - dict : The initial message that was sent from the Slack Web API
            text -  String : The text that you would like send to slack
        """
        response = {
            "text" : text,
            "type" : "text",
            "channel" : message.get("channel"),
            "user" : message.get("user")          
        }

        return response

    def listAllServices(self, message, services) :

        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        blocks = self._createListServiceBlock(services, buttonText="Info", action="info", heading="*Here are all the runnable services*")
        
        if(len(blocks) > 0) :
            response["blocks"] = blocks
        else :
            response["text"] = "There are no available services."

        return response

    def listMyServices(self, message, services) :
        
        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        blocks = self._createListServiceBlock(services, buttonText="Remove", action="remove", heading="*Here are all the services you are subscribe to:*")
        if(len(blocks) <= 0) :
            blocks = self._listMyServicesEmpty()

        response["blocks"] = blocks

        return response

    def singleService(self, message, action, text="", serviceOptions=[]) :
        """
        Paramerters:
            - message : original message from slack
            - action : type of service action being executed
            - text : text that is to be displayed on message
            - serviceOptions : list of services that you are able to run
        """
        defaultText = "Which service would you like to run?"

        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel")
        }
        options = []
        for service in serviceOptions :
            options.append(self.messageBuilder.newActions().getOptions(service.get("name"), service.get("name"), service.get("description")))

        actions = self.messageBuilder.newActions().addSelect(name=action, text="Select a service...", options=options).build()
        attachments = self.messageBuilder.newAttachment().addAttachment(text="Select a service...", callbackId=action, color="#e3dd3a", actions=actions).build()

        response["text"] = text if len(text) > 0 else defaultText
        response["attachments"] = attachments

        return response

    def unsubscribe(self, message, action, services) :
        
        defaultText = "Select which service you would like to unsubscribe from."

        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel")
        }

        # If user is subscribed to at least one service
        if(len(services) != 0) :
            options = []

            for service in services :
                options.append(self.messageBuilder.newActions().getOptions(service.get("name"), service.get("name"), service.get("description")))

            actions = self.messageBuilder.newActions().addSelect(name=action, text="Select a service...", options=options).build()
            attachments = self.messageBuilder.newAttachment().addAttachment(text="Select which service you would like to unsubscribe from.", callbackId=action, color="#e3dd3a", actions=actions).build()

            response["text"] = defaultText
            response["attachments"] = attachments

        response["text"] = "Which service would you like to unsubscribe to?"
        

        return response

    def subscribe(self, message, action, services) :
        
        options = []
        defaultText = "Which service would you like to subscribe to?"

        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        for service in services :
            options.append(self.messageBuilder.newActions().getOptions(service.get("name"), service.get("name"), service.get("description")))
        
        actions = self.messageBuilder.newActions().addSelect(name=action, text="Select a service...", options=options).build()
        attachments = self.messageBuilder.newAttachment().addAttachment(text=defaultText, callbackId=action, color="#e3dd3a", actions=actions).build()


        response["text"] = defaultText
        response["attachments"] = attachments
        
        return response

    def interactiveSubscription(self, message, periods, arguments, serviceName) :
        self.messageBuilder.newDialog(title="Subscribe to a Service", submitLabel="Request", state=serviceName, callbackId="subscribe")
        
        for period in periods :
            self.messageBuilder.getDialog().addOption(period, period)

        options = self.messageBuilder.getDialog().buildOptions()

        dialog = self.messageBuilder.getDialog() \
                .addTextElement("Description", "description", "Description") \
                .addSelectElement("Duration", "duration", options=options) \
                .addTextElement("Time", "time", "8AM or 11:17PM") \
                .build()

        response = {
            "type" : "dialog",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
            "trigger" : message.get("trigger_id"),
            "dialog" : dialog         
        }

        return response

    def interactiveService(self, message, serviceName) :
        pass

    def interactiveUnsubscription(self) :
        pass

    def dialogSubmission(self) :
        pass

    def updateDialog(self, message) :

        ts = message.get("original_message").get("ts") if message.get("original_message") != None else message.get("message").get("ts")
        text = message.get("original_message").get("text") if message.get("original_message") != None else message.get("message").get("blocks")[0].get("text").get("text")
        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
            "ts" : ts,
            "text" : text,
            "attachments" : [{ "text" : "You have selected {}".format(message.get("actions")[0].get("selected_options")[0].get("value"))}]
        }

        return response

    def requestUserArgs(self, message, arguments, serviceName) :
        
        response = {
            "type" : "dialog",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        self.messageBuilder.newDialog(title="Subscribe Arguments", submitLabel="Request", state=serviceName, callbackId="service")

        for argument in arguments :
            self.messageBuilder.getDialog().addTextElement(argument.get("name"), argument.get("name").lower(), "placeholder")

        response["dialog"] = self.messageBuilder.getDialog()
        response["trigger"] = message.get("trigger_id")
        
        return response

    def blockActionInfo(self, message, serviceName, serviceInfo ) :
        
        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        response["text"] = "*Service name*: " + serviceName + "\n*Description*: "+ serviceInfo

        return response

    # TODO: Uniquely update service with multiple names
    def blockActionRemove(self, message, services, service, successful) : 
        
        serviceName = service.get("name")
        _id = service.get("_id")

        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        if(successful) :

            # update removed services
            blocks = message.get("message").get("blocks")

            for block in blocks :
                if(block.get("accessory") != None) :
                    if(_id == block.get("accessory").get("value")) :
                        block["text"]["text"] = "You have successfully unsubscribed from " + serviceName
                        del block["accessory"]

            response["blocks"] = blocks
            response["ts"] = message.get("message").get("ts")

        else :
            response["text"] = "Sorry I was unable to unsubscribe you form " + serviceName + ". Please contact Slack Admins."

        return response

    def blockActionSubscribe(self, message, services, sub) :
        
        response = {
            "type" : "text",
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

        if(sub) :
            response = self.listAllServices(message, services)
            response["ts"] = message.get("message").get("ts")
        else :
            
            response["text"] = "You are not subscribed to any services. Would you like to view some services that you can subscribe to?"
            response["attachments"] = self.messageBuilder.newAttachment().addAttachment(text="Okay if you need anything, dont be afriad to ask.", callbackId="yeah" ,color="#e3dd3a").build()
            
            response["ts"] = message.get("message").get("ts")

        return response

    def _createResponse(self, message, rtype="text") :

        response = {
            "user" : message.get("user"),
            "channel" : message.get("channel"),
        }

    def _listMyServicesEmpty(self) :
        blocks = self.messageBuilder.newBlocks()
        blocks.addSection("You are not subscribed to any services. Would you like to view some services that you can subscribe to?", plain=False)
        elements = self.messageBuilder.newBlockElements().addButton("Sure", "sure", value="sure").addButton("No thanks", "no thanks", value="no thanks").getBlockElements()
        blocks.addAction(elements, blockId="subscribe")
        return blocks.getBlocks()

    def _createListServiceBlock(self, services, buttonText="", action="", heading="") :
        """ Creates a service dialog for the finance bot finance 
        Paramaters
            services - String
            buttonText - String
            heading - name of the service
        """
        blocks = self.messageBuilder.newBlocks()
        if(services != None) :
            blocks.addSection(heading, plain=False)
            for service in services :
                text = self._getDescriptionValue(service)
                value = service.get("_id") if service.get("_id") != None else service.get("name")
                accessory = self.messageBuilder.newAccessory().createButton(buttonText, actionId=action, value=value)
                blocks.addSection(text, accessory=accessory, plain=False)

        return blocks.getBlocks()

    def _getDescriptionValue(self, service) :

        serviceName = "_"+service.get("name")+"_"
        description = ""
        if(len(service.get("description")) > 56) :
            description = service.get("description")[0:57]+"..."
        else :
            description = service.get("description")

        return serviceName + "\n" + description

    def _getServiceInfo(self, services, serviceName) :
        for service in services :
            if(service.get("name") == serviceName) :
                return service.get("description")

    def _createDialogTextElement(self, argument) :

        return {
            "label": argument.get("name"),
            "name": argument.get("name").lower(),
            "type": "text",
            "placeholder": argument.get("placeholder")
            }

if __name__ == "__main__":
    pass