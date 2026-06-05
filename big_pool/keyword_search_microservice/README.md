**Description:**

The keyword search microservice handles filtering the dataset (lists of dictionaries) based on specific column headers and substring matches using ZeroMQ. It operates as a background process that allows the client application to perform a case-insensitive keyword search across any dataset. The microservice follows the request-reply pattern to ensure the dataset is safely processed and filtered before the client proceeds with execution. 
<br>
<br>
**Architecture and Communication:**

This microservice implements a decoupled client-server model using a ZMQ Request-Reply pattern. External applications communicate with this service by packing arguments into structured JSON strings, opening a temporary ZMQ socket (REQ), transmitting the payload across the network, and blocking until the microservice execeutes the search and sends a response back. 
<br>

**Port:**
tcp://localhost:5552
<br>

**Setup:**
1. Install the ZeroMQ dependency

       pip install pyzmq

2. Place the microservice code in your directory
3. Start the microservice in a separate terminal to keep it listening for incoming requests

       python search_microservice.py
<br>

**Implementation:**

In your own application file, establish a ZeroMQ REQ socket connection pointing to port 5552 to interact with the service.
<br>
<br>
Searching Data: To search or filter a dataset, construct a JSON payload with the "find" command. Pass the specific key/column name you want to inspect, they keyword string you want to find, and the data itself. 
<br>
<br>
The microservice validates the data strcutures, gets the matching dictionaries, and replies.

    Example:
    import zmq
    import json

    # initialize the connection 
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5552")

    # sample data
    data_to_search = [
      {"id": "101", "title": "Avengers"},
      {"id": "102", "title": "Dark Knight"},
      {"id": "103", "title": "Avengers: Infinity War"},
    ]

    payload = {
      "command": "find",
      "key": "title",
      "keyword": "avengers",
      "dataset": data_to_search,
    }

    socket.send_string(json.dumps(payload))

    response = json.loads(socket.recv_string())
    if response.get("status" == "success":
      search_results = response.get("results")

      for record in serach_results:
        print(f"Found Match: {record['title']}")
<br>

**Parameters:**

To communicate directly with the port, requests and responses must match the following JSON schema:

    command (string) -- must be "find"
    key (string) -- the target dictionary key or column header to execute search logic with
    dataset(array/list) -- a list of dictionary objeccts containing the records that will be filtered through
    keyword (string) -- the text pattern to match
<br>

**Response Format:**

Successful requests:

    {
      "status": "success", 
      "results": [...]
    }

Missing parameters or validation issues:

    {
      "status": "error", 
      "message": "Missing required structural parameters ('key' or 'dataset')."
    }

Invalid commands:

    {
      "status": "error", 
      "message": "Invalid command. Expected 'find'."
    }

   
