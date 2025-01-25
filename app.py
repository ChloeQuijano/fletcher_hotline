from flask import Flask, request, jsonify, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import requests
import csv
import os
app = Flask(__name__)

# Twilio and Google Maps API Credentials
# ACCOUNT_SID = "ACded8c8e442fec247d27ac634e642b5bc"
# AUTH_TOKEN = "036b4133f3d6a7cb1811e2afa5c061ba"
# TWILIO_PHONE_NUMBER = "+15179958321"
# GOOGLE_MAPS_API_KEY = "AIzaSyDJq8FL95iPyZ-j8A3KICQGo4awuADWNUs"

ACCOUNT_SID = "ACc08851291881bbf6b6f7fc06a9e7bcc3"
AUTH_TOKEN = "5270932520fdd7c878a4f5f2b780b9e4"
TWILIO_PHONE_NUMBER = "+19363565178"
GOOGLE_MAPS_API_KEY = "AIzaSyDJq8FL95iPyZ-j8A3KICQGo4awuADWNUs"

# Store user sessions for context
user_sessions = {}


# Store user sessions for context
user_sessions = {}

lat = 0
lng = 0
report = ""


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

    # MAIN pipeline: handle start and user options
    if session["pipeline"] is None and user_message == "start":
        twiml.message(
            "Welcome to the Natural Disaster Hotline! Please reply with:\n"
            "- TRACK: Receive disaster alerts for your location.\n"
            "- VIEW: View a map of ongoing disasters.\n"
            "- REPORT: Report a disaster."
        )
        session["pipeline"] = "main"
        session["step"] = "prompt"

    elif session["pipeline"] == "main":
        if user_message == "track":
            session["pipeline"] = "track"
            session["step"] = "awaiting_location"
            twiml.message(
                "TRACK selected. Please share your location:\n"
                "- Reply with your location as text (e.g., '123 Main St, City').\n"
                "- Or click here to select your location: https://your-domain.com/select-location"
            )
        elif user_message == "report":
            session["pipeline"] = "report"
            session["step"] = "awaiting_location"
            twiml.message(
                "REPORT selected. Please share your location:\n"
                "- Reply with your location as text (e.g., '123 Main St, City').\n"
                "- Or click here to select your location: https://your-domain.com/select-location"
            )
        elif user_message == "view":
            session["pipeline"] = "view"
            session["step"] = "view_map"
            twiml.message(
                "VIEW selected. Visit the following link to view a map of ongoing disasters:\n"
                "https://your-domain.com/map"
            )
            reset_session(session)
        else:
            twiml.message("Invalid input. Please reply with TRACK, VIEW, or REPORT.")

    # TRACK pipeline
    elif session["pipeline"] == "track" and session["step"] == "awaiting_location":
        # if validate_location(user_message):
        
            session["data"]["location"] = user_message
            twiml.message(
                f"Thank you! You will now receive alerts for disasters near {user_message}."
            )
            save_tracking_location(session["data"]["location"])
            reset_session(session)
            
            lat, lng = get_coordinates(user_message)
            session['data']['latitude'] = lat
            session['data']['longitude'] = lng
            
            print('lat', lat)
            print('lng', lng)


            # get_coordinates()
        # else:
        #     twiml.message("Invalid address. Please send a valid address.")

    # REPORT pipeline
    elif session["pipeline"] == "report" and session["step"] == "awaiting_location":
        # if validate_location(user_message):
            session["data"]["location"] = user_message
            session["step"] = "awaiting_disaster_type"
            twiml.message(
                "Thank you! Now, please specify the type of disaster (e.g., Flood, Earthquake, Fire)."
            )
        # else:
        #     twiml.message("Invalid address. Please send a valid address.")
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
        
        data = [lat, lng, report]
        save_report(data, "data")
        
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



def validate_location(address):
    """
    Validates if the given address can be geocoded using the Google Maps Geocoding API.

    Args:
        address (str): The address to be validated.

    Returns:
        bool: True if the address can be geocoded successfully, False otherwise.
    """
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    
    # try:
    response = requests.get(geocode_url)
    geocode_data = response.json()

    print(geocode_data)
    #     # Debugging: Print the API response
    #     print("Google Maps API Response:", geocode_data)

    #     # Check if the API response status is 'OK' and results are non-empty
    #     if geocode_data.get("status") == "OK" and geocode_data.get("results"):
    #         return True
    #     else:
    #         return False
    # except Exception as e:
    #     print(f"Error validating address: {e}")
    #     return False


def get_coordinates(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(geocode_url)
    geocode_data = response.json()
    
    if geocode_data['status'] == 'OK':
        location = geocode_data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise ValueError(f"Error from Geocoding API: {geocode_data['status']}")

def save_tracking_location(location):
    # Mock function to save a tracking location
    print(f"Tracking location saved: {location}")



def save_to_csv(data, filename='data.csv'):
    # Define the CSV file headers
    headers = ['lat', 'long', 'latitude', "report_desc"]
    
    # Check if the file exists
    file_exists = os.path.isfile(filename)
    
    # Open the CSV file in append mode
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write the headers if the file does not exist
        if not file_exists:
            writer.writeheader()
        
        # Write the data
        writer.writerow(data)

def save_report(data):
    # Mock function to save a report
    print(f"Report saved: {data}")
    save_to_csv(data)

def reset_session(session):
    # Reset user session
    session["pipeline"] = None
    session["step"] = None
    session["data"] = {}


if __name__== "__main__":
    app.run(debug=True)