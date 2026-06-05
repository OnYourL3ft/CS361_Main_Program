import zmq
import matplotlib.pyplot as plt
import io
import base64
import datetime

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5580")


def create_chart(data, x_label, y_label, title, calc_mode, bar_color, label_key):
    current_month = datetime.date.today().strftime("%Y-%m")
    category_totals = {}

    # process data based on calc_mode
    for entry in data:
        if entry.get("date", "").startswith(current_month):
            cat = entry.get(label_key, "Uncategorized")

            if calc_mode == "sum":
                try:
                    amt = float(entry.get("amount", 0))
                except ValueError:
                    amt = 0.0
                category_totals[cat] = category_totals.get(cat, 0.0) + amt
            else:
                category_totals[cat] = category_totals.get(cat, 0) + 1

    # create plot
    categories = list(category_totals.keys())
    totals = list(category_totals.values())

    plt.figure(figsize=(8, 5))

    plt.bar(categories, totals, color=bar_color)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    # only force whole numbers on the Y-axis if we are counting transactions, not summing money
    if calc_mode == "count" and totals:
        plt.yticks(range(0, int(max(totals)) + 2))

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return base64.b64encode(buf.read()).decode("utf-8")


print("--- Chart Microservice Active on Port 5580 ---")
while True:
    message = socket.recv_json()
    try:
        data = message.get("data", [])
        x_label = message.get("x_label", "Category")
        y_label = message.get("y_label", "Value")
        title = message.get(
            "title", f"Category Analysis ({datetime.date.today().strftime('%Y-%m')})"
        )

        calc_mode = message.get("calc_mode", "count")
        bar_color = message.get("bar_color", "blue")
        label_key = message.get("label_key", "category")

        # generate chart
        chart_b64 = create_chart(
            data, x_label, y_label, title, calc_mode, bar_color, label_key
        )
        socket.send_json({"status": 200, "image": chart_b64})
    except Exception as e:
        socket.send_json({"status": 500, "error": str(e)})
