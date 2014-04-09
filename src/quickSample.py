#!/usr/bin/python

'''
OCE 495 Senior Design Bridge Monitoring

Written By: Matthew Iannucci
Spring 2014

'''
import signal
import sys
import time
from libs.Adafruit_ADS1x15 import ADS1x15

ADS1115 = 0x01  # 16-bit ADC Address
ADC_ADDRESS_1 = 0x48  # Default, when the right pin is grounded

SAMPLE_RATE = 100  # in herz
SAMPLE_DURATION = 60  # in seconds
TEST_DURATION = 120  # in minutes
LOGFILE_NAME = 'rawData'  # without the extension
CHANNELS = [0, 1, 2]  # ADC channels to read in on

def signal_handler(signal, frame):
    '''Handle a keyboard interrupt
    '''
    print 'You pressed Ctrl+C! Exiting...\n'
    sys.exit(0)


class QuickSample:
    
    def __init__(self, filename, sampleRate, sampleDuration, testDuration, channels):
        '''Default constructor block

        @param filename The base filename to record data to (Without file extension)
        @param sampleRate The ADC sample rate in Herz
        @param sampleDuration The duration to sample during each window in seconds
        @param testDuration How long the entire test lasts in seconds
        @param channels An array containing eahc channel to sample on i.e. [1,2,3]

        @return New QuickSample object

        '''
        self.filename = filename
        self.sampleRate = sampleRate
        self.sampleDuration = sampleDuration
        self.testDuration = testDuration
        self.channels = channels

    def sampleRun(self):
        '''Sample from the ADC and log into an array

        @return An array of data of length channels X samples
        '''
        # Initialise the ADC using the default mode
        # For now only use one ADC, so only create one ADC object
        adc = ADS1x15(address=ADC_ADDRESS_1, ic=ADS1115)
        samples = range(0, ((self.sampleDuration*self.sampleRate)-1))
        volts = [None] * len(samples)  # Initialize the array to print to
        for sample in samples:
            if not isinstance(self.channels, int):
                volts[sample] = [adc.readADCSingleEnded(self.channels[0], 3300, self.sampleRate) / 1000,
                                 adc.readADCSingleEnded(self.channels[1], 3300, self.sampleRate) / 1000,
                                 adc.readADCSingleEnded(self.channels[2], 3300, self.sampleRate) / 1000]
            else:
                volts[sample] = adc.readADCSingleEnded(self.channels, 3300, SAMPLE_RATE) / 1000
        return volts

    def log(self, rectime, data):
        '''Log the data collected in an array to a file to be used for later
        '''
        fp = open(self.filename + '-' + str(rectime) + '.txt', 'w+')
        fp.write('ADS 1115 Data Collection\nSample Rate: ' + str(self.sampleRate) + ' Herz\nDuration: ' + str(self.sampleDuration) + ' Seconds\n')
        fp.write(time.strftime('%X %x %Z') + '\n--------------------------------------------------------------\n')
        for dataset in data:
            if isinstance(self.channels, int):
                fp.write(str(dataset) + '\n')
            else:
                j = 0
                j = range(0,len(self.channels))
                for k in j:
                    if k == max(j):
                        fp.write(str(dataset[k]) + '\n')
                    else:
                        fp.write(str(dataset[k]) + ',')
        print 'Data logged to ' + self.filename + str(rectime) + '.txt' + '\n'

    def mainLoop(self):
        '''Run the main log for the data logging application
        '''
        print "Data collection initiated. Press Ctrl+C to cancel"
        i = 0
        while i < (self.testDuration/15):
            rectime = time.clock()
            data = self.sampleRun()
            self.log(rectime, data)
            time.sleep(15*60)  # Sleep for 15 minutes
            i += 1
        print 'Finished data collection. Logging...\n'

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    q = QuickSample(LOGFILE_NAME, SAMPLE_RATE, SAMPLE_DURATION, TEST_DURATION, CHANNELS)
    q.mainLoop()
    print 'Data logging successful. Exiting...\n'