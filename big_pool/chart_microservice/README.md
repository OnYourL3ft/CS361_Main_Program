**Description:**

The chart microservice handles visualizing data by generating a graphical representation (bar chart) based on the user's dataset. It aggregates data from a user-specified column (e.g. "department") by either counting the number or summing the amounts. It then returns a Base64 encoded image back to the client. The service operates as a decoupled background process to ensure the main application remains responsive. 
<br>
<br>
**Architecture and Communication:**

The chart microservice implements a decoupled client-server model using a ZMQ Reuest-Reply pattern. External applications communicate with this service by packing data and configuration parameters into a structured JSON payload, opening a temporary ZMQ socket (REQ), transmitting the payload across the network, and blocking until the microservice returns a Base64 string of the generated chart.
<br>

**Port:** tcp://localhost:5580
<br>

**Setup:**
1. Install the required dependencies

       pip install pyzmq matplotlib

2. Place the microservice in your project directory
3. Start the microservice in a separate terminal to keep it listening for incoming requests

       python chart_microservice.py
<br>

**Implementation:**
In your application file, establish a ZeroMQ REQ socket connection pointing to port 5580. 
<br>
To generate a chart, construct a JSON payload with your dataset, the specific key to analyze, and your preferred calculation (sum or count).

    Example:
    import zmq
    import json
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5580")
    
    data = [
        {"department": "HR", "amount": 150.50, "date": "2026-06-01"},
        {"department": "IT", "amount": 200.75, "date": "2026-06-01"}
    ]
    
    payload = {
        "data": data,
        "calc_mode": "sum",       
        "label_key": "department", 
        "bar_color": "#89CFF0",   
        "x_label": "Department",
        "y_label": "Total Dollars ($)",
        "title": "June Spending by Dept"
    }
    
    socket.send_json(payload)
    response = socket.recv_json()
    
    if response.get("status") == 200:
        chart_image_b64 = response.get("image")
<br>

**Parameters:**
To communicate with the microservice, the JSON payload must include the following:

    data (list) -- List of dictionary objects containing the records
    label_key (string) -- The dictionary key/column header to group by
    calc_mode (string) -- Mode of aggregation: "count" or "sum"
    bar_color (string) -- Hex color code or name for the bars
    x_label (string) -- Label for the x-axis
    y_label(string) -- Label for the y-axis
    title (string) -- Chart title
<br>

**Response Format:**

Successful Requests:

    {"status": 200, "image": "iVBORw0KGgoAAAANSUhEUgA..."}

Errors:

    {"status": 500, "error": "Description of validation or processing error."}


