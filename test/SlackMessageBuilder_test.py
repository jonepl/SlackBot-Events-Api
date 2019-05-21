import pytest, os

import app.SlackMessageBuilder as SlackMessageBuilder

TEST_PATH = os.path.abspath(__file__)
PERIODICITY = ["Testingly", "Hourly", "Daily", "Weekly", "Bi-weekly", "Monthly", "Quarterly", "Semi-annually", "Annually"]

def setup_module(module) :

    global dialog
    global attachments
    global blocks
    global accessory
    global blockElements
    global slackMessageBuilder
    global slackObject
    global actions

    slackMessageBuilder = SlackMessageBuilder.SlackMessageBuilder()
    slackObject = SlackMessageBuilder.SlackObjects()
    blocks = SlackMessageBuilder.Blocks()
    dialog = SlackMessageBuilder.Dialog("title", "callbackId", [])
    blockElements = SlackMessageBuilder.BlockElements()
    accessory = SlackMessageBuilder.Accessory()
    attachments = SlackMessageBuilder.Attachments()
    actions = SlackMessageBuilder.Actions()
    
# Slack Message Class
def test_slackMessage_createServiceDialog():

    expect = {}
    arguments = []
    
    actual = slackMessageBuilder.createServiceDialog("Title", "Callback", "ServiceName", arguments)

    assert(expect == actual)

def test_createServiceDialogComplex_oneArg():

    expect = {'title' : 'title', 'callback_id' : 'callbackId', 'elements' : [{'label': 'Ticker', 'name': 'ticker', 'type': 'text', 'placeholder': 'AAPL'}], 'state': 'ServiceName'}
    arguments = [
        {
            "name" : "Ticker",
            "dataType" : "string",
            "flag" : "t",
            "placeholder" : "AAPL"
        }
    ]
    
    actual = slackMessageBuilder.createServiceDialog("title", "callbackId", "ServiceName", arguments)

    assert(expect == actual)

def test_createServiceDialogComplex_manyArgs():

    expect = {'title': 'Title', 'callback_id': 'Callback', 'elements': [{'label': 'Ticker', 'name': 'ticker', 'type': 'text', 'placeholder': 'AAPL'}, {'label': 'name1', 'name': 'name1', 'type': 'text', 'placeholder': 'placeholder1'}, {'label': 'name2', 'name': 'name2', 'type': 'text', 'placeholder': 'placeholder2'}], 'state': 'ServiceName'}
    arguments = [
        {
            "name" : "name1",
            "dataType" : "string",
            "flag" : "a",
            "placeholder" : "placeholder1"
        },
        {
            "name" : "name2",
            "dataType" : "string",
            "flag" : "b",
            "placeholder" : "placeholder2"
        }
    ]
    
    actual = slackMessageBuilder.createServiceDialog("Title", "Callback", "ServiceName", arguments)

    assert(expect == actual)

# Dialog Tests
def test_dialog_constructor() :
    elements = []
    expected = { "title" : "title", "callback_id" : "callbackId", "elements" : elements}
    actual = dialog.newDialog("title", "callbackId", []).build()

    assert(expected == actual)

def test_dialog_addTextElement() :

    elements = [{ "label" : "label", "name" : "name", "type" : "text"}]
    expected = { "title" : "title", "callback_id" : "callbackId", "elements" : elements, "state" : "state" }
    actual = dialog.newDialog("title", "callbackId", elements=elements, state="state").addTextElement("label", "name", "placeholder").build()

    assert(expected == actual)

def test_dialog_addTextAreaElement() :

    elements = [{ "label" : "label", "name" : "name", "type" : "textarea", "placeholder" : "placeholder", "value" : "value"}]
    expected = { "title" : "title", "callback_id" : "callbackId", "elements" : elements, "state" : "state" }
    actual = dialog.newDialog("title", "callbackId", elements=elements, state="state").addTextAreaElement("label", "name", "placeholder", "value").build()

    assert(expected == actual)

