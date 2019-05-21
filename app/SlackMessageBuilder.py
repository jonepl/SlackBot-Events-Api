r"""  Slack Message Builder contains all messaging material needed for the slackClient module

This exports:
    - SlackMessage: returns complete message objects 
    - Attachments: helpper class for SlackMessage
    - Dialog: helpper class for SlackMessage
    - Blocks: helpper class for SlackMessage
    - BlockElments: helpper class for SlackMessage
    - Accesory: helpper class for SlackMessage

"""

# Basic Message formating https://api.slack.com/messaging/composing/formatting

class SlackMessageBuilder():
    
    def __init__(self) :
        # TODO: Research if static class is appropriate
        self.dialog = Dialog("title", "callbackId")
        self.blocks = Blocks()
        self.actions = Actions()
        self.blockElements = BlockElements()
        self.attachments = Attachments()
        self.accessory = Accessory()
        

    # Creates a dialog for user to enter arguments to run the service
    def createServiceDialog(self, title, callbackId, serviceName, arguments=[]) :
        """ Creates a service dialog for the finance bot finance 
        Paramaters
            title - String
            callbackId - String
            serviceName - name of the service
            arguments - Service Arguements
        """
        serviceDialog = {}
        
        if(len(arguments) != 0) :
            dialog = self.dialog.newDialog(title, callbackId, state=serviceName)

            if(len(arguments) != 0) :
                for argument in arguments :
                    dialog.addTextElement(argument.get("name"), argument.get("name").lower(), argument.get("placeholder"))
            serviceDialog = dialog.build()

        return serviceDialog

    # 
    def createSubscriptionDialog(self, title, callbackId, serviceName, periodicity, arguments=[]) :
        """ Creates a service dialog for the finance bot app 
        Paramaters
            title - String
            callbackId - String
            serviceName - name of the service
            periodicity - Array of periods
            arguments - Service Arguements
        """
        subscriptionDialog = {}

        if(len(arguments) != 0) :
            dialog = self.dialog.newDialog(title, callbackId, state=serviceName)

            dialog.addTextElement("Description", "description", placeholder="Description")
            dialog.addSelectElement("Duration", "duration", options=periodicity)
            dialog.addTextElement("Time", "time", placeholder="8AM or 11:17PM")

            if(len(arguments) != 0) :
                for argument in arguments :
                    dialog.addTextElement(argument.get("name"), argument.get("name").lower(), placeholder=argument.get("placeholder"))

            subscriptionDialog = dialog.build()
        
        return subscriptionDialog

    def createMessageAttachment(self, text, callbackId, services=None) :
        """ Creates a message attachment for the finance bot app 
        Paramaters
            text - text of the static select element
            callbackId - String
            servics - list of services
        """
        options = self._createAttachmentOptions(services)
        actions = Actions().addSelect(name=action, text="Select a service...", options=options).build()
        self.attachments.createAttachment(text=text, callbackId=callbackId,  actions=actions)

        return attachments
    
    def _createAttachmentOptions(self, services) :
        options = []

        for service in services :
            text = service.get("name")
            value = service.get("_id") if service.get("_id") != None else service.get("name")
            description = service.get("description")
            option = self.getAttachmentOption(text, value, description)
            options.append(option)
        
        return options

    def getAttachmentOption(self, text, value, description="") :
        """
        Parameters:
            text - String: 
            value - String:
        """
        option =  {
            "text" : text,
            "value" : value
        }

        if(len(description) > 0) : option["description"] = description

        return option

    def createListServiceBlock(self, services, buttonText="", heading="") :
        """ Creates a service dialog for the finance bot finance 
        Paramaters
            services - String
            buttonText - String
            heading - name of the service
        """
        blocks = Blocks()
        if(services != None) :
            blocks.addSection(heading, plain=False)
            for service in services :
                text = self.getDescriptionValue(service)
                accessory = self.accessory.createButton(buttonText, buttonText.lower(), value=service.get("name"))
                blocks.addSection(text, accessory=accessory, plain=False)

        return blocks.getBlocks()

    def getDescriptionValue(self, service) :

        serviceName = "_"+service.get("name")+"_"
        description = ""
        if(len(service.get("description")) > 56) :
            description = service.get("description")[0:57]+"..."
        else :
            description = service.get("description")

        return serviceName + "\n" + description

    def listMyServicesEmpty(self) :
        blocks = Blocks()
        blocks.addSection("You are not subscribed to any services. Would you like to view some services that you can subscribe to?", plain=False)
        elements = BlockElements().addButton("Sure", "subscribe", value="subscribe").addButton("No thanks", "no thanks", value="no thanks").getBlockElements()
        blocks.addAction(elements, blockId="subscribe")
        return blocks.getBlocks()

    # Deprecated
    def updateListMyServices(self, response) :

        blocks = Blocks()
        blocks.addSection("You are not subscribed to any services. Would you like to view some services that you can subscribe to?\n" + response + " selected.", plain=False)
        return blocks.getBlocks()

    def newDialog(self, title="", callbackId="", elements=[], state="", submitLabel="Submit", notifyOnCancel=False) :
        self.dialog = Dialog(title, callbackId, [], state, submitLabel, notifyOnCancel)
        return self.dialog

    def getDialog(self) :
        return self.dialog

    def newBlocks(self) :
        """
            Blocks are a series of components that can be combined to create visually rich and compellingly interactive messages.
        """
        self.blocks = Blocks()
        return self.blocks

    def newBlockElements(self) :
        """
            Block elements can be used inside of section, context, and actions layout blocks.
        """
        self.blockElements = BlockElements()
        return self.blockElements

    def newAccessory(self) :
        """
            Block elements can be used inside of section, context, and actions layout blocks.
        """        
        self.accessory = Accessory()
        return self.accessory

    def newActions(self) :

        return Actions()

    def newAttachment(self) :
        self.attachments = Attachments()
        return self.attachments
    
    def getTextObject(text, plain=True, emoji=False, verbatim=False) :
        """
        Parameters:
            text - String or Text Object: 
            plain - Boolean: plain_text if True mkdwn if False
            emoji - Boolean: enable False
            verbatim -  When set to true will skip any preprocessing of this nature, although you can still include manual parsing strings. This field is only usable when type is mrkdwn
        """
        return _getTextObject(text, plain, emoji, verbatim=verbatim)

