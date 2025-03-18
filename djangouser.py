import requests, sys

# Read the API key
try:
    with open('API_KEY', "r") as key_file:
        API_KEY = key_file.read().strip()
except Exception as e:
    print(f"UNKNOWN: Error reading API_KEY file: {str(e)}")
    sys.exit(3)

# The base URL for the API
base_url = " URL HERE "

# Query string
search_name = input("Enter the name for which you want to query: ")

# Query parameters
params = {"q": search_name}

# Set up the required headers for authentication and routing
headers = {
    "XA-RESOURCE": "operations.django",
    "XA-AGENT": "userinfo",
    "XA-API-KEY": API_KEY
}

# Make the API request
try:
    response = requests.get(base_url, params=params, headers=headers)

    # Check if the request was successful
    response.raise_for_status()

    # Print the response data
    print("\nSearch Results:")
    print(response.json())

except requests.exceptions.HTTPError as err:
    print(f"HTTP Error occurred: {err}")
except requests.exceptions.ConnectionError:
    print("Error connecting to the API. Please check your internet connection.")
except requests.exceptions.Timeout:
    print("The request timed out. Please try again later.")
except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")
except ValueError:
    print("Could not parse the JSON response.")
