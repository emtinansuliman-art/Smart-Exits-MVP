from flask import Flask, jsonify, render_template
import json

app = Flask(__name__, template_folder="templates")

app.config["JSON_AS_ASCII"] = False

# Load the real MVP JSON file
with open("mvp_smart_exits_real.json", "r", encoding="utf-8") as f:
    smart_exits_data = json.load(f)

@app.route("/")
def home():
    return "Smart Exits API is running!"

@app.route("/api/smart_exits")
def smart_exits():
    return jsonify(smart_exits_data), 200


# ----------- UI Pages -------------

@app.route("/traffic")
def traffic_page():
    return render_template("traffic.html")

@app.route("/driver")
def driver_page():
    return render_template("driver.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