# https://api.slack.com/interactive-messages
# https://api.slack.com/docs/interactive-message-field-guide#action_fields
class Actions() :
    """ Only to to be used with attachments
    """

    def __init__(self) :
        self.actions = []

    def newActions(self) :
        self.actions = []
        return self

    def addButton(self, name, text, value="", style="default", confirm={}) :
        """
        Paramaters
            name - String
            text - String
            value - Boolean
            style - String : options primary & danger
            confirm - Confirm
        """
        button = {
            "name" : name,
            "text" : text,
            "type" : "button"
        }

        if(len(value) > 0 ) : button["value"] = value
        if(style != "default") : button["style"] = style
        if(len(confirm) != 0) : button["confirm"] = confirm

        self.actions.append(button)
        return self
    
    def addSelect(self, name, text, options) :
        """
        Paramaters
            name - String
            text - String
            value - Boolean
            style - default
            confirm - Confirm
        """

        select = {
            "name": name,
            "text": text,
            "type": "select",
            "options": options 
        }

        self.actions.append(select)
        return self

    def build(self) :
        return self.actions


    def getConfirmObject(self, title="Confirm", text="Are you sure?", okText="Yes", dismissText="No") :
        """
        Parameters:
            title - String
            text - String
            okText - String
            dismissText - String
        """

        confirmObject = {
            "title" : title,
            "text" : text,
            "ok_text" : okText,
            "dismiss_text" : dismissText
        }

        return confirmObject

    def getOptions(self, text, value, description) :
        """
        Paramaters
            text - String
            value - Boolean
            description - description
        """

        return { 
            "text": text, 
            "value": value,
            "description" : description
        }

