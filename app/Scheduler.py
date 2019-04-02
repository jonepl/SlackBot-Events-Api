'''
File: Scheduler.py
Description: Responsible for scheduling tasks (Services) within the application
'''

import time, schedule, pymongo, re, datetime

from threading import Thread

PEROIDICITY = ["Testingly", "Hourly", "Daily", "Weekly", "Bi-weekly", "Monthly", "Quarterly", "Semi-annually", "Annually"]
PERIOD_MAPPER = {
        "Testingly" :("second", 20),
        "Hourly" : ("hour", 1),
        "Daily" : ('day', 1),
        "Bi-weekly" : ('weeks', 2),
        "Weekly" : ('weeks', 1),
        "Monthly" : ('weeks', 4),
        "Quarterly" : ('weeks', 13),
        "Semi-annually" : ("weeks", 26),
        "Annually" : ('weeks', 52),
    }

class Scheduler(Thread) :
    
    def __init__(self, financeBot=None, config=None, debug=False) :

        Thread.__init__(self)
        client = pymongo.MongoClient( config['mongoDB']['uri'] )
        db = client[ config['mongoDB']['dbName'] ]
        self.running = True
        self.collection = db[ config['mongoDB']['collectionName'] ]       
        self.debug = debug
        self.financeBot = financeBot
        self.pending = {}
        self.usersSubscriptions = {}

    def run(self) :

        self.loadScheduledJobs()

        while(self.running) :
            try:

                schedule.run_pending()
                time.sleep(0.5)
            except(KeyboardInterrupt, SystemError) :
                self.running = False

    def addSubscription(self, request) :
        job = self.sanitizeRequest(request)
        successful = self.scheduleJob(job)
        if(successful) :
            successful = self.saveJob(job)
        return successful

    def removeSubscription(self, request) :
        print("Implement removal of subscription will multiple service names")

    def sanitizeRequest(self, request) :
        request["submission"]["time"] = self.convertTime(request.get("submission").get("time"))
        return request
    
    def convertTime(self, time):
        afternoon = False
        time = time.replace(".", "")

        obj = re.search(r"((1[0-2]|0?[1-9])((:([0-5][0-9]))?([AaPp][Mm])?)?)", time)
        if(obj != None) :
            timeStr = obj.group().lower()
            if("pm" in timeStr) :
                timeStr = timeStr.replace("pm","")
                afternoon = True
            elif("am" in timeStr) :
                timeStr = timeStr.replace("am","")


            if(":" in timeStr) :
                hr, minute = timeStr.split(":")
            else :
                hr = timeStr
                minute = 0

            if(afternoon) :
                now = datetime.datetime.now()
                return datetime.datetime(now.year, now.month, now.day, (int(hr) + 12)%24, int(minute))
                #return datetime.combine(date.today(), datetime.time((int(hr) + 12)%24, int(minute)))
            else :
                now = datetime.datetime.now()
                return datetime.datetime(now.year, now.month, now.day, int(hr), int(minute))
                #return datetime.combine(date.today(), datetime.time(int(hr),int(minute)))
        else :
            return None

    # Loads all jobs from DB into scheduler
    def loadScheduledJobs(self):

        jobs = self.collection.find( {} )
        if(self.debug) : logger.debug("Found {} logs in db".format(str(jobs)))
        for job in jobs :
            successful = self.scheduleJob(job)
            if(successful) : 
                self.addUserToSubscription(self.produceTag(job))

    # Helper method: Adds a new intra-day schedule job
    def scheduleJob(self, job) :
        
        status = True
        tag = self.produceTag(job)
        serviceName = job.get('serviceName')
        func = self.financeBot.getServiceHandler().runService

        # Grabs scheduling arguments
        frequency, unit = PERIOD_MAPPER[job.get("submission").get("duration")]
        time = job.get("submission").get("time").strftime("%H:%M")

        if( not self.subscriptionExists(tag) ) :
            args = job

            # NOTE: When would args be None?
            if( args is not None ) :
                #TODO: remove set value from messagehandler and determine serivceName within this file

                if ("second" in frequency) :
                    schedule.every(unit).seconds.do(func, args).tag(tag)

                elif ("hour" in frequency) :
                    schedule.every(unit).hours.at(time).do(func, args).tag(tag)

                elif ("day" in frequency or "dai" in frequency) :
                    schedule.every(unit).days.at(time).do(func, args).tag(tag)

                elif ("week" in frequency) :
                    schedule.every(unit).weeks.at(time).do(func, args).tag(tag)

                else :
                    print("ERROR OCCURRED")
                    status = False
            else :
                print("Error Occurred while searching for ServiceDetails")
                status = False

        return status

    # Removes schedule jobs from schedule
    def unscheduleJob(self, subscription) :

        status = True

        if(self.debug) : logger.debug("Unscheduling Job ...")

        tag = self.produceTag(subscription)
        
        # : Figure out if a status can be evaluated
        schedule.clear(tag)

        return status

    # Unschedules a list of users from scheduler
    def unscheduledJobByTag(self, userIds, service) :

        for userId in userIds :
            tag = userId + "_" + service
            # FIXME: Status of removal?
            schedule.clear(tag)

    # Adds to reoccuring job to DB
    def saveJob(self, subscription):
        #FIXME: Use Mongo Schema to prevent ulgy jobs entrying db
        successful = False
        user = subscription.get("user")
        service = subscription.get("service")
        tag = self.produceTag(subscription)

        if(True) :
            dbResult = self.collection.insert_one(subscription)
            successful = dbResult.acknowledged
            if(successful) : 
                self.addUserToSubscription(self.produceTag(subscription))
        else :
            print("User id {} is already subscribed to service {}".format(user, service))
            successful = False

        return successful

    # Removes reoccuring job to DB
    def deleteJob(self, subscription) :

        tag = self.produceTag(subscription)
        user = subscription.get("user")
        serviceName = subscription.get("serviceName")
        
        if(self.subscriptionExists(tag)) :

            # FIXME: Research how to remove subscription
            query = { "serviceName" :  serviceName, "user" : user }
            dbStat = self.collection.remove(query)

            if(dbStat['n'] <= 0) : 
                print("ERROR removing document with tag {}.")
                return False
                
            else :
                self.removeUserFromSubscription(self.produceTag(subscription))
                print("Mongdo DB document for tag {} has been properly removed.")
                return True
        else :
            print("Unable to removed tag because it does not exist")
            return False

    # NOTE: request contains new services
    def updateJob(self, subscription) :
        
        user = subscription.get("user")
        service = subscription.get("serviceName")

        query = { "user" : user, "serviceName" : service }

        update = { "$set": { 
            "frequency": subscription.get('frequency'),
            "time": subscription.get('time'),
            "unit": subscription.get('unit'),
            }
        }

        result = self.collection.find_one_and_update(query, update)

        if(result is None) : return False
        else : return True

    def addPending(self, user, serviceName) :
        status = False
        if(self.pending.get(user) == None) :
            if(serviceName not in self.pending[user]) :
                self.pending[user] = serviceName
                status = True
        
        return status

    # Adds a user to the local user subscription list
    def addUserToSubscription(self, tag) :

        userId, service = tag.split("_")

        if(self.debug) : logger.debug("service: {} userId: {} userSubscriptions: {}".format(service, userId, self.usersSubscriptions))

        if(userId in self.usersSubscriptions) :

            self.usersSubscriptions[userId].append(service)
            if(self.debug) : logger.debug("Added additional service to {}.".format(userId))
        else :
            self.usersSubscriptions[userId] = []
            if(self.debug) : logger.debug("Adding new userId to usersSubscriptions")
               
            self.usersSubscriptions[userId].append(service)
            if(self.debug) : logger.debug("Service: {} userId: {} added to userSubscriptions: {}".format(service, userId, self.usersSubscriptions))

    # Removes a user to the local user subscription list
    def removeUserFromSubscription(self, tag) :

        userId, service = tag.split("_")

        if(userId in self.usersSubscriptions) :
            
            if(service in self.usersSubscriptions[userId]) :
                self.usersSubscriptions[userId].remove(service)
            else :
                print("Tag {} does not exits. Can't remove".format(tag))

            if(not self.usersSubscriptions[userId]) :
                del self.usersSubscriptions[userId]
        else :
            print("No userId {} exists".format(userId))

    # Produces an job identifier
    def produceTag(self, subscription) :
        return subscription.get('user') + "_" + subscription.get('serviceName')

    # Determines if there is a user subscription that exists for a given tag
    def subscriptionExists(self, tag) :

        userId, service = tag.split("_")

        if(userId in self.usersSubscriptions) : 
            if(service in self.usersSubscriptions[userId]) :
                return True
        else : return False

    def getUsersSubscriptions(self) :
        return self.usersSubscriptions
    
    def getPeriodicity(self) :
        return PEROIDICITY