import pickle
import sys
import time

import zmq

import const

context = zmq.Context()

me = sys.argv[1]

receiver = context.socket(zmq.PULL)
receiver.connect(f'tcp://{const.SRC1}:{const.PORT1}')

sender_reducer_1 = context.socket(zmq.PUSH)
sender_reducer_1.connect(f'tcp://{const.SRC3}:{const.PORT3}')


sender_reducer_2 = context.socket(zmq.PUSH)
sender_reducer_2.connect(f'tcp://{const.SRC4}:{const.PORT4}')

while True:
    print(f'{me} waiting for work...')
    work = pickle.loads(receiver.recv())  # receive work from a source
    
    words = work.split(' ')
    
    short_words = []
    long_words = []
    
    for w in words:
        if len(w) > 5:
            long_words.append(w)
        else: 
            short_words.append(w)

    sender_reducer_1.send(pickle.dumps(short_words))
    sender_reducer_2.send(pickle.dumps(long_words))

    print(f'{me} did something...\n')
    time.sleep(1)
