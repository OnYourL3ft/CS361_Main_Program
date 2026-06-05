import sys
import zmq

TEST_FILE = "test_data.csv"


def send_raw_request(socket, payload):
    socket.send_json(payload)
    try:
        return socket.recv_json()
    except zmq.error.Again:
        print("Response: FAILED")
        sys.exit(1)


def run_direct_tests():
    print("=== Starting Microservice Integration Tests ===")
    print(f"Target File: {TEST_FILE}\n")

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 2000)
    socket.connect("tcp://localhost:5555")

    # test 1
    print("--- Test 1: Clearing existing data ---")
    response = send_raw_request(
        socket, {"command": "save_all", "filename": TEST_FILE, "data": []}
    )
    print(f"Response: {response}")

    # test 2
    print("\n--- Test 2: Saving a single record ---")
    user_1 = {"id": "1", "name": "Alice", "role": "Admin"}
    response = send_raw_request(
        socket, {"command": "save", "filename": TEST_FILE, "data": user_1}
    )
    print(f"Response: {response}")

    # test 3
    print("\n--- Test 3: Loading records ---")
    response = send_raw_request(socket, {"command": "load", "filename": TEST_FILE})
    data = response.get("data", [])
    print(f"Loaded Data: {data}")
    if len(data) == 1 and data[0].get("name") == "Alice":
        print("-> SUCCESS: Single record verified.")
    else:
        print("-> FAILED: Record mismatch.")

    # test 4
    print("\n--- Test 4: Overwriting with multiple records ---")
    bulk_users = [
        {"id": "2", "name": "Bob", "role": "User"},
        {"id": "3", "name": "Charlie", "role": "Moderator"},
    ]
    response = send_raw_request(
        socket,
        {"command": "save_all", "filename": TEST_FILE, "data": bulk_users},
    )
    print(f"Response: {response}")

    # test 5
    print("\n--- Test 5: Loading records after overwrite ---")
    response = send_raw_request(socket, {"command": "load", "filename": TEST_FILE})
    data = response.get("data", [])
    print(f"Loaded Data: {data}")
    if len(data) == 2 and data[0].get("name") == "Bob":
        print("-> SUCCESS: Overwrite verified.")
    else:
        print("-> FAILED: Overwrite mismatch.")

    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    run_direct_tests()
