import zmq
import csv
import os


def handle_save(socket, fname, payload):
    """
    Checks datatype, calls save_to_csv, and sends message back to calling program
    :param socket
    :param fname: string
    :param payload: dictionary
    :return: None
    """
    if not isinstance(payload, dict):
        raise ValueError("Data for 'save' must be a dictionary.")
    save_to_csv(fname, payload)
    print("Sending Save Response")
    socket.send_json({"status": "success"})


def handle_load(socket, fname):
    """
    Handles loading file from csv, sends message back to calling program
    :param socket
    :param fname: as string
    :return None
    """
    records = load_from_csv(fname)
    print("Sending Load Response")
    socket.send_json({"status": "success", "data": records})


def handle_save_all(socket, fname, payload):
    """
    Checks datatype, calls overwrite_csv, and sends message back to calling program
    :param socket
    :param fname: as string
    :param payload: as list of dicts
    :return: None
    """
    if not isinstance(payload, list):
        raise ValueError("Data for 'save_all' must be a list of dictionaries.")
    overwrite_csv(fname, payload)
    print("Sending SaveAll Response")
    socket.send_json({"status": "success"})


def load_from_csv(filename):
    """
    Reads a CSV file and converts it into a list of dictionaries.
    If the file does not exist, returns an empty list.
    Receives: filename as string
    Returns: list of dictionaries
    """
    if not os.path.exists(filename):
        return []
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        # DictReader uses the first row of the CSV as keys for the dictionaries
        return list(csv.DictReader(file))


def save_to_csv(filename, data_dict):
    """
    Appends a single dictionary as a new row in the specified CSV file.
    Automatically creates the file and writes headers if it doesn't exist.
    Receives: filename as string
              data_dict as dictionary
    Returns: None. File is modified/saved.
    """
    file_exists = os.path.isfile(filename)
    headers = list(data_dict.keys())

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        # Write the header only if creating a brand new file
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_dict)


def overwrite_csv(filename, data_list):
    """
    Overwrites an entire CSV file with a new list of dictionaries.
    Used for bulk updates like deleting or editing records.
    Receives: filename as string
              data_list as list of dictionaries
    Returns: None. Modifies target file.
    """
    # If the list is empty, delete the file to keep folder clean
    if not data_list:
        if os.path.exists(filename):
            os.remove(filename)
        return

    # Extract headers from the first dictionary in the list
    headers = list(data_list[0].keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_list)


def start_service():
    """
    Main loop that listens for ZeroMQ messages and routes them to
    the appropriate file-handling functions based on the 'command'.
    Receives: None
    Returns: None
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    print("--- Storage Microservice Active (Port 5555) ---")

    while True:
        print("\nWaiting for request...")
        request = socket.recv_json()
        print("Request received")

        # Parameters from the request payload
        cmd = request.get("command")
        fname = request.get("filename")
        payload = request.get("data")

        try:
            # Route based on the command
            if cmd == "save":
                handle_save(socket, fname, payload)

            elif cmd == "load":
                handle_load(socket, fname)

            elif cmd == "save_all":
                handle_save_all(socket, fname, payload)

            else:
                print("Sending Error Response")
                socket.send_json({"status": "error", "message": "Unknown command"})

        except Exception as e:
            print(f"Error processing request: {e}")
            socket.send_json(
                {"status": "error", "message": f"Microservice Error: {str(e)}"}
            )


if __name__ == "__main__":
    start_service()
