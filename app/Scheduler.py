'''
File: Scheduler.py
Description: Responsible for scheduling tasks (Services) within the application
'''

import time, schedule, pymongo, re, datetime
from bson.objectid import ObjectId
from threading import Thread
# FIXME: Collapse into one thing
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
        self.services = financeBot.getServiceHandler().getServices()
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

    # FIXME: Dependency on ServiceHandler
    def addSubscription(self, request) :
        
        job = self.sanitizeRequest(request)
        successful = self.saveJob(job)
        if(successful) :
            successful = self.scheduleJob(job)
        else :
            # TODO: Undo changes
            pass
        return successful

    # FIXME: Dependency on ServiceHandler
    def removeSubscription(self, job) :
        successful = self.unscheduleJob(job)
        if(successful) :
            successful = self.deleteJob(job)
        return successful

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
                self.addUserToSubscription(job)

    # Helper method: Adds a new intra-day schedule job
    def scheduleJob(self, job) :
        
        status = True

        tag = job.get("_id")
        serviceName = job.get("name")
        func = self.financeBot.getServiceHandler().runService

        # Grabs scheduling arguments
        frequency, unit = PERIOD_MAPPER[job.get("submission").get("duration")]
        time = job.get("submission").get("time").strftime("%H:%M")

        if( not self.subscriptionExists(job) ) :
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

        tag = subscription.get("_id")
        
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

        if(True) :
            dbResult = self.collection.insert_one(subscription)
            successful = dbResult.acknowledged
            if(successful) : 
                self.addUserToSubscription(subscription)

        return successful

    # Removes reoccuring job to DB
    def deleteJob(self, job) :

        tag = job.get("_id")
        user = job.get("user")
        serviceName = job.get("name")
        
        if(self.subscriptionExists(job)) :

            # FIXME: Research how to remove subscription
            query = { "_id" :  ObjectId(job.get("_id"))}
            dbStat = self.collection.remove(query)

            if(dbStat['n'] <= 0) : 
                print("ERROR removing document with tag {}.")
                return False
                
            else :
                self.removeUserFromSubscription(job)
                print("Mongdo DB document for tag {} has been properly removed.")
                return True
        else :
            print("Unable to removed tag because it does not exist")
            return False

    # NOTE: request contains new services
    def updateJob(self, subscription) :
        
        user = subscription.get("user")
        serviceName = subscription.get("name")

        query = { "user" : user, "name" : serviceName }

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
    def addUserToSubscription(self, job) :

        userId = job.get("user")
        serviceName = job.get("name")
        subscription = {
            "_id" : str(job.get("_id")),
            "name" : serviceName,
            "description" : job.get("submission").get("description")
        }

        if(self.debug) : logger.debug("Service name: {} userId: {} userSubscriptions: {}".format(serviceName, userId, self.usersSubscriptions))

        if(userId in self.usersSubscriptions) :

            self.usersSubscriptions[userId].append(subscription)
            if(self.debug) : logger.debug("Added additional service Name to {}.".format(userId))
        else :
            self.usersSubscriptions[userId] = []
            if(self.debug) : logger.debug("Adding new userId to usersSubscriptions")
               
            self.usersSubscriptions[userId].append(subscription)
            if(self.debug) : logger.debug("service Name: {} userId: {} added to userSubscriptions: {}".format(serviceName, userId, self.usersSubscriptions))

    # Removes a user to the local user subscription list
    # TODO: Finish remove and Uniquely identifying in Slack
    def removeUserFromSubscription(self, job) :

        userId = job.get("user")
        _id = job.get("_id")
        service = job.get("name")

        if(userId in self.usersSubscriptions) :
            
            for service in self.usersSubscriptions[userId] :
                if(_id in service.get("_id")) :
                    self.usersSubscriptions[userId].remove(service)

            # Removes user from dict if user has no subscriptions
            if(not self.usersSubscriptions[userId]) :
                del self.usersSubscriptions[userId]
        else :
            print("No userId {} exists".format(userId))

    # Determines if there is a user subscription that exists for a given tag
    def subscriptionExists(self, job) :

        userId = job.get("user")
        serviceName = job.get("name")

        if(userId in self.usersSubscriptions) : 
            for subscription in self.usersSubscriptions[userId] :
                if(serviceName in subscription.get("name")) :
                    return True
        else : return False

    def getUsersSubscriptions(self) :
        return self.usersSubscriptions
    
    def getPeriodicity(self) :
        return PEROIDICITY

    def getSubscriptionById(self, user, _id) :

        subscriptions = self.usersSubscriptions.get(user)

        if(subscriptions != None) :
            for subscription in subscriptions :
                if(_id == subscription.get("_id")) :
                    return subscription
        
        return {}

    def getFullSubscriptions(self, user) :
        
        subscriptions = []
        userSubscriptions = self.usersSubscriptions.get(user)

        if(userSubscriptions != None) :
            for userSubscription in userSubscriptions :
                for service in self.services :
                    if(userSubscription.get("name") == service.get("name")) :

                        service["_id"] = userSubscription.get("_id")
                        service["user"] = userSubscription.get("user")
                        subscriptions.append(service)
            return subscriptions

