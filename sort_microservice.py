# Spring 2026
# CS 361
# Main Project - Sort microservice

import pandas as pd
import json
import zmq
from io import StringIO


# ---------------------------------------------------------------------
# Set up spike protocol
# Create environment, initialize socket, listen for request from client
# ---------------------------------------------------------------------
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
print("Socket is connected, now waiting for request")
# ---------------------------------------------------------------------
# Function: sorts data in order specified by user
# Receives: datafile in JSON format
#           parameter used for sorting in string format
#           sort method as int
# Returns: JSON file of sorted data
# ---------------------------------------------------------------------
def sort_micro(datafile, attribute=None, sort_method=3):

    # check that dataset is in correct format
    try:
        my_data = pd.read_json(StringIO(datafile))
    except:
        return None


    # sort by column 1 if no attribute specified
    if attribute is None:
        attribute = my_data.columns[0]

    # determine sort direction, default is ascending
    if sort_method == 3 or sort_method is None:
        # ascending
        sort_method = True
    else:
        # descending
        sort_method=False

    # copy sorted dataframe
    result = my_data.sort_values(by=attribute, ascending=sort_method).copy()

    # convert sorted dataframe to json
    result = result.to_json()

    return result

# loop to continuously run on startup, listening for request.
while True:
    print("sort microservice is listening for request")
    message = socket.recv()
    print("Received request: now sorting data")

    # quit microservice running, close socket, break
    if message.decode() == "Q":
        socket.send_string("Sort microservice shutting down.")
        break

    # pull data from request payload
    sort_data = json.loads(message)

    # unpack request payload
    app_file, data_attr, sort_method = sort_data

    # call sort function on dataset, data_attribute, and sort direction
    result = sort_micro(app_file, data_attr, sort_method)

    # check for bad datatype
    if result is None:
        print("Please check the datatype. Incorrect data was received. Data should be a csv or Pandas dataframe encoded into JSON")
        socket.send_string("")
    else:
        socket.send_string(result)

context.destroy()

