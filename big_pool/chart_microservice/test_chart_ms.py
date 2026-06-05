import zmq
import base64


def run_test():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5580")

    test_data = [
        {"department": "HR", "amount": 150.50, "date": "2026-06-01"},
        {"department": "IT", "amount": 200.75, "date": "2026-06-01"},
        {"department": "HR", "amount": 50.25, "date": "2026-06-02"},
    ]

    payload = {
        "data": test_data,
        "calc_mode": "sum",
        "label_key": "department",
        "x_label": "Office Department",
        "y_label": "Total Dollars",
        "title": "June Spending by Dept",
        "bar_color": "#89CFF0",
    }

    print("Sending test request...")
    socket.send_json(payload)
    response = socket.recv_json()

    if response.get("status") == 200:
        print("Success! Saving chart...")
        with open("test_chart.png", "wb") as f:
            f.write(base64.b64decode(response["image"]))
        print("Chart saved as 'test_chart.png'")
    else:
        print(f"Error: {response.get('error')}")

    socket.close()


if __name__ == "__main__":
    run_test()
