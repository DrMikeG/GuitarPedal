#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import os
import subprocess
import datetime
import psutil #used to kill arecord
import signal

# members for GPIO
recordingLEDState = 0
playbackLEDState = 0
recordingLEDPin = 20
playbackLEDPin = 21

# common to both playback and record
fullfilepathandname = " /media/usb/000.wav"
filepath = " /home/pi"
filename = "/foo.wav"

# members for playback
procnameParent = 'aplayLoop.sh'
procnameChild = 'aplay'
# members for recording
procname = 'arecord'


# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(recordingLEDPin, GPIO.OUT)
GPIO.setup(playbackLEDPin, GPIO.OUT)

# GPIO 24 set up as an input, pulled down, connected to 3V3 on button press
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# playback methods
def start_playback(channel):
    global filepath
    global filename
    global fullfilepathandname
    global procnameParent
    #if os.path.exists(filepath + filename):
    #process = subprocess.Popen (procnameParent+" "+ filepath + filename, shell=True)
    process = subprocess.Popen (procnameParent+" "+ fullfilepathandname, shell=True)
    print "PID " + str(process.pid)
    print "Playback started"

def stop_playback(channel):
    global procnameParent
    global procnameChild
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            if proc.name() == procnameChild or proc.name() == procnameParent:
                print "Killing process: "+proc.name()
                print "process ID= "+str(proc.pid)
                proc.kill()
                print "Playback parent stopped"

# recording methods

def start_recording(channel):
    global filepath
    global filename
    global fullfilepathandname
    global procname
    i = 0
    while os.path.exists("/media/usb/%03d.wav" % i):
        i += 1
    fullfilepathandname = ("/media/usb/%03d.wav" % i)
    #process = subprocess.Popen ("arecord -Dhw:1,0 -r 44100 -c1 -f S16_LE "+ filepath + filename, shell=True) #channels = 2 for stereo
    process = subprocess.Popen ("arecord -Dhw:1,0 -r 44100 -c1 -f S16_LE "+ fullfilepathandname, shell=True) #channels = 2 for stereo

    print "PID " + str(process.pid)
    print "Recording started"

def stop_recording(channel):
    global procname
    print "looking for process name: "+procname
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            if proc.name() == procname:
                print "Killing process: "+proc.name()
                print "process ID= "+str(proc.pid)
                proc.send_signal(signal.SIGKILL)
                print "Recording stopped"

# gpio handling callback methods

def recording_callback(channel):
    global playbackLEDState
    global recordingLEDState

    if recordingLEDState == 1:
        print "Turning off LED"
        recordingLEDState= 0
        stop_recording(0)
    else:
        
        if playbackLEDState == 1: # If we are still playing when someone presses record
            playback_callback(0)  # then stop playing...

        print "Turning on LED"
        recordingLEDState = 1
        start_recording(0)

    GPIO.output(recordingLEDPin,recordingLEDState)

def playback_callback(channel):
    global playbackLEDState
    global recordingLEDState

    if playbackLEDState == 1:
        print "Turning off LED"
        playbackLEDState= 0
        stop_playback(0)
    else:

        if recordingLEDState == 1: # If we are still recording when someone presses play
            recording_callback(0)  # then stop recording...
            
        print "Turning on LED"
        playbackLEDState = 1       
        start_playback(0)

    GPIO.output(playbackLEDPin,playbackLEDState)


def my_callback2(channel):
    print "falling edge detected on 23"


#print "Make sure you have a button connected so that when pressed"
#print "it will connect GPIO port 23 (pin 16) to GND (pin 6)\n"
#print "You will also need a second button connected so that when pressed"
#print "it will connect GPIO port 24 (pin 18) to 3V3 (pin 1)\n"
#print "You will also need a third button connected so that when pressed"
#print "it will connect GPIO port 17 (pin 11) to GND (pin 14)"
#raw_input("Press Enter when ready\n>")

# when a falling edge is detected on port 17, regardless of whatever
# else is happening in the program, the function my_callback will be run
GPIO.add_event_detect(18, GPIO.BOTH, callback=recording_callback, bouncetime=300)

# when a falling edge is detected on port 23, regardless of whatever
# else is happening in the program, the function my_callback2 will be run
# 'bouncetime=300' includes the bounce control written into interrupts2a.py
GPIO.add_event_detect(17, GPIO.BOTH, callback=playback_callback, bouncetime=300)

try:
    print "Listening for stomps..."
    GPIO.wait_for_edge(24, GPIO.RISING)
    #print "Rising edge detected on port 24. Here endeth the third lesson."

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit

