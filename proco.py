#! /usr/bin/env python3

#Questions for Monday
# What logic do we use to keep the consumer running? The producer will go until it stops succeeding in extracting frames
# In the demo code, the consumer waits until the queue is empty, but we can't do that for the thread version for obvious reasons
# How do we know the consumer has finished its job?
# How do we test our code? Do we just make two threads each running the other method?

import threading
import cv2
import os
import numpy as np
import base64

#Going to just make pcQueue here

class PCQ:
    def __init__(self):
        self.storage = []
        self.storageLock = threading.Lock()
        self.size = 30        
        self.emptyCells = threading.Semaphore(self.size)
        self.fullCells = threading.Semaphore(0)

    def insert(self, item):
        self.emptyCells.acquire()
        self.storageLock.acquire()
        self.storage.append(item)
        self.storageLock.release()
        self.fullCells.release()

    def remove(self):
        self.fullCells.acquire()
        self.storageLock.acquire()
        item = self.storage.pop(0)
        self.storageLock.release()
        self.emptyCells.release()
        return item

def extractFrames(fileName, queue, maxFramesToLoad=9999):
    #initialize frame count
    count = 0

    #open video file
    vidcap = cv2.VideoCapture(fileName)

    #read first image
    success, image = vidcap.read()

    print(f'Reading frame {count} {success}')
    while success and count < maxFramesToLoad:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the queue
        queue.insert(image)

        success, image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    #Do one more push into the queue on failure to signal to consumer we are done
    queue.insert(None)
    
    print('Frame extraction complete')


def grayFrames(readQueue, writeQueue):
    count = 0
    colorFrame = readQueue.remove()

    while colorFrame is not None:
        grayFrame = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)

        print(f'Graying frame {count}')
        writeQueue.insert(grayFrame)

        count += 1

        colorFrame = readQueue.remove()

    #when loop ends, load None into queue to signal EoF for consumer
    print("Finished Graying Frames")
    writeQueue.insert(None)

    
def displayFrames(queue):
    #initialize frame count
    count = 0
    frame = queue.remove()
    #find logic to keep function going for while loop
    while(frame is not None):

        #get the next frame
        
        
        print(f'Displaying frame {count}')

        #display the image in a window called "video" and wait 42ms
        #before displaying the next frame
    
        cv2.imshow('Video', frame)
        
        if(cv2.waitKey(42) and 0xFF == ord("q")):
            break

        count += 1
        frame = queue.remove()

    print('Finished displaying all frames')
    #cleanup the windows
    cv2.destroyAllWindows()
           
filename = 'clip.mp4'

#producer consumer queue
progray = PCQ()
grayco = PCQ()

producer = threading.Thread(target = extractFrames, args = [filename, progray, 1000])
gray = threading.Thread(target = grayFrames, args = [progray, grayco])
consumer = threading.Thread(target = displayFrames, args = [grayco])

producer.start()
gray.start()
consumer.start()