def test_dialog_addSelectElement() :

    options = [ {"label" : "label", "value" : "value"} ]
    elements = [{ "label" : "label", "name" : "name", "type" : "select", "options" : options}]

    expected = { "title" : "title", "callback_id" : "callbackId", "elements" : elements, "state" : "state" }
    actual = dialog.newDialog("title", "callbackId", elements=elements, state="state").addSelectElement("label", "name", "placeholder", "value").build()

    assert(expected == actual)

def test_dialog_addOption():

    expected = [{ "label" : "label", "value" : "value"}]
    actual = dialog.addOption("label", "value").getOptions()

    assert(expected == actual)

def test_dialog_addOptions_Complex():

    expected = [{ "label" : "label", "value" : "value"}, { "label" : "label", "value" : "value"}, { "label" : "label", "value" : "value"}]

    actual = dialog.addOption("label", "value").addOption("label", "value").addOption("label", "value").getOptions()

    assert(expected == actual)

def test_dialog_addOptionGroup() :
    
    options = [{"label" : "label", "value" : "value"}]
    expected = [{ "label" : "label", "options" : options}]

    actual = dialog.addOptionGroups("label", options )

def test_dialog_addOptionGroup_Complex() :
    options = [{"label" : "label", "value" : "value"}, {"label" : "label", "value" : "value"}, {"label" : "label", "value" : "value"}]
    expected = [{ "label" : "label", "options" : options}]

    actual = dialog.addOptionGroups("label", options)

# Actions
def test_actions_addButton() :

    expected = [{ "name" : "name", "text" : "text", "type" : "button" }]
    actual = actions.newActions().addButton("name", "text").build()

    assert(expected == actual)

def test_actions_addButton_Complex() :

    expected = [{ "name" : "name", "text" : "text", "type" : "button", "value" : "value", "style" : "primary", "confirm" : {"confirm" : "confirm"}} ]
    actual = actions.newActions().addButton("name", "text", value="value", style="primary", confirm={"confirm" : "confirm"}).build()

    assert(expected == actual)

def test_actions_addSelect() :
    
    options = { "text": "Hearts", "value": "hearts" }
    expected = [{ "name" : "name", "text" : "text", "type" : "select", "options" : options }]
    actual = actions.newActions().addSelect("name", "text", options).build()

    assert(expected == actual)


def test_actions_getConfirmObject() :
    
    expected = { "title": "Confirm", "text": "Are you sure?", "ok_text" : "Yes", "dismiss_text" : "No" }
    actual = actions.getConfirmObject()

    assert(expected == actual)

def test_actions_getConfirmObject_Complex() :
    
    expected = { "title": "Confirm Transaction", "text": "All transactions are final", "ok_text" : "Confirm", "dismiss_text" : "Cancel" }
    actual = actions.getConfirmObject("Confirm Transaction", "All transactions are final", "Confirm", "Cancel")

    assert(expected == actual)


def test_actions_addSelect() :
    
    expected = { "text": "Hearts", "value": "hearts", "description" : "description"}
    actual = actions.getOptions("Hearts", "hearts", "description")

    assert(expected == actual)

# TODO: Data Source
# def test_actions_addSelect_Complex() :

#     options = { "text": "Hearts", "value": "hearts" }
#     expected = [{ "name" : "name", "text" : "text", "type" : "select", "options" : options }]
#     actual = actions.newActions().addSelect("name", "text", options).build()

#     assert(expected == actual)

# Blocks Tests
def test_blocks_noBlocks():
    
    expected = []
    actual = blocks.getBlocks()
    assert(expected == actual)

def test_blocks_addSectionPlain() :

    textObject = _getTextObject("value")
    expected = [{ "type" : "section", "text" : textObject }]
    actual = blocks.addSection("value").getBlocks()

    assert(expected == actual)

