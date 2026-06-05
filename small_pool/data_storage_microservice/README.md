**Description:**

The data storage microservice handles saving, loading, and overwriting data in CSV files using ZeroMQ.
It allows a client application to store dictionary-based records and perform database-like CRUD operations without needing to write any local CSV file-handling logic
The microservice follows the request-reply pattern to ensure data is safely written or retrieved before the client proceeds with execution.
<br>
<br>

**Architecture and Communication**

This implements a decoupled client-server model using a ZMQ Reuest-Reply pattern.
While the client application interacts with simple Python function imported from data_storage_functions.py, no local file I/O happens in the calling program.
Those helper functions are meant to act as wrappers hiding the network layer by packing arguments into structured JSON strings, opening a temporary ZMQ socket, transmitting the payload across a network port, and blocking until the microservice sends a formal acknowledgement back.
<br>
<br>

**Port:** 

tcp://localhost:5555
<br>
<br>


**How To Use The Microservice:**
<br>
<br>


**Setup:**
1. Install the ZeroMQ dependency

       pip install pyzmq

2. Place both the data_microservice.py file and data_storage_functions.py in your project directory
   
3. Start the microservice in a separate terminal to keep it listening for incoming requests

        python data_microservice.py

<br>
<br>

**Implementation:**

In your own file, import the functions from data_storage_functions.py
<br>
<br>

**Saving Data**: To append a single record, pass a Python dictionary where the keys are your desired CSV column headers into save_data()

(This function connects via ZMQ and sends a {"command": "save", ...} payload. The microservice validates that the payload is a dictionary, appends it as a new row, and replies.)

    Example 1:
    from data_storage_functions import save_data
    
    data_being_saved = {"name": "Max", "job": "student", "age": "24"}
    save_data("chosen_filename, data_being_saved)
    
    
    Example 2:
    from data_storage_functions import save_data
    
    new_users = [
       {"name": "Max", "job": "student", "age": "24"}
       {"name": "Alice", "job": "athlete", "age": "25"}
       {"name": "Kim", "job": "chef", "age": "27"}
    
    for user in new_users:
       save_data("chosen_filename", user)

<br>
<br>

**Loading Data**: Retrieves all rows from a CSV file

(This sends a {"command": "load"} request over port 5555. The microservice reads the file, parses rows into a list of dictionaries, and returns it over the network socket.)

    Example:
    from data_storage_functions import load_data
    
    data_being_loaded = load_data("chosen_filename")
    for record in data_being_loaded:
       print(f"Name: {record['name']}, {record['job']}, {record['age']}")

<br>
<br>  

**Save All Data**: Overwites the entire contents of the target CSV file with the specified list of dictionaries.

(Sends a {"command": "save_all"} payload. The microservice runs a validation check to ensure the payload is a valid list before wiping and writing the file.)

    Example:
    from data_storage_functions import save_all_data
    
    new_csv_data = [
           {"name": "Max", "job": "Analyst", "age": "26"},
           {"name": "Crystal", "job": "Engineer", "age": "24"}
    ]
    
    save_all_data("users.csv", new_csv_data)

<br>
<br>
  
**Clearing All Data**:

This removes all records from the target CSV file.

    Example:
    from data_storage_functions import clear_all_data
    
    clear_all_data("users.csv")

<br>
<br>

**Parameters**
If you want to communicate directly with the port via raw ZMQ sockets, requests and responses must match the following JSON schema:

    i. command (string) -- "save", "load" or "save_all"
   
    ii. filename (string) -- target .csv filename
  
    iii. data (object) -- dictionary or list of dictionaries

<br>
<br>

**Response Format:**
Successful requests return:

    {"status": "success"}

Load requests return:

    {"status": "success", "data": [...]}
       
Invalid commands return:

    {"status": "error", "message": "Unknown command"}
    
<br>
<br>

**UML Diagram**
   
   <img width="895" height="629" alt="image" src="https://github.com/user-attachments/assets/0d239451-e440-418c-8425-3790f41ff2c4" />



