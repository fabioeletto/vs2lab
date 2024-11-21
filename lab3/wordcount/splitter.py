import pickle
import random
import sys
import time

import zmq

import constPipe

context = zmq.Context()

push_socket_to_mapper = context.socket(zmq.PUSH)
push_socket_to_mapper.bind(f'tcp://{constPipe.SRC}:{constPipe.PORT_SPLITTER}')  

sentences = []
file = open("text.txt", "r")
while True:
    line = file.readline()
    if not line:
        break
    sentences.append(line)
file.close()

sentences.append(constPipe.EOF)

for sentence in sentences:
    push_socket_to_mapper.send(pickle.dumps(sentence))