# TODO: Figure out a way to create actions in attachment
#  https://api.slack.com/docs/message-attachments
class Attachments() :

    def __init__(self) :
        self.attachments = []
        self.actions = []

    def addAttachment(self, actions=[], authorIcon="", authorLink="", authorName="", blocks=[], callbackId = "", color="", fallback="", fields=[], footer="", footerIcon="", imageUrl="", mrkdwnIn="", pretext="", text="", thumbUrl="", title="", titleLink="", ts=None) :

        attachment = {}

        if(len(actions) > 0) : attachment["actions"] = actions        
        if(len(authorIcon) > 0) : attachment["author_icon"] = authorIcon
        if(len(authorName) > 0) : attachment["author_name"] = authorName
        if(len(blocks) > 0) : attachment["blocks"] = blocks
        if(len(callbackId) > 0) : attachment["callback_id"] = callbackId
        if(len(color) > 0) : attachment["color"] = color
        if(len(fallback) > 0) : attachment["fallback"] = fallback        
        if(len(fields) > 0) : attachment["fields"] = fields # TODO: Validation on fields
        if(len(footer) > 0) : attachment["footer"] = footer
        if(len(footerIcon) > 0) : attachment["footer_icon"] = footerIcon
        if(len(imageUrl) > 0) : attachment["image_url"] = imageUrl
        if(len(mrkdwnIn) > 0) : attachment["mrkdwn_in"] = mrkdwnIn
        if(len(pretext) > 0) : attachment["pretext"] = pretext
        if(len(text) > 0) : attachment["text"] = text
        if(len(thumbUrl) > 0) : attachment["thumb_url"] = thumbUrl
        if(len(title) > 0) : attachment["title"] = title
        if(len(titleLink) > 0) : attachment["title_link"] = titleLink
        if(ts != None) : attachment["ts"] = ts

        self.attachments.append(attachment)
        return self

    def createAttachmentField(self, title, value, short=False) :

        fields = {
            "title" : title,
            "value" : value
        }

        if(short == True) : fields["short"] = True

        return fields

    def build(self) :
        return self.attachments

class Accessory() :

    def createImage(self, imageUrl, altText, title=None, blockId="") :

        image = {
            "type" : "image",
            "image_url" : imageUrl,
            "alt_text" : altText,
        }

        if(title != None) : image["title"] = title
        if(len(blockId) != 0) : image["block_id"] = blockId

        return image
    
    def createButton(self, text, actionId, plain=True, emoji=False, value="", style="default", confirm=None) :
        """
        Paramaters
            text - TextObject
            actionId - String
            plain - Boolean
            emoji - Boolean
            style - default
            confirm - Confirm Object https://api.slack.com/reference/messaging/composition-objects#confirm
        """
        if(isinstance(text, str)) : 
            text = _getTextObject(text, plain=plain, emoji=emoji)

        button =  {
            "type" : "button",
            "text" : text,
            "action_id" : actionId,
        }

        if(len(value) != 0) : button["value"] = value
        if(confirm != None) : button["confirm"] = confirm
        if(style != "default") : button["style"] = style

        return button

    def createSelectMenu(self, placeholder, actionId, options=[], optionGroups=[], initialOption={}, confirm={}) :
        """
        Paramaters
            placeholder - TextObject
            actionId - String
            options - Array Options Object or Options Groups
            options Group - Array options Groups or Options Object 
            initalOption - Options or Options Group Object: A single option that exactly matches one of the options within options or option_groups
            confirm - Confirm Object https://api.slack.com/reference/messaging/composition-objects#confirm
        """
        selectMenu = { }

        if(_isTextObject(placeholder) and (_isOptionsObject(options) or _isOptionsGroupObject(optionsGroup)) and (len(options) > 0  or len(optionGroups) > 0) ) :
            selectMenu = {
                "type" : "static_select",
                "placeholder" : placeholder,
                "action_id" : actionId
            }

            if( len(options) > 0) :
                selectMenu["options"] = options
            elif( len(optionGroups) > 0) :
                selectMenu["option_groups"] = optionGroups
            else :
                return {}

            if(_isOptions(initialOption) or _isOptionGroups(initialOption)) :
                selectMenu["initial_option"] = initialOption

            if(_isConfirmObject(confirm)) :
                selectMenu["confirm"] = confirm

        return selectMenu

    def createOverflowMenu(self, actionId, options, confirm={}) :
        """
        Paramaters
            actionId - String
            options - Array Options Object or Options Group
            confirm - confirm https://api.slack.com/reference/messaging/composition-objects#confirm
        """        
        menu = {}
        
        if(len(actionId) > 0  and _isOptionsObject(options)) :
            menu = {
                "type" : "overflow",
                "action_id" : actionId,
                "options" : options
            }
            if(len(confirm) != 0): menu["confirm"] = confirm
        
        return menu

    def createDatePicker(self, actionId, placeholder={}, initialDate="", confirm={}) :
        """
        Paramaters
            actionId - String
            placeholder - Text Object
            initial date - String: YYYY-MM-DD
            confirm - Confirm Object
        """     
        datePicker = {}

        if(len(actionId) > 0) :
            datePicker = {
                "type" : "datepicker",
                "action_id" : actionId
            }

            if(_isTextObject(placeholder)) : datePicker["placeholder"] = placeholder
            if(len(initialDate) > 0) : datePicker["initial_date"] = initialDate
            if(confirm.get("title") != None and confirm.get("text") != None and confirm.get("confirm") != None and confirm.get("deny") != None) :
                datePicker["confirm"] = confirm

        return datePicker

    def _getTextObject(self, text, plain=True, emoji=False) :
        """
        Parameters:
            text - String: 
            value - String: Option value 75 character max
        """

        textObject = { "text" : text }

        if(plain) : textObject["type"] = "plain_text"
        else : textObject["type"] = "mrkdwn"
        if(emoji) : textObject["emoji"] : True

        return textObject

