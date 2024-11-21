import pickle
import sys
import time
from collections import defaultdict

import zmq

import constPipe



me = str(sys.argv[1])

context = zmq.Context()

receive_socket_from_mapper = context.socket(zmq.PULL)
receive_socket_from_mapper.connect(f'tcp://{constPipe.SRC}:{constPipe.PORT_MAPPER1 if me == "1" else constPipe.PORT_MAPPER2}')

print(f'{me}.Reducer started')

word_count = defaultdict(int)

while True:
    print("Waiting for work ...")
    word = pickle.loads(receive_socket_from_mapper.recv())  # receive work from a source

    if word == constPipe.EOF:
        for key, value in word_count.items():
            print(f"{key}: {value} times ")
        print(f"Different words: {len(word_count)}")
        print(f"Total words: {sum(word_count.values())}")
        break

    word_count[word] += 1
    print(f'{me} received word {word}')
    