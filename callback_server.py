from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    print("=" * 60)
    print("M-PESA CALLBACK RECEIVED")
    print(json.dumps(data, indent=2))
    print("=" * 60)
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

@app.route("/", methods=["GET"])
def home():
    return "ABAWERA INVESTOR callback server is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