# https://api.slack.com/dialogs
class Dialog() :
    """
        Dialog class uses to construct Slack Dialog messages. This Dialog class uses
        the Builder pattern to append Dialog form Objects to the Dialog class. Once 
        all elements are added to your Dialog use the build method to produce Slack Dialog
    """

    def __init__(self, title, callbackId, elements=[], state="", submitLabel="Submit", notifyOnCancel=False) :
        """
            Parameters
                - title: String
                - callbackId: String
                - elements: Array of Dialog Elements
                - state
                - sumbitLabel
                - notifyOnCancel
        """
        self.options = []
        self.optionGroups = []
        self.dialog = {
            "title" : title,
            "callback_id" : callbackId,
            "elements" : elements
        }
        
        if(len(state) != 0) : self.dialog["state"] = state
        if(submitLabel != "Submit") : self.dialog["submit_label"] = submitLabel
        if(notifyOnCancel != False) : self.dialog["notify_on_cancel"] = True

    def newDialog(self, title, callbackId, elements=[], state="", submitLabel="Submit", notifyOnCancel=False) :
        """
            Parameters
                - title: String
                - callbackId: String
                - elements: Array of Dialog Elements
                - state
                - sumbitLabel
                - notifyOnCancel
        """
        self.dialog = {
            "title" : title,
            "callback_id" : callbackId,
            "elements" : elements
        }

        self.options = []
        self.optionGroups = []
        
        if(len(state) != 0) : self.dialog["state"] = state
        if(submitLabel != "Submit") : self.dialog["submit_label"] = submitLabel
        if(notifyOnCancel != False) : self.dialog["notify_on_cancel"] = True

        return self

    def setTitle(self, title) :
        self.dialog["title"] = title
        return self

    def setCallbackId(self, callbackId) :
        self.dialog["callback_id"] = callbackId
        return self

    def setElements(self, elements) :
        self.dialog["elements"] = elements
        return self

    def setState(self, state) :
        self.dialog["state"] = state
        return self

    def setSubmitLabel(self, submitLabel) :
        self.dialog["submit_label"] = submitLabel
        return self

    def setTitle(self, title) :
        self.dialog["title"] = notifyOnCancel
        return self

    def setTitle(self, notifyOnCancel) :
        self.dialog["notify_on_cancel"] = notifyOnCancel
        return self

    # https://api.slack.com/dialogs#text_elements
    def addTextElement(self, label, name, placeholder="", subtype="", minLength=-1, maxLength=-1) :
        """
            Parameters
                - label : String 48 character maximum
                - name : Element name 300 character maximum
                - placeholder : String 150 character maximum
                - subtype : String can be email, number, tel, or url
                - minLength : minimum length of zero
                - maxLength : maximum length of 150
        """
        element = {
            "label": label,
            "name": name,
            "type": "text",
        }

        if(len(placeholder) != 0) : element["placeholder"] = placeholder
        if(len(subtype) != 0) : element["subtype"] = subtype
        if(minLength > -1) : element["min_length"] = minLength
        if(maxLength < 0 and maxLength >= 150) : element["max_length"] = maxLength

        self.dialog["elements"].append(element)
        return self

    # https://api.slack.com/dialogs#textarea_elements
    def addTextAreaElement(self, label, name, placeholder="", value="", optional=False, hint="") :
        element = {
            "label": label,
            "name": name,
            "type": "textarea",
            "optional" : optional
        }

        if(len(hint) != 0) : element["hint"] = hint
        if(len(placeholder) != 0) : element["placeholder"] = placeholder
        if(len(value) != 0) : element["value"] = value

        self.dialog["elements"].append(element)
        return self

    # https://api.slack.com/dialogs#attributes_select_elements
    def addSelectElement(self, label, name, options, option_groups=[]) :
        element = {
            "label": label,
            "type": "select",
            "name": name,
            "options" : options
        }

        self.dialog["elements"].append(element) 

        return self

    def addOption(self, label, value) :
        """
        Parameters:
            options - Array
            label - String 
            value - String
        """
        if(len(label) != 0 and len(value) != 0 ) :
            self.options.append({ "label" : label, "value" : value })

        return self

    def addOptionGroups(self, label, options) :
        if(len(label) != 0 and isinstance(options, list)) :
            self.optionGroups.append({"label" : label, "options" : options})

        return self

    # https://api.slack.com/reference/messaging/composition-objects#option
    def getOptions(self) :
        options = self.options
        self.options = []
        return options
    
    def getOptionsGroup(self) :
        optionGroups = self.optionGroups
        self.optionGroups = []
        return optionGroups

    def __str__(self):
        return str(self.dialog)

    def build(self) :
        return self.dialog

    def buildOptions(self) :
        return self.options

    def buildOptionGroup(self) :
        return self.optionGroups