def test_blocks_addSectionMarkDown() :

    textObject = _getTextObject("value", plain=False)
    expected = [{ "type" : "section", "text" : textObject }]
    actual = blocks.addSection("value", plain=False).getBlocks()

    assert(expected == actual)

def test_blocks_addSectionComplex_withFields() :
    
    textObject1 = _getTextObject("value1", plain=True)
    textObject2 = _getTextObject("value2", plain=False)
    textObject3 = _getTextObject("value3", plain=True)
    accessory = { "type" : "image", "image_url" : "imageUrl", "alt_text" : "altText" }

    expected = [{ "type" : "section", "text" : textObject1, "fields" : [textObject2, textObject3], "accessory" : accessory}]
    actual = blocks.addSection("value1", plain=True, fields=[textObject2, textObject3], accessory=accessory).getBlocks()

    assert(expected == actual)

def test_blocks_addSectionComplex_All() :
    pass

def test_blocks_addDivider() :
    
    expected = [{ "type": "divider" }]
    actual = blocks.addDivider().getBlocks()
    assert(expected == actual)

def test_blocks_addDividerComplex_withBlockId() :
    
    expected = [{ "type": "divider", "block_id": "blockId" }]
    actual = blocks.addDivider(blockId="blockId").getBlocks()
    assert(expected == actual)

def test_blocks_addImage() :
    
    expected = [ { "type" : "image", "image_url" : "imageUrl", "alt_text": "altText" }]
    actual = blocks.addImage("imageUrl", "altText").getBlocks()
    assert(expected == actual)

def test_blocks_addImage_titleAndBlockId() :
    
    expected = [ { "type" : "image", "image_url" : "imageUrl", "alt_text": "altText", "title" : "title", "block_id" : "blockId",  }]
    actual = blocks.addImage("imageUrl", "altText", title="title", blockId="blockId").getBlocks()
    assert(expected == actual)

def test_blocks_addAction() :
    elements = [_getButtonBlockElement(), _getImageBlockElement()]
    expected = [ { "type" : "actions", "elements" : elements, "block_id" : "blockId" } ]
    actual = blocks.addAction(elements, blockId="blockId").getBlocks()

    assert(expected == actual)

def test_blocks_addContext() :
    
    elements = [_getTextObject("textObject"), _getImageBlockElement() ]
    expected = [{ "type" : "context", "elements" : elements }]
    actual = blocks.addContext(elements).getBlocks()

    assert(expected == actual)

def test_blocks_addContextComplex():

    elements = [_getTextObject("textObject"), _getImageBlockElement()]
    expected = [{ "type" : "context", "elements" : elements, "block_id" : "blockId" }]
    actual = blocks.addContext(elements, blockId="blockId").getBlocks()

    assert(expected == actual)

# Block Elements Test
def test_blockElements_addImage():

    expected = [ { "type" :  "image", "image_url" : "imageUrl", "alt_text" : "altText"} ]
    actual = blockElements.addImage("imageUrl", "altText").getBlockElements()

    assert(expected == actual)

def test_blockElements_addImageComplex():

    expected = [ { "type" :  "image", "image_url" : "imageUrl", "alt_text" : "altText", "block_id" : "blockId"} ]
    actual = blockElements.addImage("imageUrl", "altText", blockId="blockId").getBlockElements()

    assert(expected == actual)

def test_blockElements_addButton():
    
    expected = [ {"type" : "button", "text" : _getTextObject("text"), "action_id" : "actionId"}]
    actual = blockElements.addButton("text", "actionId").getBlockElements()

    assert(expected == actual)

def test_blockElements_addButtonComplex():
    
    expected = [ {"type" : "button", "text" : _getTextObject("text", plain=False), "action_id" : "actionId", "value" : "value", "confirm" : "confirm"}]
    actual = blockElements.addButton("text", "actionId", plain=False, value="value", confirm="confirm").getBlockElements()

    assert(expected == actual)

