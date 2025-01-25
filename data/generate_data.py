import csv
import random

# Function to generate random latitude and longitude
def generate_lat_long():
    latitude = random.uniform(40, 80)
    longitude = random.uniform(50, 140)
    return latitude, longitude

# Function to generate random description
def generate_description():
    descriptions = ["Earthquake", "Fire", "Other"]
    return random.choice(descriptions)

# Generate dummy data
def generate_dummy_data(num_records):
    data = []
    for _ in range(num_records):
        latitude, longitude = generate_lat_long()
        description = generate_description()
        data.append([latitude, longitude, description])
    return data

# Save data to CSV file
def save_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Latitude", "Longitude", "Description"])
        writer.writerows(data)

# Main function
if __name__ == "__main__":
    num_records = 100  # Number of dummy records to generate
    data = generate_dummy_data(num_records)
    save_to_csv(data, 'disasters.csv')