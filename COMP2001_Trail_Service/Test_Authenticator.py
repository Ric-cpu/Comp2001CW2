import requests

# Authentication details
auth_url = 'https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users'
email = 'tim@plymouth.ac.uk'
password = 'COMP2001!'

credentials = {
    'email': email,
    'password': password
}

# Authenticate
response = requests.post(auth_url, json=credentials)
if response.status_code == 200:
    token = response.json().get('token')  # Extract token
    print("Authenticated successfully, token:", token)

    # Use the token to access your API
    headers = {'Authorization': f'Bearer {token}'}
    api_url = 'http://localhost:8000/trails'

    # Fetch trails
    api_response = requests.get(api_url, headers=headers)
    if api_response.status_code == 200:
        print("Trails fetched successfully:", api_response.json())
    else:
        print(f"Failed to fetch trails: {api_response.status_code}")
        print(api_response.text)
else:
    print(f"Authentication failed: {response.status_code}")
    print(response.text)
