import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])

context = zmq.Context()

receive_socket_from_splitter = context.socket(zmq.PULL)
receive_socket_from_splitter.connect(f'tcp://{constPipe.SRC}:{constPipe.PORT_SPLITTER}')

push_socket_to_reducer1 = context.socket(zmq.PUSH)
push_socket_to_reducer1.bind(f'tcp://{constPipe.SRC}:{constPipe.PORT_MAPPER1}')

push_socket_to_reducer2 = context.socket(zmq.PUSH)
push_socket_to_reducer2.bind(f'tcp://{constPipe.SRC}:{constPipe.PORT_MAPPER2}')

time.sleep(1) 

print(f'{me}.Mapper started')

while True:
    print("Waiting for work ...")
    word_text = pickle.loads(receive_socket_from_splitter.recv())  # receive work from a source

    words = word_text.split()

    for word in words:
        if word == constPipe.EOF:
            push_socket_to_reducer1.send(pickle.dumps(constPipe.EOF))
            push_socket_to_reducer2.send(pickle.dumps(constPipe.EOF))
            break

        reducer_index = hash(word) % 2
        if reducer_index == 0:
            push_socket_to_reducer1.send(pickle.dumps(word))
        else:
            push_socket_to_reducer2.send(pickle.dumps(word))
        print(f'{me} sent word {word} to reducer {reducer_index}')
