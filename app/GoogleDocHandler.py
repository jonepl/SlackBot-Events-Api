class GoogleDocHandler(Thread) :

    _instance = None

    def __init__(self, financeBot=None, config=None, debug=False) :
        Thread.__init__(self)
        self.financeBot = financeBot
        self.services = SERVICES
        self.serviceNames = self.getServicesNames(self)
        self.runnableServices = _initRunnableServices(self.serviceNames)

    
    def run(self) :
        self.running = True
        # TODO: Figure out multi-threaded solution
        while(self.running) :
            try :
                if(self.financeBot.getGoogleDocHandlerQueue().qsize() > 0) : 

                    message = self.financeBot.getGoogleDocHandlerQueue().get()
                    self.financeBot.getGoogleDocHandlerQueue().task_done()
                    if(self.debug) : logger.debug("Message requested received from Bot {}".format(str(message)))
                    self.handleService(message)

                time.sleep(0.5)

            except(KeyboardInterrupt, SystemError) :
                if(self.debug) : logger.debug("\n~~~~~~~~~~~ MessageHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n")
                self.subscriptionHandler.kill()
                self.running = False
    
    def handleService(self, message) :
        pass