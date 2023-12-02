#! /usr/bin/env python3

#Going to just make pcQueue here
import threading

class PCQ:
    def __init__(self):
        self.storage = []
        self.storageLock = threading.Lock(storage)
        self.size = 30        
        self.emptyCells = Semaphore(self.size)
        self.fullCells - Semaphore(0)

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
        
