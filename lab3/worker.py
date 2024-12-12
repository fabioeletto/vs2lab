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
    
    for w in words:
        if len(w) > 5:
            sender_reducer_2.send(pickle.dumps(w))
        elif len(w) > 0: 
            sender_reducer_1.send(pickle.dumps(w))
    

    print(f'{me} did something...\n')
    time.sleep(1)
