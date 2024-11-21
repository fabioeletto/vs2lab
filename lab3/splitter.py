import pickle
import random
import sys
import time

import zmq

import const

context = zmq.Context()
sender = context.socket(zmq.PUSH)  # create a push socket
sender.bind(f'tcp://{const.SRC1}:{const.PORT1}')  # bind socket to address

print("Press Enter when the workers are ready: ")
_ = input()
print("Sending tasks to workers...")

with open('lorem_ipsum.txt', mode='r', encoding='utf-8') as file:
    text = file.read()

paragraphs = text.split('.')

for p in paragraphs: 
    sender.send(pickle.dumps(p))