def test_blockElements_addSelectMenu():
    
    placeholder = _getTextObject("placeholder")
    options = _getOptionObject()
    expected = [ {"type" : "static_select", "placeholder" : placeholder, "action_id" : "actionId", "options" : options}]
    actual = blockElements.addSelectMenu(placeholder, "actionId", options=options).getBlockElements()

    assert(expected == actual)

def test_blockElements_addSelectMenuComplex_options():
    
    placeholder = _getTextObject("placeholder")
    options = _getOptionObject()
    initialOptions = _getOption(text="text", value="initialOption")
    confirm = _getConfirmObject()

    expected = [ {"type" : "static_select", "placeholder" : placeholder, "action_id" : "actionId", "options" : options, "initial_option" : initialOptions, "confirm" : confirm}]
    actual = blockElements.addSelectMenu(placeholder, "actionId", options=options, initialOption=initialOptions, confirm=confirm).getBlockElements()

def test_blockElements_addSelectMenuComplex_optionGroups():
    
    placeholder = _getTextObject("placeholder")
    optionGroups = _getOptionGroupObject()
    initialOptions = _getOption(text="text", value="initialOption")
    confirm = _getConfirmObject()

    expected = [ {"type" : "static_select", "placeholder" : placeholder, "action_id" : "actionId", "option_group" : optionGroups, "initial_option" : initialOptions, "confirm" : confirm}]
    actual = blockElements.addSelectMenu(placeholder, "actionId", optionGroups=optionGroups, initialOption=initialOptions, confirm=confirm).getBlockElements()

def test_blockElements_addSelectMenuComplex_optionAndoptionGroups():
    
    placeholder = _getTextObject("placeholder")
    options = _getOptionObject()
    optionGroups = _getOptionGroupObject()
    initialOptions = _getOption(text="text", value="initialOption")
    confirm = _getConfirmObject()

    expected = [ {"type" : "static_select", "placeholder" : placeholder, "action_id" : "actionId", "options" : options, "initial_option" : initialOptions, "confirm" : confirm}]
    actual = blockElements.addSelectMenu(placeholder, "actionId", optionGroups=optionGroups, initialOption=initialOptions, confirm=confirm).getBlockElements()

def test_blockElements_addOverflowMenu():
    
    options = _getOptionObject()
    expected = [ {"type" : "overflow", "action_id": "actionId", "options" : options} ]
    actual = blockElements.addOverflowMenu("actionId", options).getBlockElements()
    assert(expected == actual)

def test_blockElements_addOverflowMenuComplex():
    
    options = _getOptionObject()
    expected = [ {"type" : "overflow", "action_id": "actionId", "options" : options} ]
    actual = blockElements.addOverflowMenu("actionId", options).getBlockElements()
    assert(expected == actual)   

def test_blockElements_addDatePicker():
    
    expected = [ { "type" : "datepicker", "action_id" : "actionId"} ]
    actual = blockElements.addDatePicker("actionId").getBlockElements()

    assert(expected == actual)

def test_blockElements_addDatePickerComplex():
    
    placeholder = _getTextObject("placeholder")
    initialDate = "2019-04-21"
    expected = [ { "type" : "datepicker", "action_id" : "actionId", "placeholder" : placeholder, "initial_date" : initialDate} ]
    actual = blockElements.addDatePicker("actionId", placeholder=placeholder, initialDate=initialDate).getBlockElements()

    assert(expected == actual)

