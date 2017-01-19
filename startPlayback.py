import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time
import os
import subprocess
import datetime
import psutil #used to kill arecord
import signal
#to install psutil:
#sudo apt-get install python-dev
#sudo apt-get install python-psutil

procnameParent = 'aplayLoop.sh'
procnameChild = 'aplay'
filepath = " /home/pi"
pid = 0

def start_playback(channel):
    global filepath
    global procname
    process = subprocess.Popen ("aplayLoop.sh "+ filepath + "/foo.wav", shell=True) #channels = 2 for stereo
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
              
start_playback(0)
time.sleep(20)
stop_playback(0)
print " Quit"