# https://api.slack.com/reference/messaging/blocks
class Blocks() :

    def __init__(self) :
        self.blocks = []

    def addSection(self, text, blockId="", plain=True, fields=[], accessory={}) :
        """
        Paramaters
            text - TextObject
            blockId - String
            plain - Boolean: Plain text or Slack Markdown
            fields - Array of TextObjects
            accesory - BlockElement
        """
        text = _getTextObject(text, plain=plain)

        sectionBlock = {
            "type": "section",
            "text": text
        }

        if(len(blockId) != 0) : sectionBlock["block_id"] = blockId
        if(len(fields) != 0) : sectionBlock["fields"] = fields
        if(len(accessory) != 0) : sectionBlock["accessory"] = accessory

        self.blocks.append(sectionBlock)
        return self

    def addDivider(self, blockId="") :
        """
        Paramaters
            blockId - String
        """
        divBlock = {
            "type" : "divider",
        }

        if(len(blockId) != 0) : divBlock["block_id"] = blockId
        self.blocks.append(divBlock)

        return self

    def addImage(self, imageUrl, altText, title=None, blockId="") :
        """
        Paramaters
            imageUrl - String
            altText - String
            text - String
            title - TextObject
            blockId - String
        """
        imageBlock = {
            "type" : "image",
            "image_url" : imageUrl,
            "alt_text" : altText
        }

        if(title != None) : imageBlock["title"] = title
        if(len(blockId) != 0) : imageBlock["block_id"] = blockId
        self.blocks.append(imageBlock)

        return self

    def addAction(self, elements, blockId="") :
        """
        Parameters:
            elements - Array of BlockElements max 5 elements. Buttons, Select Menu, Overflow Menu, Date Pickers
            blockId - String: Option value 75 character max
        """    
        actionBlock = {
            "type" : "actions",
            "elements" : elements
        }

        if(len(blockId) != 0) : actionBlock["block_id"] = blockId
        self.blocks.append(actionBlock)

        return self
        
    def addContext(self, elements, blockId="") :
        """
        Parameters:
            elements - Array[TextObject | ImageElement]: max 10 items 
            value - String: Option value 75 character max
        """      
        contextBlock = {
            "type" : "context",
            "elements" : elements
        } 

        if(len(blockId) != 0) : contextBlock["block_id"] = blockId
        self.blocks.append(contextBlock)
        return self

    def _getImageElement(self, imageUrl, altText, title=None, blockId="") :
        """
        Parameters:
            imageUrl - Array[TextObject | ImageElement]: max 10 items 
            altText - String: Option value 75 character max
            title - String
            blockId - String
        """ 
        imageElement = {
            "type" : "image",
            "image_url" : imageUrl,
            "alt_text" : altText,
            "title" : title,
            "block_id" : blockId
        }        
        
        if(title != None) : imageElement["title"] = title
        if(len(blockId) != 0) : imageElement["block_id"] = blockId
        
        return imageElement

    def __str__(self):
        return str(self.blocks)

    def __newBlocks(self):
        pass

    def getBlocks(self) :
        blocks = self.blocks
        self.blocks = []
        return blocks

# https://api.slack.com/reference/messaging/block-elements
# TODO: Append empty element on failure or no element
class BlockElements() :

    def __init__(self) :
        self.elements = []

    def addImage(self, imageUrl, altText, blockId="") :
        """
        Parameters
            imageUrl - String
            altText - String
            blockId - String
        """
        element = {
            "type" : "image",
            "image_url" : imageUrl,
            "alt_text" : altText,
        }

        if(len(blockId) != 0) : element["block_id"] = blockId

        self.elements.append(element)
        return self

    def addButton(self, text, actionId, plain=True, value="", emoji=False, style="default", confirm=None) :
        """
        Paramaters
            text - String or TextObject
            actionId - String
            plain - Boolean
            emoji - Boolean
            style - default
            confirm - Confirm Object https://api.slack.com/reference/messaging/composition-objects#confirm
        """
        if(isinstance(text, str)) : 
            text = _getTextObject(text, plain=plain, emoji=emoji)
        button =  {
            "type" : "button",
            "text" : text,
            "action_id" : actionId,
        }

        if(len(value) != 0) : button["value"] = value
        if(confirm != None) : button["confirm"] = confirm
        if(style != "default") : button["style"] = style

        self.elements.append(button)
        return self

    def addSelectMenu(self, placeholder, actionId, options=[], optionGroups=[], initialOption={}, confirm={}) :
        """
        Paramaters
            placeholder - TextObject
            actionId - String
            options - Array Options Object or Options Groups
            options Group - Array options Groups or Options Object 
            initalOption - Options or Options Group Object: A single option that exactly matches one of the options within options or option_groups
            confirm - Confirm Object https://api.slack.com/reference/messaging/composition-objects#confirm
        """
        selectMenu = { }

        if(_isTextObject(placeholder) and (_isOptionsObject(options) or _isOptionsGroupObject(optionsGroup)) and (len(options) > 0  or len(optionGroups) > 0) ) :
            selectMenu = {
                "type" : "static_select",
                "placeholder" : placeholder,
                "action_id" : actionId
            }

            if( len(options) > 0) :
                selectMenu["options"] = options
            elif( len(optionGroups) > 0) :
                selectMenu["option_groups"] = optionGroups
            else :
                return {}

            if(_isOptions(initialOption) or _isOptionGroups(initialOption)) :
                selectMenu["initial_option"] = initialOption

            if(_isConfirmObject(confirm)) :
                selectMenu["confirm"] = confirm

        self.elements.append(selectMenu)
        return self

    def addOverflowMenu(self, actionId, options, confirm={}) :
        """
        Paramaters
            actionId - String
            options - Array Options Object or Options Group
            confirm - confirm https://api.slack.com/reference/messaging/composition-objects#confirm
        """        
        element = {}
        
        if(len(actionId) > 0  and _isOptionsObject(options)) :
            element = {
                "type" : "overflow",
                "action_id" : actionId,
                "options" : options
            }
            if(len(confirm) != 0): element["confirm"] = confirm    

        self.elements.append(element)
        
        return self

    def addDatePicker(self, actionId, placeholder={}, initialDate="", confirm={}) :
        """
        Paramaters
            actionId - String
            placeholder - Text Object
            initial date - String: YYYY-MM-DD
            confirm - Confirm Object
        """     
        datePicker = {}

        if(len(actionId) > 0) :
            datePicker = {
                "type" : "datepicker",
                "action_id" : actionId
            }

            if(_isTextObject(placeholder)) : datePicker["placeholder"] = placeholder
            if(len(initialDate) > 0) : datePicker["initial_date"] = initialDate
            if(confirm.get("title") != None and confirm.get("text") != None and confirm.get("confirm") != None and confirm.get("deny") != None) :
                datePicker["confirm"] = confirm

        self.elements.append(datePicker)

        return self

    def _createOption(self, text, value, plain=True) :
        """
        Paramaters
            text - String
            value - String
        """
        text = _getTextObject(text)

        return {
            "text" : text,
            "value" : value
        }

    def getBlockElements(self) :
        elements = self.elements
        self.elements = []
        return elements

