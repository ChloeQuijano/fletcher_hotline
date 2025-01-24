from flask import Flask, request, Response, jsonify, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

app = Flask(__name__)

# Twilio Credentials
ACCOUNT_SID = "xx"
AUTH_TOKEN = "xx
TWILIO_PHONE_NUMBER = "xx"


# Store user sessions for context (you may use a database or a cache in production)
user_sessions = {}

@app.route("/sms", methods=["POST"])
def sms_reply():
    # Extract the message sent by the user
    user_message = request.form.get("Body", "").strip()
    user_phone = request.form.get("From")  # Get the sender's phone number for session handling
    
    # Create a Twilio response object
    twiml = MessagingResponse()

    # Check if the user has an active session
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"step": None, "data": {}}
    
    session = user_sessions[user_phone]

    # Process the user's input
    if session["step"] is None and user_message.lower() == "start":
        twiml.message(
            "Welcome to the Natural Disaster Hotline! Reply with:\n"
            "TRACK - to receive disaster alerts for your location.\n"
            "VIEW - to view a map of ongoing disasters.\n"
            "REPORT - to report a disaster."
        )
        session["step"] = "started"
    
    elif session["step"] == "started" and user_message.lower() == "report":
        twiml.message(
            "Please share your location. You can:\n"
            "- Reply with your location as text (e.g., '123 Main St, City').\n"
            "- Or click here to select your location on a map: https://your-domain.com/select-location"
        )
        session["step"] = "awaiting_location"

    elif session["step"] == "awaiting_location":
        # Save the location to the session data
        session["data"]["location"] = user_message
        session["data"]["timestamp"] = datetime.now().isoformat()
        twiml.message(
            "Got it! Now, please specify the type of disaster (e.g., 'Flood', 'Earthquake', 'Fire')."
        )
        session["step"] = "awaiting_disaster_type"

    elif session["step"] == "awaiting_disaster_type":
        # Save the disaster type to the session data
        session["data"]["disaster_type"] = user_message
        twiml.message(
            "Thank you for reporting! Here are the details you provided:\n"
            f"Location: {session['data']['location']}\n"
            f"Disaster Type: {session['data']['disaster_type']}\n"
            f"Timestamp: {session['data']['timestamp']}\n"
            "We will take it from here. Stay safe!"
        )
        # Reset the session or store the data to a database
        save_report(session["data"])
        session["step"] = None
        session["data"] = {}

    else:
        twiml.message(
            "Invalid input. Please type START to begin or reply with 'REPORT' to report a disaster."
        )

    return str(twiml)


@app.route("/save-location", methods=["POST"])
def save_location():
    # Handle location submission from the map
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({"error": "Invalid data"}), 400

    # You can log the location or save it to your database here
    print(f"Location received: Latitude {latitude}, Longitude {longitude}")

    return jsonify({"message": "Location saved successfully!"}), 200


@app.route("/select-location")
def select_location():
    # Serve the map page
    return send_from_directory("static", "index.html")


def save_report(data):
    # Mock function to save the report
    # Replace this with actual database or API integration
    print("Saving report:", data)


if __name__ == "__main__":
    app.run(debug=True)