import os

i = 0
while os.path.exists("/media/usb/%03d.wav" % i):
    i += 1

filename = ("/media/usb/%03d.wav" % i)
thefile = open(filename, 'w')    
thefile.write("Hello World!\n")
