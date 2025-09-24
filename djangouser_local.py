import requests, sys, os

def search_users(query):
    """
    Search for users via the API

    Args:
        query (str): The search term

    Returns:
        list: Search results from the API
    """
    # Read the API key
    API_KEY = os.environ.get('API_KEY')
    if not API_KEY:
        try:
            with open('/Users/jelambeadmin/soft/access_django_user_admin/API_KEY', "r") as key_file:
                API_KEY = key_file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading API key: {str(e)}")

    # The base URL for the API
    base_url = "https://allocations-api.access-ci.org/acdb/userinfo/v2/people/search"

    # Query parameters
    params = {"q": query}

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

        # Return the JSON response
        return response.json()

    except requests.exceptions.HTTPError as err:
        raise Exception(f"HTTP Error occurred: {err}")
    except requests.exceptions.ConnectionError:
        raise Exception("Error connecting to the API. Please check your internet connection.")
    except requests.exceptions.Timeout:
        raise Exception("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as err:
        raise Exception(f"An error occurred: {err}")
    except ValueError:
        raise Exception("Could not parse the JSON response.")

# This allows the script to be run directly
if __name__ == "__main__":
    search_name = input("Enter the name for which you want to query: ")
    try:
        results = search_users(search_name)
        print("\nSearch Results:")
        print(results)
    except Exception as e:
        print(f"UNKNOWN: {str(e)}")
        sys.exit(3)
