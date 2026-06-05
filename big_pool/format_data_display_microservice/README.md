# Display Table Microservice

Accepts a JSON payload containing table data and terminal info, and returns a formatted unicode table as a string. The client can just print the response — no extra dependencies needed on their end.

Built with **Rich** for table rendering. Rich handles column sizing and truncation automatically based on the terminal width you send.

---

## Running the service
1. Create a venv (if not already) and activate it
2. From the project root, install deps: pip install -r "big pool/format_data_display_microservice/requirements.txt"
3. Start the microservice, the service binds to port 5565 and waits for requests:

```
python "big pool/format_data_display_microservice/display_table.py"
```

---

## Request format

Send a JSON object with the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| width | int | yes | Terminal width of the calling program |
| limit | int | yes | Max number of rows to display |
| data | list of dicts | yes | The table data, where keys are column headers |
| format_headers | bool | no | If true, converts snake_case headers to Title Case |

### Example:

**note: the below spins up a subprocess. You can also manually start the MS in a dedicated terminal as seen above**
```python
import zmq, os, sys, subprocess, time

# spin up the service
service = subprocess.Popen(
    [sys.executable, r"big pool\format_data_display_microservice\display_table.py"]
)
time.sleep(1)

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5565")

socket.send_json({
    "width": os.get_terminal_size().columns,
    "limit": 10,
    "data": [
        {"first_name": "Tre",   "last_name": "Wenger",  "age": 25},
        {"first_name": "Amari", "last_name": "Jones",   "age": 23},
    ],
    "format_headers": True
})

response = socket.recv_json()
print(response["data"])

# shut down the service when done
socket.send_string("Q")
socket.recv()
service.wait()
```

---

## Response format

```json
{
    "status": 200,
    "message": "Successfully built the table",
    "data": "<formatted table string>"
}
```

- If validation fails (bad width, limit, or data), status will be **400** and **message** will contain the error description.
- If an internal error occurs, status will be **500** and **message** will contain the exception detail.

