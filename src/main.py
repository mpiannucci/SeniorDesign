#!/usr/bin/python

'''
OCE 495 Senior Design Bridge Monitoring

Handle data collection from ADS1115 ADC with a BeagleBone. Then do relevant things
with the data, For now print out or log the raw data to a file to get bare bones of
the package up and running.

To run this script fill in these variables for your application:
      SAMPLE_RATE     = The sample rate for data collection, (int) in Hz
      DURATION        = The duration for data logging, (int) in seconds
      LOGFILE_NAME    = The logfile to save the data to, (string) relative path
      CHANNELS        = The channels to collect data to in an array, [int, int] from 0-3
      ADC_ADDRESS_1   = The I2C address of the first ADC (Defualt is 0x48)

PIN SETUP:
      TIMER PIN = P8_12
      GPS TX    = P9_26
      GPS RX    = P9_24
      ADC SCL   = P9_19
      ADC SDA   = P9_20

TODO: Eventually, this script could be used to send the log file to a remote computer using
      a wifi dongle, or Xbee module. This way a remote computer can gather data from multiple
      sensor packages for data analysis.

      The only missing functionality of this script right now is the ability to analyze the data.
      Right now it seems that the most glaring imperfection of this program is the weird time delay
      in between logging the data and writing it to a file. I am completely uncertain what is causing
      this and what the delay even is.

Written By: Matthew Iannucci with Adafruit's BeagleBone Python Libraries
Fall 2013
'''
import signal
import sys
import time
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1x15

ADS1115 = 0x01    # 16-bit ADC Address

GPSENABLED = False
SAMPLE_RATE = 200
DURATION = 10
LOGFILE_NAME = 'rawData.txt'
CHANNELS = [0, 2, 3]
TIMER_PIN = 'P8_12'
ADC_ADDRESS_1 = 0x48

def signal_handler(signal, frame):
    '''
    Handle a keyboard interrupt
    '''
    print 'You pressed Ctrl+C! Exiting...\n'
    sys.exit(0)

def initGPIO(pin):
    '''
    Initialize the GPIO
    '''
    GPIO.setup(pin, GPIO.IN)
    print 'GPIO Initialized'

def sampleRun(duration, sampleRate, channels, timer_pin):
    '''
    Sample from the ADC and log into an array
    '''
    # Initialise the ADC using the default mode
    # For now only use one ADC, so only create one ADC object
    print 'Data collection started...Press Ctrl+C to exit\n'
    adc = ADS1x15(address=ADC_ADDRESS_1, ic=ADS1115)
    gps = []
    if GPSENABLED:
        from Copernicus_GPS import GPS
        gps = GPS()
    samples = range(0, ((duration*sampleRate)-1))
    volts = [None] * len(samples)
    for sample in samples:
        GPIO.wait_for_edge(TIMER_PIN, GPIO.RISING)
        if not isinstance(channels, int):
            # Read channels 0 through 2 in single-ended mode, +/-3.3V, 200sps
            # Eventually, this can be called multiple times with different objects to provide access
            # to data from multiple ADC's. Uncomment the first one to include a timestamp.
            if GPSENABLED:
                volts[sample] = [adc.readADCSingleEnded(channels[0], 3300, sampleRate) / 1000,
                                 adc.readADCSingleEnded(channels[1], 3300, sampleRate) / 1000,
                                 adc.readADCSingleEnded(channels[2], 3300, sampleRate) / 1000,
                                 gps.getData()[0]]
            else:
                volts[sample] = [adc.readADCSingleEnded(channels[0], 3300, sampleRate) / 1000,
                                 adc.readADCSingleEnded(channels[1], 3300, sampleRate) / 1000,
                                 adc.readADCSingleEnded(channels[2], 3300, sampleRate) / 1000]
        else:
            #volts[sample] = [adc.readADCSingleEnded(channels, 3300, SAMPLE_RATE) / 1000, gps.getData()[0]]
            volts[sample] = adc.readADCSingleEnded(channels, 3300, SAMPLE_RATE) / 1000
    return volts

def log(filename, data, sampleRate, duration, channels):
    '''
    Log the data collected in an array to a file to be used for later
    '''
    fp = open(filename, 'w+')
    fp.write('ADS 1115 Data Collection\nSample Rate: ' + str(sampleRate) + ' Herz\nDuration: ' + str(duration) + ' Seconds\n')
    fp.write(time.strftime('%X %x %Z') + '\n--------------------------------------------------------------\n')
    for dataset in data:
        if isinstance(channels, int):
            fp.write(str(dataset) + '\n')
        else:
            j = 0
            if GPSENABLED:
                j = range(0,len(channels)+1)
            else:
                j = range(0,len(channels))
            for k in j:
                if k == max(j):
                    fp.write(str(dataset[k]) + '\n')
                else:
                    fp.write(str(dataset[k]) + ',')
    print 'Data logged to ' + filename + '\n'

def main(filename, sampleRate, duration, channels, timer_pin):
    '''
    Run the main log for the data logging application
    '''
    initGPIO(timer_pin)
    data = sampleRun(duration, sampleRate, channels, timer_pin)
    print 'Finished data collection. Logging...\n'
    log(filename, data, sampleRate, duration, channels)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(LOGFILE_NAME, SAMPLE_RATE, DURATION, CHANNELS, TIMER_PIN)
    print 'Data logging successful. Exiting...\n'