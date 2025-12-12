
# api.py
from flask import Flask, jsonify
from processing_and_model import generate_smart_exits

app = Flask(__name__)
FCD_FILE = "data/riyadh_fcd.xml"

@app.route("/")
def home():
    return "Smart Exits API is running!"

@app.route("/api/smart_exits")
def smart_exits():
    results = generate_smart_exits(FCD_FILE)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
