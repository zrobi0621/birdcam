from flask import Flask, render_template, request, redirect, url_for, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from os import path
import os.path
import time
import subprocess
import atexit
import csv
import json

# Hardware
import Adafruit_DHT
from gpiozero import CPUTemperature
from gpiozero import LightSensor

# E-mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = Flask(__name__)

dateTimeNow = ""

isLiveCamActive = False
isMotionDetectingActive = False
canDetectMotionTime = False
canDetectMotionLDR = False

#   HARDWARE
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 17                                # can be modified - DHT Sensor's PIN
LDR_PIN = 18                                # can be modified - LDR Sensor's PIN
ldr = LightSensor(LDR_PIN)          
cpu = CPUTemperature()

#   SETTINGS    - DEFAULT values
isEmailSendingActive = True
emailTo1 = "null"
emailTo2 = "null"
emailTo3 = "null"
isDetectionWithTimeActive = True
isDetectionWithLDR = False
detectionTimeFrom = 6
detectionTimeTo = 18
detectionLDRFrom = 0.6
detectionLDRTo = 1.0
maxDailyEmail = 5
timeBetweenEmails = 15      # in sec

dailyEmailCounter = 0

#   WEBSITE USAGE TIMER
isWebsiteTimerActive = False
websiteTimerMax = 30        # in sec
websiteTimer = 30           # in sec

#   APP USAGE TIMER
isAppTimerActive = False
appTimerMax = 30            # in sec
appTimer = 30               # in sec


################### Scheduler - Hourly task ###################

measurementCounter = 0

dailyMinTemp = 200.0
dailyMaxTemp = -200.0
dailyMinHumidity = 200.0
dailyMaxHumidity = -200.0

class MData(dict):
    def __init__(self, datetime, minTemp, maxTemp, minHumidity, maxHumidity):
        dict.__init__(self, datetime=datetime, minTemp=minTemp, maxTemp=maxTemp,
                      minHumidity=minHumidity, maxHumidity=maxHumidity)

