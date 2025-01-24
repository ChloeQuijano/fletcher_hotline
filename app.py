from flask import Flask, request, Response, jsonify, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

app = Flask(__name__)

# Twilio Credentials
ACCOUNT_SID = "ACded8c8e442fec247d27ac634e642b5bc"
AUTH_TOKEN = "036b4133f3d6a7cb1811e2afa5c061ba"
TWILIO_PHONE_NUMBER = "+15179958321"


# Store user sessions for context (replace with a database in production)
user_sessions = {}

@app.route("/sms", methods=["POST"])
def sms_reply():
    # Extract user input and phone number
    user_message = request.form.get("Body", "").strip().lower()
    user_phone = request.form.get("From")
    
    # Create a Twilio response object
    twiml = MessagingResponse()

    # Initialize user session if not already active
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"pipeline": None, "step": None, "data": {}}
    
    session = user_sessions[user_phone]

    # Handle the START command
    if session["pipeline"] is None and user_message == "start":
        twiml.message(
            "Welcome to the Natural Disaster Hotline! Please reply with:\n"
            "- TRACK: Receive disaster alerts for your location.\n"
            "- VIEW: View a map of ongoing disasters.\n"
            "- REPORT: Report a disaster."
        )
        session["pipeline"] = "main"
        session["step"] = "prompt"

    # Handle the TRACK pipeline
    elif session["pipeline"] == "main" and user_message == "track":
        twiml.message(
            "TRACK selected. Please share your location:\n"
            "- Reply with your location as text (e.g., '123 Main St, City').\n"
            "- Or click here to select your location: https://your-domain.com/select-location"
        )
        session["pipeline"] = "track"
        session["step"] = "awaiting_location"

    elif session["pipeline"] == "track" and session["step"] == "awaiting_location":
        session["data"]["location"] = user_message
        twiml.message(
            f"Thank you! You will receive alerts for disasters near {user_message}."
        )
        save_tracking_location(session["data"]["location"])
        reset_session(session)

    # Handle the REPORT pipeline
    elif session["pipeline"] == "main" and user_message == "report":
        twiml.message(
            "REPORT selected. Please share your location:\n"
            "- Reply with your location as text (e.g., '123 Main St, City').\n"
            "- Or click here to select your location: https://your-domain.com/select-location"
        )
        session["pipeline"] = "report"
        session["step"] = "awaiting_location"

    elif session["pipeline"] == "report" and session["step"] == "awaiting_location":
        session["data"]["location"] = user_message
        twiml.message(
            "Thank you! Now, please specify the type of disaster (e.g., Flood, Earthquake, Fire)."
        )
        session["step"] = "awaiting_disaster_type"

    elif session["pipeline"] == "report" and session["step"] == "awaiting_disaster_type":
        session["data"]["disaster_type"] = user_message
        session["data"]["timestamp"] = datetime.now().isoformat()
        twiml.message(
            "Thank you for reporting! Here are the details you provided:\n"
            f"Location: {session['data']['location']}\n"
            f"Disaster Type: {session['data']['disaster_type']}\n"
            f"Timestamp: {session['data']['timestamp']}\n"
            "We will take it from here. Stay safe!"
        )
        save_report(session["data"])
        reset_session(session)

    # Handle the VIEW pipeline
    elif session["pipeline"] == "main" and user_message == "view":
        twiml.message(
            "VIEW selected. Visit the following link to view a map of ongoing disasters:\n"
            "https://your-domain.com/map"
        )
        reset_session(session)

    else:
        twiml.message("Invalid input. Reply with START to begin.")

    return str(twiml)


@app.route("/save-location", methods=["POST"])
def save_location():
    # Handle location submission from the map
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        return jsonify({"error": "Invalid data"}), 400

    print(f"Location received: Latitude {latitude}, Longitude {longitude}")
    return jsonify({"message": "Location saved successfully!"}), 200


@app.route("/select-location")
def select_location():
    # Serve the map selection page
    return send_from_directory("static", "index.html")


def save_tracking_location(location):
    # Mock function to save a tracking location
    print(f"Tracking location saved: {location}")


def save_report(data):
    # Mock function to save a report
    print(f"Report saved: {data}")


def reset_session(session):
    # Reset user session
    session["pipeline"] = None
    session["step"] = None
    session["data"] = {}


if __name__ == "__main__":
    app.run(debug=True)