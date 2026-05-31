# Brandon Smith
# CS 361
# Spring 2026
# Main Project - Results Limit Microservice

import pandas as pd
import json
import zmq
from io import StringIO


# ---------------------------------------------------------------------
# Set up environment, initialize socket, listen for request from client
# ---------------------------------------------------------------------
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5560")
print("Results limit microservice is connected, now waiting for request")

# ---------------------------------------------------------------------
# Function: limits results to user specified number
# Receives: datafile in JSON format
#           result_limit as int
# Returns: JSON string of truncated data
# ---------------------------------------------------------------------
def limit_results(datafile, result_limit):

    # check that dataset is in correct format
    try:
        my_data = pd.read_json(StringIO(datafile))
    except:
        return None

    # if limit exceeds number of results, return all results
    if result_limit >= len(my_data):
        return my_data.to_json()

    # truncate results to user specified limit
    result = my_data.iloc[:result_limit].copy()

    # convert truncated dataframe to json
    result = result.to_json()

    return result

# loop to continuously run on startup, listening for request.
while True:
    print("Results limit microservice is listening for request")
    message = socket.recv()
    print("Received request: now limiting results")

    # quit microservice, close socket, break
    if message.decode() == "Q":
        socket.send_string("Results limit microservice shutting down.")
        break

    # pull data from request payload
    limit_data = json.loads(message)

    # unpack request payload
    app_file, result_limit = limit_data

    # call limit function on dataset and result limit
    result = limit_results(app_file, result_limit)

    # check for bad datatype
    if result is None:
        print("Please check the datatype. Incorrect data was received. Data should be a csv or Pandas dataframe encoded into JSON")
        socket.send_string("")
    else:
        socket.send_string(result)

context.destroy()
