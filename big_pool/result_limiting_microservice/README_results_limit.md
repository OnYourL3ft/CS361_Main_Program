# Results Limit Microservice

## Function:
Takes a dataset in the format of a JSON list and a user specified integer, converts
the dataset to a pandas dataframe, and truncates the results to the specified limit.
If the specified limit exceeds the number of results in the dataset, all results are
returned. The microservice is called via a ZMQ Request - Response pipeline.
The details of how to setup the ZMQ environment, make a request, and receive a reply
can be found below.

## How to Run:

1. Install dependencies for dev environment

   pip install pyzmq

   pip install pandas

2. Import dependencies for main/calling/client application

   import subprocess

   import zmq

   import json

   import time

   from io import StringIO

3. Start up the results limit microservice by running it as a separate process on main app startup using:
```python
limit_process = subprocess.Popen(['python', 'results_limit_microservice.py'])
```
4. Use sleep so main app doesn't try connecting before microservice can be started

   time.sleep(1)

5. Quit signal when main program shuts down

   send 'Q' to the microservice to initiate cleanup

## Example Call/Request:
socket is initialized and connects to results limit microservice via port 5560.
After payload is converted into json, the payload/request is sent via socket.send_string(request).

### Request Parameters:
- `dataset` — the data to be limited, sent as a JSON-encoded string (converted from a pandas DataFrame)
- `result_limit` — a positive integer specifying the number of results to display

### Environment set up
```python
context = zmq.Context()
```

### Create socket for results limit microservice
```python
limit_socket = context.socket(zmq.REQ)
limit_socket.connect("tcp://localhost:5560")
```

### Request
```python
request = json.dumps([dataframe, result_limit])
limit_socket.send_string(request)
```

## Example Receipt:

### Receive response/limited data
### Calling/client program will wait until response is received. socket.recv_string() must be used to receive the response
### for the client program to continue.
```python
limited_data = limit_socket.recv_string()
```

### IMPORTANT: response must be checked for empty string. Invalid datasets sent to the microservice will send back "" as a response.
Check for invalid response
```python
if limited_data:
    results = pd.read_json(StringIO(limited_data))
else:
    print('-' * 60)
    print(" Error: Result limit request could not be completed. Please try again. ")
    print('-' * 60)
```

### IMPORTANT: To allow the user to change the limit multiple times without permanently truncating results,
### always send the original untruncated dataset to the microservice, not the previously limited version.
```python
# save original results before any limiting
original_results = results.copy()

# always send original results to microservice
request = json.dumps([original_results.to_json(), result_limit])
limit_socket.send_string(request)
```

## Other Notes
results_limit_microservice.py runs as a separate process on port 5560 using a ZMQ REP socket.
It is launched automatically using the code above. Do not run results_limit_microservice.py manually.