# https://api.slack.com/reference/messaging/composition-objects
class SlackObjects() :        

    def getTextObject(self, text, plain=True, emoji=False, verbatim=False) :
        """
        Parameters:
            text - String: 
            plain - Boolean: True plain text False Slack Markdown
            emoji - Boolean: A value of true for emoji and plain will allow emoji in text object
            verbatim - Boolean: False URL will be auto converted into links, conversation name and mentioned will be linekd
        """

        textObject = { "text" : text }

        if(len(value) > 0 ) : textObject["value"] = value
        if(plain) : textObject["type"] = "plain_text"
        else : textObject["type"] = "mrkdwn"
        if(emoji and plain) : textObject["emoji"] = True
        if(verbatim) : textObject["verbatim"] = True
        
        return textObject

    def getConfirmObject(self, title, text, confirm, deny) :
        """
        Parameters:
            title - TextObject: 100 characters max
            text - TextObject: Option value 300 character max
            confirm - TextObject: Option value 30 character max
            deny - TextObject: Option value 30 character max
        """
        confirmObject = {}

        if(_isTextObject(title) and _isTextObject(text) and _isTextObject(confirm) and _isTextObject(deny) ) :
            confirmObject = {
                "title" : title,
                "text" : text,
                "confirm" : confirm,
                "deny" : deny
            }

        return confirmObject

    def createOptionObject(self, text, value) :
        """
        Parameters:
            text - Text Object: plain text only 75 characters max
            value - String: Option value 75 character max
        """
        option = {}
        if(_isTextObject(text)) :
            option["text"] = text
            option["value"] = value
        return option

    def createOptionGroupObject(self, label, options) :
        """
        Parameters:
            label - Text Object: plain text only 75 characters max
            options - Options Object: Option value 75 character max
        """
        optionGroup = {}
        if(_isTextObject(label) and _isOptionsObject(options)) :
            optionGroup["label"] = label
            optionGroup["options"] = options
        
        return optionGroup


def _isTextObject(obj) :
    if(obj.get("text") != None) : return True
    else : return False

def _isOptionsObject(objs) :
    for obj in objs :
        if(obj.get("text") == None or obj.get("value") == None) :
            return False
    return True

def _isOptions(obj) :
    if(obj.get("text") != None and obj.get("value") != None) :
        return True
    return False

def _isOptionsGroupObject(objs) :
    for obj in objs :
        if(obj.get("label") == None and obj.get("options") == None) : 
            return False
    return True

def _isOptionGroups(obj) :
    if(obj.get("label") != None and obj.get("options") != None) :
        return True
    return False

def _isConfirmObject(obj) :
    if(obj.get("title") and obj.get("text") and obj.get("confirm") and obj.get("deny")) :
        return True
    return False

      
def _getTextObject(text, plain=True, emoji=False, verbatim=False) :
    """
    Parameters:
        text - String: 
        plain - Boolean: plain_text if True mkdwn if False
        emoji - Boolean: enable False
        verbatim -  When set to true will skip any preprocessing of this nature, although you can still include manual parsing strings. This field is only usable when type is mrkdwn
    """

    textObject = { "text" : text }

    if(plain) : textObject["type"] = "plain_text"
    else : textObject["type"] = "mrkdwn"
    if(emoji) : textObject["emoji"] : True
    if(verbatim) : textObject["verbatim"] = True

    return textObject

if __name__ == "__main__":
    pass