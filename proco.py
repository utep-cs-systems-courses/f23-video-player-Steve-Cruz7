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
        self.storageLock = threading.Lock(storage)
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

    print('Frame extraction complete')

def displayFrames(queue):
    #initialize frame count
    count = 0

    #find logic to keep function going for while loop
    while(true):

        #get the next frame
        frame = queue.remove()

        print(f'Displaying frame {count}')

        #display the image in a window called "video" and wait 42ms
        #before displaying the next frame
    
        cv2.imshow('Video', frame)
        
        if(cv2.waitKey(42) and 0xFF == ord("q")):
            break

        count += 1

    print('Finished displaying all frames')
    #cleanup the windows
    cv2.destroyAllWindows()
           
filename = 'clip.mp4'

#producer consumer queue
proco = PCQ()

producer = threading.Thread(target = extractFrames, args = [filename, proco, 72])
consumer = threading.Thread(target = displayFrames, args = [proco])

producer.start()
consumer.start()
