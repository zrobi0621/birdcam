import smtplib
import time
import Adafruit_DHT
import atexit
import sys
import requests
from gpiozero import CPUTemperature
from gpiozero import LightSensor
from datetime import datetime
from gpiozero import MotionSensor
from picamera import PiCamera
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# HARDWARE           
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 17                        # can be modified - DHT Sensor's PIN
pir = MotionSensor(4)               # can be modified - PIR Sensor's PIN
ldr = LightSensor(18)               # can be modified - LDR Sensor's PIN

dateTimeNow = ""

# CAMERA SETTINGS
camera = PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = 15
camera.rotation = 0

# EMAIL
SMTP_SERVER = 'smtp.gmail.com'  # Email Server (don't change!)
SMTP_PORT = 587  # Server Port (don't change!)
GMAIL_USERNAME = ''     # change this to match your gmail account
GMAIL_PASSWORD = ''     # change this to match your gmail password

class Emailer:
    def sendmail(self, recipient, subject, content, image):

        # Create Headers
        emailData = MIMEMultipart()
        emailData['Subject'] = subject
        emailData['To'] = recipient
        emailData['From'] = GMAIL_USERNAME

        # Attach our text data
        emailData.attach(MIMEText(content))

        # Create our Image Data from the defined image
        imageData = MIMEImage(open(image, 'rb').read(), 'jpg')
        imageData.add_header(
            'Content-Disposition', 'attachment; filename="madareteto' + dateTimeNow + ".jpg")
        emailData.attach(imageData)

        # Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        # Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        # Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, emailData.as_string())
        session.quit

sender = Emailer()
atexit.register(lambda: camera.close())

##################################
#   Settings
isEmailSendingActive = sys.argv[1]
emailTo1 = sys.argv[2]
emailTo2 = sys.argv[3]
emailTo3 = sys.argv[4]
timeBetweenEmails = int(sys.argv[5])        # in sec

dailyEmailCounter = 0

while isEmailSendingActive == True:      
        
    time.sleep(1)
    pir.wait_for_motion()        
    print("  ### PIR: Motion detected.")
    
    dateTimeNow = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    cpu = CPUTemperature()
    image = '/home/pi/Desktop/BirdCam/Madareteto/Madareteto' + dateTimeNow + '.jpg'
    camera.capture(
        '/home/pi/Desktop/BirdCam/Madareteto/Madareteto' + dateTimeNow + '.jpg')
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    emailSubject = "Mozgás észlelve!"
    emailContent = "Mozgás észlelve: " + time.ctime() + "\nLDR: " + str(ldr.value) + "\nCPU Hőmérséklet: " + \
        str(cpu.temperature) + \
        "*C\nHőmérséklet: {0:0.1f}*C \nPáratartalom: {1:0.1f}%".format(
            temperature, humidity)        

    print("  ### EMAIL: " + dateTimeNow)
    if emailTo1 != "null":
        sendTo = emailTo1
        sender.sendmail(sendTo, emailSubject, emailContent, image)
        print("  ### EMAIL: Email sent to: " + sendTo)        
    if emailTo2 != "null":
        sendTo = emailTo2
        sender.sendmail(sendTo, emailSubject, emailContent, image)
        print("  ### EMAIL: Email sent to: " + sendTo)
    if emailTo3 != "null":
        sendTo = emailTo3
        sender.sendmail(sendTo, emailSubject, emailContent, image)
        print("  ### EMAIL: Email sent to: " + sendTo)

    response = requests.post('http://127.0.0.1:7000/email', data = {'email':'sent'})        # PORT can be modified
    time.sleep(1)
    
    pir.wait_for_no_motion()
    
    # Cooldown
    print("  ### EMAIL: Waiting now " + str(timeBetweenEmails) + " sec")
    time.sleep(timeBetweenEmails)    