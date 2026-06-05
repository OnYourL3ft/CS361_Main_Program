import zmq, json
from io import StringIO
from rich.console import Console 
from rich.table import Table

# ---------------------------------------------------------------------
# Set up spike protocol
# Create environment, initialize socket, listen for request from client
# ---------------------------------------------------------------------
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5565")
    
def validate(width:int, limit:int, data:list[dict]=[{}]) -> str:
    """ Helper function that validates the input fields and returns a status message """
    # validate width arg
    try:
        if not width:
            raise ValueError
        width = int(width)
    except Exception:
        return "Error: width must be a valid integer"
    
    # validate limit arg
    try:
        if not limit:
            raise ValueError
        limit = int(limit)
    except Exception:
        return "Error: limit must be a valid integer"
    
    # validate data arg
    try:
        if not data or not data[0]:
            raise ValueError
        if type(data) != list:
            raise ValueError
        if type(data[0]) != dict:
            raise ValueError
    except Exception:
        return "Error: data must be a list of objects with at least 1 row"
    
    return "Success, the data is valid"

def build_table(width:int, limit:int, data:list[dict]=[{}], format_headers:bool=False) -> str:
    """
    builds the table and parses the output into a string for stdout redirection.
    Leverages column truncation and unicode table display provided by the Rich libary,
    then returns the output as a string instead of displaying it in the terminal directly.
        width: current width of the caller's terminal interface window
        limit: the row limit to be displayed of the data
        data: a list of dictionary objects formatted as {col_header:value, ...}
        format_headers: converts snake_case column headers to title case with spaces (optional)
    """
    # validate input
    validate_res = validate(width, limit, data)
    if "error" in validate_res.lower():
        return validate_res

    # build rich table. expand=True + no_wrap lets Rich fit and truncate columns to width
    table = Table(expand=True, show_lines=True)
    for col in data[0].keys():
        # optionally format the column headers
        header = col.replace("_", " ").title() if format_headers else col
        # add the rich table column
        table.add_column(header, no_wrap=True)
    for row in data[:limit]:
        # add the rich table row
        table.add_row(*[str(row[col]) for col in data[0].keys()])

    # capture rich output as a plain string and return it instead of displaying in terminal
    output = StringIO()
    console = Console(file=output, width=width)
    console.print(table)
    return output.getvalue()

# run until client program quits
while True:
    ### the calling program will need to send os data about the current state of the terminal (size)
    print("Waiting for request...")
    message = socket.recv()
    print("Received request:")

    # quit microservice running, close socket, break
    if message.decode() == "Q":
        socket.send_string("Table microservice shutting down.")
        break

    # parse the response
    configs = json.loads(message.decode())
    width = configs["width"]
    row_limit = configs["limit"]
    data = configs["data"]
    format_headers = configs.get("format_headers", False)

    # build the string to be printed by the caller
    try:
        io_string = build_table(width, row_limit, data, format_headers)
        if io_string.startswith("Error:"):
            response = {"status": 400, "message": io_string, "data": ""}
        else:
            response = {"status": 200, "message": "Successfully built the table", "data": io_string}
    except Exception as e:
        response = {"status": 500, "message": f"Internal server error: {e}", "data": ""}

    # return email confirmation message to client
    socket.send_json(response)

# close connection and clean up environment on exit
context.destroy()