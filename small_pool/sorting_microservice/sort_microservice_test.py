# Sort Microservice Test Script
# Tests both the ZeroMQ communication pipe and sort_microservice function
# Tests default sorting, user specified parameters, and bad data

import zmq
import json
import time
import subprocess
import pandas as pd
from io import StringIO


# ---------------------------------------------------------------------
# Test data - fake TV show data matching dataset attributes
# ---------------------------------------------------------------------
tv_show_data = pd.DataFrame( [
    {"Name": "Breaking Bad",    "Genres": "Drama, Crime",   "Network": "AMC",     "Language": "English", "Total Seasons": 5,  "Total Episodes": 62, "Average Runtime": 45, "Critic_Rating": 9.5, "User_Rating": 9.4, "Metacritic_Rating": 8.7},
    {"Name": "The Wire",        "Genres": "Drama, Crime",   "Network": "HBO",     "Language": "English", "Total Seasons": 5,  "Total Episodes": 60, "Average Runtime": 58, "Critic_Rating": 9.3, "User_Rating": 9.3, "Metacritic_Rating": 9.6},
    {"Name": "Severance",       "Genres": "Drama, Sci-Fi",  "Network": "Apple+",  "Language": "English", "Total Seasons": 2,  "Total Episodes": 19, "Average Runtime": 52, "Critic_Rating": 8.8, "User_Rating": 8.7, "Metacritic_Rating": 8.4},
    {"Name": "Shogun",          "Genres": "Drama, History", "Network": "FX",      "Language": "English", "Total Seasons": 1,  "Total Episodes": 10, "Average Runtime": 60, "Critic_Rating": 8.9, "User_Rating": 8.8, "Metacritic_Rating": 9.9},
    {"Name": "Succession",      "Genres": "Drama, Comedy",  "Network": "HBO",     "Language": "English", "Total Seasons": 4,  "Total Episodes": 39, "Average Runtime": 65, "Critic_Rating": 9.0, "User_Rating": 8.0, "Metacritic_Rating": 9.2},
]).to_json()

# ---------------------------------------------------------------------
# Start sort microservice as subprocess
# ---------------------------------------------------------------------
print("Starting sort microservice...")
sort_process = subprocess.Popen(['python', 'sort_microservice.py'])
time.sleep(2)

# ---------------------------------------------------------------------
# Set up ZeroMQ connection
# ---------------------------------------------------------------------
context = zmq.Context()
sort_socket = context.socket(zmq.REQ)
sort_socket.connect("tcp://localhost:5556")
print("Connected to sort microservice on port 5556\n")

# ---------------------------------------------------------------------
# Test 1: sort by critic rating, ascending
# ---------------------------------------------------------------------
print("-" * 60)
print("TEST 1: Sort dataframe by ascending critic rating")
print("-" * 60)


request = json.dumps([tv_show_data, "Critic_Rating", 3])
sort_socket.send_string(request)
sort_receive = sort_socket.recv_string()
time.sleep(3)

if sort_receive == "":
	print("The sorting was not successful. Please try again.")
else:
	sorted_tv_df = pd.read_json(StringIO(sort_receive))
	print("Here are the sorted tv shows")
	print(sorted_tv_df.to_string())
print()

# ---------------------------------------------------------------------
# Test 2: sort by user rating, descending
# ---------------------------------------------------------------------
print("-" * 60)
print("TEST 2: sort by descending user rating")
print("-" * 60)


request = json.dumps([tv_show_data, "User_Rating", 4])
sort_socket.send_string(request)
sort_receive = sort_socket.recv_string()
time.sleep(3)

if sort_receive == "":
	print("The sorting was not successful. Please try again.")
else:
	sorted_tv_df = pd.read_json(StringIO(sort_receive))
	print("Here are the sorted tv shows")
	print(sorted_tv_df.to_string())

print()

# ---------------------------------------------------------------------
# Test 3: sort by run time, ascending
# ---------------------------------------------------------------------
print("-" * 60)
print("TEST 3: sorting by ascending run time")
print("-" * 60)

request = json.dumps([tv_show_data, "Average Runtime", 3])
sort_socket.send_string(request)
sort_receive = sort_socket.recv_string()
time.sleep(3)

if sort_receive == "":
	print("The sorting was not successful. Please try again.")
else:
	sorted_tv_df = pd.read_json(StringIO(sort_receive))
	print("Here are the sorted tv shows")
	print(sorted_tv_df.to_string())

print()

# ---------------------------------------------------------------------
# Test 4: sort by defaults (title and ascending)
# ---------------------------------------------------------------------

print("-" * 60)
print("TEST 4: sorting by default title and ascending")
print("-" * 60)

request = json.dumps([tv_show_data, None, None])
sort_socket.send_string(request)
sort_receive = sort_socket.recv_string()
time.sleep(3)

if sort_receive == "":
	print("The sorting was not successful. Please try again.")
else:
	sorted_tv_df = pd.read_json(StringIO(sort_receive))
	print("Here are the sorted tv shows")
	print(sorted_tv_df.to_string())

print()

# ---------------------------------------------------------------------
# Test 5: Bad data
# ---------------------------------------------------------------------

print("-" * 60)
print("TEST 5: sorting with bad data")
print("-" * 60)

request = json.dumps(["this is bad data", None, None])
sort_socket.send_string(request)
sort_receive = sort_socket.recv_string()
time.sleep(3)

if sort_receive == "":
	print("The sorting was not successful. Please try again.")
else:
	sorted_tv_df = pd.read_json(StringIO(sort_receive))
	print("Here are the sorted tv shows")
	print(sorted_tv_df.to_string())

print()

# ---------------------------------------------------------------------
# Clean up
# ---------------------------------------------------------------------
sort_socket.send_string("Q")
sort_receive = sort_socket.recv_string()
time.sleep(1)
sort_socket.close()
context.destroy()

print("-" * 60)
print("All tests complete.")
print("-" * 60)