def hourly_measurement():
    global dailyMinTemp
    global dailyMaxTemp
    global dailyMinHumidity
    global dailyMaxHumidity    

    dateTimeNow = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")

    measurementCounter = datetime.now().strftime("%H")

    # DEBUG
    #print(dateTimeNow)
    #print(measurementCounter)
    # DEBUG

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    humidity = '{:.2f}'.format(humidity)
    temperature = '{:.2f}'.format(temperature)

    if(float(humidity) < 100 and float(humidity) > 0):
        if(float(temperature) <= dailyMinTemp and float(temperature) < 100 and float(temperature) > -100):
            dailyMinTemp = float(temperature)
        if(float(temperature) >= dailyMaxTemp and float(temperature) < 100 and float(temperature) > -100):
            dailyMaxTemp = float(temperature)
        if(float(humidity) <= dailyMinHumidity and float(humidity) < 100 and float(humidity) > -100):
            dailyMinHumidity = float(humidity)
        if(float(humidity) >= dailyMaxHumidity and float(humidity) < 100 and float(humidity) > -100):
            dailyMaxHumidity = float(humidity)

    # DEBUG
    """ print(f"Current Temp: {temperature}°C, Humidity: {humidity}%")
    print(f"    MinTemp: {dailyMinTemp}°C")
    print(f"    MaxTemp {dailyMaxTemp}°C")
    print(f"    MinHum: {dailyMinHumidity}%")
    print(f"    MaxHum: {dailyMaxHumidity}%") """
    # DEBUG

    if(int(measurementCounter) == 23):
        if(path.exists('measurementsDaily.csv')):
            with open('measurementsDaily.csv', mode='a') as measurementsDaily_file:
                measurementsDaily_writer = csv.writer(
                    measurementsDaily_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                measurementsDaily_writer.writerow(
                    [dateTimeNow, dailyMinTemp, dailyMaxTemp, dailyMinHumidity, dailyMaxHumidity])

                dailyMinTemp = 200
                dailyMaxTemp = -200
                dailyMinHumidity = 200
                dailyMaxHumidity = -200                

                # DEBUG
                #print("...  resetDefaultValues    ...")
                # DEBUG
        else:
            with open('measurementsDaily.csv', mode='a') as measurementsDaily_file:
                measurementsDaily_writer = csv.writer(
                    measurementsDaily_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # Layout of the .csv file
                measurementsDaily_writer.writerow(
                    ['date', 'minTemp', 'maxTemp', 'minHumidity', 'maxHumidity'])

#### Scheduler ####
scheduler = BackgroundScheduler()
#   Change interval: seconds, minutes, hours #
scheduler.add_job(func=hourly_measurement, trigger="interval", minutes=60, misfire_grace_time=3600)
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
#### Scheduler ####

def startLiveCamStreaming():
    global isLiveCamActive
    
    isLiveCamActive = True
    print("  ### LiveCam: Camera streaming started")
    os.system("python3 liveCam.py")
    
def stopLiveCamStreaming():
    global isLiveCamActive

    isLiveCamActive = False    
    print("  ### LiveCam: Camera streaming stopped")    
    os.system('pkill -f liveCam.py')  

    startMotionDetection()

def startMotionDetection():
    global isMotionDetectingActive
    global isLiveCamActive
    global canDetectMotionTime
    global canDetectMotionLDR
    global dailyEmailCounter
    global maxDailyEmail

    # For command line arguments
    global isEmailSendingActive
    global emailTo1
    global emailTo2
    global emailTo3
    global isDetectionWithTimeActive
    global isDetectionWithLDR
    global detectionTimeFrom
    global detectionTimeTo
    global maxDailyEmail
    global timeBetweenEmails

    if isLiveCamActive == False:
        if dailyEmailCounter != maxDailyEmail:
            if isMotionDetectingActive == False:                

                if isEmailSendingActive == True:    
                    if isDetectionWithTimeActive == True:
                        if canDetectMotionTime == True:
                            isMotionDetectingActive = True
                            print("  ### PIR: Motion detection started - With Time")            
                            os.system(f"python3 sendEmail.py {isEmailSendingActive} {emailTo1} {emailTo2} {emailTo3} {timeBetweenEmails}")
                    elif isDetectionWithLDR == True:
                        if canDetectMotionLDR == True:    
                            isMotionDetectingActive = True                
                            print("  ### PIR: Motion detection started - With LDR")            
                            os.system(f"python3 sendEmail.py {isEmailSendingActive} {emailTo1} {emailTo2} {emailTo3} {timeBetweenEmails}")

def motionDetectionWithTime():    
    global canDetectMotionTime
    global isMotionDetectingActive
    global isDetectionWithTimeActive
    global detectionTimeFrom
    global detectionTimeTo    
            
    timeNowHour = datetime.now().strftime("%H")                

    if isDetectionWithTimeActive == True:
        if int(timeNowHour) >= int(detectionTimeFrom):
            if int(timeNowHour) < int(detectionTimeTo):                            
                canDetectMotionTime = True
                if isMotionDetectingActive == False:                                
                    startMotionDetection()
            else:                                    
                canDetectMotionTime = False
                if isMotionDetectingActive == True:                     
                    stopMotionDetection()        

def motionDetectionWithLDR():    
    global canDetectMotionLDR  
    global isMotionDetectingActive
    global isDetectionWithLDR
    global detectionLDRFrom
    global detectionLDRTo    
                           
    #print("     ## Debug: " + str(ldr.value) + " Min: " + str(detectionLDRFrom) + " Max: " + str(detectionLDRTo))

    if isDetectionWithLDR == True:
        if detectionLDRTo >= ldr.value:
            if detectionLDRFrom <= ldr.value:                
                canDetectMotionLDR = True
                if isMotionDetectingActive == False:
                    startMotionDetection()
            else:                
                canDetectMotionLDR = False
                if isMotionDetectingActive == True:
                    stopMotionDetection()    

def dailyEmailCounterResetter():
    global dailyEmailCounter
          
    timeNowHour = datetime.now().strftime("%H")
    
    if timeNowHour == "00":
        dailyEmailCounter = 0        
        print("  ### EMAIL: Daily Email Counter reseted")             

def stopMotionDetection():
    global isMotionDetectingActive
    
    if isMotionDetectingActive == True:
        isMotionDetectingActive = False
        print("  ### PIR: Motion detection stopped")
        os.system('pkill -f sendEmail.py')                

### Website timer - to check someone is using the website
def setWebsiteTimer():
    global websiteTimer    
    websiteTimer = websiteTimerMax

def startWebsiteTimer():
    global websiteTimer
    global isWebsiteTimerActive        

    if isWebsiteTimerActive == False:
        isWebsiteTimerActive = True

        print(f"  ### WebsiteTimer: Started")
        while websiteTimer != 0:
            time.sleep(1)
            websiteTimer = websiteTimer - 1            

        isWebsiteTimerActive = False
        print(f"  ### WebsiteTimer: Stopped")
        stopLiveCamStreaming()

### App timer - to check someone is using the App
def setAppTimer():
    global appTimer    
    appTimer = appTimerMax    

def startAppTimer():
    global appTimer
    global isAppTimerActive        

    if isAppTimerActive == False:
        isAppTimerActive = True

        print(f"  ### AppTimer: Started")
        while appTimer != 0:
            time.sleep(1)
            appTimer = appTimer - 1            

        isAppTimerActive = False
        print(f"  ### AppTimer: Stopped")
        stopLiveCamStreaming()
            
scheduler2 = BackgroundScheduler()
scheduler2.start()      

# Start motion detection at start
if isEmailSendingActive == True:    
    scheduler2.add_job(motionDetectionWithTime, 'interval', minutes=1, replace_existing=True, max_instances=5, misfire_grace_time=3600) 
    scheduler2.add_job(motionDetectionWithLDR, 'interval', minutes=1, replace_existing=True, max_instances=5, misfire_grace_time=3600)        

# Resets the Daily Email Counter at midnight
scheduler2.add_job(dailyEmailCounterResetter, 'cron', hour=0, minute=0)
    
############################   FLASK SERVER   ############################

#### Website - Main Page ####
@ app.route('/')
def index():
    global isLiveCamActive
    global isMotionDetectingActive
    isLiveCamActive = False

    scheduler2.add_job(func=setWebsiteTimer, misfire_grace_time=3600)     
        
    if isLiveCamActive == False:                   
        scheduler2.add_job(func=stopMotionDetection, misfire_grace_time=3600)        
        scheduler2.add_job(func=setWebsiteTimer, misfire_grace_time=3600) 

        if isWebsiteTimerActive == False:            
            scheduler2.add_job(func=startLiveCamStreaming, misfire_grace_time=3600)
            scheduler2.add_job(func=startWebsiteTimer, misfire_grace_time=3600)             
                                         
    dateTimeNow = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    humidity = '{:.2f}'.format(humidity)
    temperature = '{:.2f}'.format(temperature)    
        
    return render_template('index.html', cpu=cpu, ldr=ldr, dateTimeNow=dateTimeNow, humidity=humidity, temperature=temperature)

#### APP - Main Page - For live data in Json format ####
@ app.route('/data', methods=['GET'])
def data():
    global isLiveCamActive    

    scheduler2.add_job(func=setAppTimer, misfire_grace_time=3600)     
        
    if isLiveCamActive == False:                   
        scheduler2.add_job(func=stopMotionDetection, misfire_grace_time=3600)        
        scheduler2.add_job(func=setAppTimer, misfire_grace_time=3600) 

        if isAppTimerActive == False:            
            scheduler2.add_job(func=startLiveCamStreaming, misfire_grace_time=3600)
            scheduler2.add_job(func=startAppTimer, misfire_grace_time=3600)
         
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    humidity = '{:.2f}'.format(humidity)
    temperature = '{:.2f}'.format(temperature)
    return jsonify({'cputemp': str(cpu.temperature),
                    'ldr': str(ldr.value),
                    'humidity': humidity,
                    'temperature': temperature})

#### APP - Measurements Page - The previous measurements on Measurements Page in Json format ####
@ app.route('/measurements', methods=['GET'])
def measurements():

    scheduler2.add_job(func=setAppTimer, misfire_grace_time=3600)

    if(path.exists('measurementsDaily.csv')):
        with open('measurementsDaily.csv', newline='') as f:
            reader = csv.reader(f)
            dataFromCsv = list(reader)

        dataToSend = []
        split = []
        dataFromCsv.pop(0)

        for item in dataFromCsv:            
            dataToSend.append(MData(
                item[0], item[1], item[2], item[3], item[4]))
        
        return json.dumps(dataToSend)

#### APP - Settings Page - To get the settings in Json format ####
@ app.route('/settings', methods=['GET'])
def settingsGet():        
    global isEmailSendingActive
    global emailTo1
    global emailTo2
    global emailTo3
    global isDetectionWithTimeActive
    global isDetectionWithLDR
    global detectionTimeFrom
    global detectionTimeTo
    global detectionLDRFrom
    global detectionLDRTo
    global maxDailyEmail
    global timeBetweenEmails

    scheduler2.add_job(func=setAppTimer, misfire_grace_time=3600)    

    print(f"    GET : {isEmailSendingActive}, {emailTo1}, {emailTo2}, {emailTo3}, {isDetectionWithTimeActive}, {isDetectionWithLDR}, {detectionTimeFrom}, {detectionTimeTo}, {detectionLDRFrom}, {detectionLDRTo}, {maxDailyEmail}, {timeBetweenEmails}")
    return jsonify({'isEmailSendingActive': isEmailSendingActive, 'emailTo1': emailTo1, 'emailTo2': emailTo2, 'emailTo3': emailTo3, 'isDetectionWithTimeActive': isDetectionWithTimeActive, 'isDetectionWithLDR': isDetectionWithLDR, 'detectionTimeFrom': detectionTimeFrom, 'detectionTimeTo': detectionTimeTo, 'detectionLDRFrom': detectionLDRFrom, 'detectionLDRTo':detectionLDRTo, 'maxDailyEmail': maxDailyEmail, 'timeBetweenEmails':timeBetweenEmails
    })

#### APP - Settings Page - To modify the settings ####
@ app.route('/settings', methods=['POST'])
def settingsPost():    
    global isEmailSendingActive
    global emailTo1
    global emailTo2
    global emailTo3
    global isDetectionWithTimeActive
    global isDetectionWithLDR
    global detectionTimeFrom
    global detectionTimeTo
    global detectionLDRFrom
    global detectionLDRTo
    global maxDailyEmail
    global timeBetweenEmails    

    data = request.get_json()

    isEmailSendingActive = data['isEmailSendingActive']
    emailTo1 = data['emailTo1']
    emailTo2 = data['emailTo2']
    emailTo3 = data['emailTo3']
    isDetectionWithTimeActive = data['isDetectionWithTimeActive']
    isDetectionWithLDR = data['isDetectionWithLDR']
    detectionTimeFrom = data['detectionTimeFrom']
    detectionTimeTo = data['detectionTimeTo']
    detectionLDRFrom = data['detectionLDRFrom']
    detectionLDRTo = data['detectionLDRTo']
    maxDailyEmail = data['maxDailyEmail']
    timeBetweenEmails = data['timeBetweenEmails']

    if emailTo1 == "":
        emailTo1 = "null"
    if emailTo2 == "":
        emailTo2 = "null"
    if emailTo3 == "":
        emailTo3 = "null"

    print(f"    POST : {isEmailSendingActive}, {emailTo1}, {emailTo2}, {emailTo3}, {isDetectionWithTimeActive}, {isDetectionWithLDR}, {detectionTimeFrom}, {detectionTimeTo}, {detectionLDRFrom}, {detectionLDRTo}, {maxDailyEmail}, {timeBetweenEmails}")
    return jsonify({'isEmailSendingActive': isEmailSendingActive, 'emailTo1': emailTo1, 'emailTo2': emailTo2, 'emailTo3': emailTo3, 'isDetectionWithTimeActive': isDetectionWithTimeActive, 'isDetectionWithLDR': isDetectionWithLDR, 'detectionTimeFrom': detectionTimeFrom, 'detectionTimeTo': detectionTimeTo, 'detectionLDRFrom': detectionLDRFrom, 'detectionLDRTo': detectionLDRTo, 'maxDailyEmail':maxDailyEmail,'timeBetweenEmails':timeBetweenEmails
    })

#### APP - To check the LiveCam is active ####
@ app.route('/streaminginfo', methods=['GET'])
def getStreamingInfo():    
    global isLiveCamActive

    if isLiveCamActive == True:        
        scheduler2.add_job(func=setAppTimer, misfire_grace_time=3600)
        return jsonify({'isLiveCamActive': True})
    else:
        return jsonify({'isLiveCamActive': False})

#### SERVER - For E-mailing function ####
@ app.route('/email', methods=['POST'])
def Email():    
    global dailyEmailCounter
    global maxDailyEmail
    
    dailyEmailCounter = dailyEmailCounter + 1    
    print("  ### EMAIL: Daily sent e-mail counter: " + str(dailyEmailCounter) + "/" + str(maxDailyEmail))

    if dailyEmailCounter == maxDailyEmail:
        print("  ### EMAIL: Daily Max E-mail reached.")
        stopMotionDetection()

    return jsonify({'dailyEmailCounter': dailyEmailCounter})

############################   FLASK SERVER   ############################

if __name__ == "__main__":    
    app.run(debug=True, host='0.0.0.0', threaded=True)