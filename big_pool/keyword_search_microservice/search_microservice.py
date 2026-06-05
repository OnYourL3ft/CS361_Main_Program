import zmq
import json


def search_by_keyword(data_list, keyword, key):
    """
    Safely stringifies target values to allow partial substring matches.
    """
    if not keyword:
        return data_list

    keyword = str(keyword).lower()

    return [item for item in data_list if keyword in str(item.get(key, "")).lower()]


def validate_payload(payload):
    """
    Checks the incoming payload for required structures.
    Returns a tuple: (is_valid: bool, error_message: str)
    """
    if payload.get("command") != "find":
        return False, "Invalid command. Expected 'find'."

    if "key" not in payload or "dataset" not in payload:
        return False, "Missing required structural parameters ('key' or 'dataset')."

    if not isinstance(payload["dataset"], list):
        return False, "Dataset must be structured as a list of dictionaries."

    return True, ""


def process_search_request(payload):
    """
    Routes a valid payload to the search algorithm and formats the success response.
    """
    target_key = payload["key"]
    keyword_query = payload.get("keyword", "")
    dataset_to_filter = payload["dataset"]

    filtered_results = search_by_keyword(dataset_to_filter, keyword_query, target_key)

    return {"status": "success", "results": filtered_results}


def handle_incoming_message(message_string):
    """
    Parses the raw JSON, checks validation, handles errors, and returns the final dictionary.
    """
    try:
        payload = json.loads(message_string)
        is_valid, error_msg = validate_payload(payload)

        if not is_valid:
            return {"status": "error", "message": error_msg}

        return process_search_request(payload)

    except json.JSONDecodeError:
        return {"status": "error", "message": "Request must be valid JSON."}
    except Exception as e:
        return {"status": "error", "message": f"Internal microservice error: {str(e)}"}


def main():
    """
    Initializes the ZeroMQ server and runs the infinite listening loop.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5552")

    print("--- Keyword Search Microservice Active (Port 5552) ---")

    while True:
        raw_message = socket.recv_string()

        response_dict = handle_incoming_message(raw_message)

        socket.send_string(json.dumps(response_dict))


if __name__ == "__main__":
    main()
