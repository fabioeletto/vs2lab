import pickle
import sys
import time

import zmq

import const

me = sys.argv[1]
context = zmq.Context()

receiver = context.socket(zmq.PULL)

if me == '1':
    receiver.bind(f'tcp://{const.SRC3}:{const.PORT3}')
elif me == '2':
    receiver.bind(f'tcp://{const.SRC4}:{const.PORT4}')
else:
    pass

word_count = {}

while True:
    words = pickle.loads(receiver.recv())
    for word in words:
        if word_count.get(word, False):
            word_count[word] += 1
        else:
            word_count[word] = 1

    print(f'{me} received results:\n{word_count}\n')
    time.sleep(1)
    