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

procname = 'arecord'
filepath = " /home/pi"

def start_recording(channel):
    global filepath
    global procname
    process = subprocess.Popen ("arecord -Dhw:1,0 -r 44100 -c1 -f S16_LE "+ filepath + "/recording.wav", shell=True) #channels = 2 for stereo
    print "PID " + str(process.pid)
    print "Recording started"

def stop_recording(channel):
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

start_recording(0)
time.sleep(10)
stop_recording(0)
print " Quit"
