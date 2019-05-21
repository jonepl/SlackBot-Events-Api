'''
'''

class SlashCommandHandler():
    
    def __init__(self, financeBot=None) :
        self.financeBot = financeBot
    
    # Make into a static Method
    def handle(self, message) :

        if(message.get("command") == "/subscribe") :
            attachments = self.createAttachments(action="subscribe")
            self.financeBot.respond({}, text="Which service would you like to subscribe to?", rType="text", channel=message.get("channel"), attachments=attachments)

        elif(message.get("command") == '/service') :
            attachments = self.createAttachments(action="service")
            self.financeBot.respond({}, text="Which service would you like to run?", rType="text", channel=message.get("channel"), attachments=attachments)

        else :
            print("Unknown slash command.")
    
    def createServiceDialog(self, arguments=None, serviceName="") :

        dialog = {
            "title": "Service Arguments",
            "submit_label": "Request",
            "state" : serviceName,
            "callback_id": "service",
            "elements": []
        }

        if(len(arguments) != 0) :
            for argument in arguments :
                 dialog.get("elements").append(self._createDialogTextElement(argument))

        return dialog

    def createSubscriptionDialog(self, arguments=[], serviceName="") :

        serviceOptions = self._createDialogOptions(self.financeBot.getServiceHandler().getServices())
        periodOptions = self._createDialogOptions(self.financeBot.getScheduler().getPeriodicity())
        

        dialog = {
            "title": "Subscribe to a Service",
            "submit_label": "Request",
            "state" : serviceName,
            "callback_id": "subscribe",
            "elements": [
                {
                    "label": "Description",
                    "type": "text",
                    "name": "description",
                    "placeholder": "Description",
                },
                {
                    "label": "Duration",
                    "type": "select",
                    "name": "duration",
                    "placeholder": "How frequent...",
                    "options": periodOptions
                },
                {
                    "label": "Time",
                    "name": "time",
                    "type": "text",
                    "placeholder": "8AM or 11:17PM"
                }
            ]
        }

        if(len(arguments) != 0) :
            for argument in arguments :
                 dialog.get("elements").append(self._createDialogTextElement(argument))

        return dialog

    # Creates a attachment for services https://api.slack.com/docs/message-attachments
    def createAttachments(self, text=None, options=None, action=None) :

        if (text == None) :
            text = "Select a service"
        if (options == None) :
            options = self._createActionOptions(self.financeBot.getServiceHandler().getServices())
        else :
            options = self._createActionOptions(options)
        if (action == None) :
            action = "serviceList"

        attachments =  [{
            "text": text,
            "callback_id": action, 
            "color": "#3AA3E3", 
            "attachment_type": "default",
            "actions": [{
                "name": action,
                "text": "Select a service...",
                "type": "select",
                "options": options 
            }]
        }]

        return attachments

    # Creates a block to list services via https://api.slack.com/reference/messaging/blocks
    def createServiceBlock(self, services) :
        blocks = []

        heading = {
            "type": "section",
            "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "These are all are the available services:"
            }
        }

        divider = { "type": "divider" }

        blocks.append(heading)
        blocks.append(divider)

        for idx, service in enumerate(services) :
            content = {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": service.get("name") + "\n" + service.get("description")
                }
            }

            blocks.append(content)

            if( idx != len(services)-1 ) :
                blocks.append(divider)

        return blocks

    # 
    def _createDialogOptions(self, items) :

        options = []

        # FIXME Bad Code for Periodiciy
        
        for item in items :
            if isinstance(item, dict) :
                option = {
                    "label" : item.get("serviceName"),
                    "value" : item.get("serviceName")
                }
            else :
                option = {
                        "label" : item,
                        "value" : item
                    }
            options.append(option)
        
        return options

    # https://api.slack.com/docs/interactive-message-field-guide#option_fields
    def _createActionOptions(self, services) :
        options = []
        #options = ["Intro Service", "External Service", "Fundament Analysis"]

        for service in services :
            option = {
                "text" : service.get("name"),
                "value" : service.get("_id") if service.get("_id") != None else service.get("name"),
                "description" : service.get("description")
            }
            options.append(option)
        
        return options

    def _createDialogTextElement(self, argument) :

        return {
            "label": argument.get("name"),
            "name": argument.get("name").lower(),
            "type": "text",
            "placeholder": argument.get("placeholder")
            }

if __name__ == "__main__":
    pass