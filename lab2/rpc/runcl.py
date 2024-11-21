import rpc
import logging
import time

from context import lab_logging

def print_server_response(result_list):
    print("Received result from long running operation: {}".format(result_list.value))

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, print_server_response)

print("Waiting for server response, but not blocking")
time.sleep(2)
print("Still waiting for server response, but not blocking")
time.sleep(2)
print("Still waiting for server response, but not blocking")
time.sleep(15)# simulate that the client is doing something else

cl.stop()