# Attachments
def test_attachments() :
    actions = [{ "name" : "name", "text" : "text", "type" : "button" }]
    authorIcon="authorIcon"
    authorLink="authorLink"
    authorName="authorName"
    blocks=[{ "type" : "section", "text" : "text", "accessory" : []}]
    callbackId = "callbackId"
    color = "color"
    fallback="fallback"
    fields=[{ "title" : "title", "value" : "value", "short" : True }]
    footer="footer"
    footerIcon="footerIcon"
    imageUrl="imageUrl"
    mrkdwnIn="mrkdwnIn"
    pretext="pretext"
    text="text"
    thumbUrl="thumbUrl"
    title="title"
    titleLink="titleLink"
    ts=124134221

    expected = [{ 
        "actions" : actions,
        "author_icon" : authorIcon, 
        "author_name" : authorName, 
        "blocks" : blocks, 
        "callback_id" : callbackId,
        "color" : color,
        "fallback" : fallback, 
        "fields" : fields, 
        "footer" : footer, 
        "footer_icon" : footerIcon, 
        "image_url" : imageUrl, 
        "mrkdwn_in" : mrkdwnIn, 
        "pretext" : pretext, 
        "text" : text, 
        "thumb_url" : thumbUrl, 
        "title" : title, 
        "title_link" : titleLink, 
         "ts" : ts 
    }]

    actual = attachments.addAttachment(actions, authorIcon, authorLink, authorName, blocks, callbackId, color, fallback, fields, footer, footerIcon, imageUrl, mrkdwnIn, pretext, text, thumbUrl, title, titleLink,  ts).build()

    assert(expected == actual)

# Accessory Class
def test_accessory_createImage() :
    expected = { "type" : "image", "image_url" : "imageUrl", "alt_text": "altText" }
    actual = accessory.createImage("imageUrl", "altText")
    assert(expected == actual)

def test_accessory_createButton() :
    expected = {"type" : "button", "text" : _getTextObject("text"), "action_id" : "actionId"}
    actual = accessory.createButton("text", "actionId")
    assert(expected == actual)

def test_accessory_createSelect() :
    placeholder = _getTextObject("placeholder")
    options = _getOptionObject()
    expected = {"type" : "static_select", "placeholder" : placeholder, "action_id" : "actionId", "options" : options}
    actual = accessory.createSelectMenu(placeholder, "actionId", options=options)

    assert(expected == actual)

def test_accessory_createOverflowMenu() :
    options = _getOptionObject()
    expected = {"type" : "overflow", "action_id": "actionId", "options" : options}
    actual = accessory.createOverflowMenu("actionId", options)
    assert(expected == actual)

def test_accessory_createDatePicker() :
    expected = { "type" : "datepicker", "action_id" : "actionId"}
    actual = accessory.createDatePicker("actionId")
    assert(expected == actual)

# Helper Functions
def _getDialog(title, callbackId, elements=[], state="", submitLabel="Request", notifyOnCancel=False) :
    return {
        "title" : title,
        "callback_id" : callbackId,
        "elements" : elements,
        "state" : state,
        "submit_label" : submitLabel,
        "notify_on_cancel" : notifyOnCancel
    }

def _getTextObject(text, plain=True) :
    textObject = {
        "text" : text,
    }

    if(plain) : textObject["type"] = "plain_text"
    else : textObject["type"] = "mrkdwn"

    return textObject

def _getImageBlockElement() :
    return {
        "type": "image",
        "image_url": "imageUrl",
        "alt_text": "altText"
    }

def _getButtonBlockElement() :
    return {
        "type": "button",
        "text": { "text" : "text", "type":  "plain_text" } ,
        "action_id": "actionId",
    }   

def _getSelectBlockElement() :
    return {
        "type": "static_select",
        "placeholder": "placeholder",
        "action_id": "actionId",
        "options": [{ "text": { "text" : "text", "type":  "plain_text" } , "value": "value"} ]
    }

def _getOption(text="text", value="value") :
    return { "text": { "text" : text, "type":  "plain_text" } , "value": value}

def _getOptionObject(text="text", value="value") :
    return [{ "text": { "text" : text, "type":  "plain_text" } , "value": value} ]

def _getOptionGroupObject(label="label", options = { "text" : _getTextObject("text"), "value" : "value" }) :
    return [ { "label" : label, "options" : options }]

def _getConfirmObject(title=_getTextObject("title"), text=_getTextObject("text"), confirm=_getTextObject("confirm"), deny=_getTextObject("deny")) :
    return { "title" : title, "text" : text, "confirm" : confirm, "deny" : deny }