from flask import Flask, render_template, request, jsonify
from fact_checker.analyzer import agent
import traceback

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analysis():
    data = request.get_json()

    if not data or "topic" not in data:
        return jsonify({"error": "Missing 'topic' in request body."}), 400

    topic = data["topic"].strip()

    if not topic:
        return jsonify({"error": "Missing topic text."}), 400

    try:
        result = agent(topic)
        return jsonify(result), 200   # jsonify packages the info. in an apt manner for HTTP transfer.
    except Exception as e:
        # Log the full traceback to the console
        app.logger.error(f"An error occurred during analysis: {e}")
        app.logger.error(traceback.format_exc())
        # Return a generic error to the user
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
