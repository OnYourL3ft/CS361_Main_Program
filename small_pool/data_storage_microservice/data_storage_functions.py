import zmq

SERVICE_ADDR = "tcp://localhost:5555"




def _send_request(payload):
    """Internal helper to handle ZeroMQ communication."""
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(SERVICE_ADDR)
        socket.send_json(payload)
        return socket.recv_json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_data(filename, data_dict):
    """
    Saves a single dictionary to the specified CSV file.
    If the file doesn't exist, the microservice creates it.
    """
    payload = {"command": "save", "filename": filename, "data": data_dict}
    return _send_request(payload)


def load_data(filename):
    """
    Retrieves all data from a CSV file as a list of dictionaries.
    """
    payload = {"command": "load", "filename": filename}
    response = _send_request(payload)
    return response.get("data", [])


def save_all_data(filename, data_list):
    """
    Overwrites the entire file with a new list of dictionaries.
    """
    payload = {"command": "save_all", "filename": filename, "data": data_list}
    return _send_request(payload)

def clear_all_data(filename):
    """
    Clears all data from the file by overwriting it with an empty list.
    """
    payload = {"command": "save_all", "filename": filename, "data": []}
    return _send_request(payload)