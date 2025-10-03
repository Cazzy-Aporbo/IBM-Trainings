"""
Learning to Calculate Scope 1 Fugitive Emissions

Practice calculating greenhouse gas emissions that escape from 
refrigeration and AC units. These are called "fugitive" emissions because 
they literally flee from where they're supposed to be contained.

Scope 1 emissions = Direct emissions YOU control (from sources you own)
"""

# First, let me import what I need. Each library has a specific purpose:
import requests  # This lets me talk to web APIs (think of it as an internet messenger)
import json      # JSON is how APIs prefer to exchange data (like a universal translator)
import configparser  # This safely reads secret credentials from a separate file

# Let me set up the configuration reader
# Think of this as creating a secure vault for API keys
config = configparser.ConfigParser()

# I'm reading credentials from a separate file - NEVER hardcode secrets!
# The path '../../auth/secrets.ini' means: go up 2 folders, then into 'auth' folder
config.read('../../auth/secrets.ini')

# Now let me extract credentials from the config file
# These are like your username and password for the emissions API
API_KEY = config['EI']['api.api_key']
CLIENT_ID = config['EI']['api.client_id']

# Step 1: Getting Permission to Use the API (Authentication)
# APIs are like secured buildings - you need a badge to get in
def get_auth_token():
    """
    This function is like getting a temporary visitor's badge.
    I exchange permanent credentials for a temporary token that expires.
    """
    
    # This is the "reception desk" where I get the badge
    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    
    # I'm preparing identification - showing who I am
    auth_headers = {
        "Content-Type": "application/json"  # Telling the API I speak JSON
    }
    
    # The credentials - like showing your ID at reception
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    # Making the request - this is walking up and asking for access
    print("Requesting authentication token...")
    response = requests.post(auth_url, headers=auth_headers, json=auth_data)
    
    # Check if I got the badge successfully
    if response.status_code == 200:
        token = response.json()['access_token']
        print("Authentication successful!")
        return token
    else:
        print(f"Authentication failed: {response.text}")
        return None

# Step 2: Create a Reusable Function to Call Any Emission API
def call_emission_api(endpoint, payload, token):
    """
    This is a universal API caller - like a phone that can call different departments.
    
    endpoint: which department (API endpoint) I'm calling
    payload: what information I'm sending
    token: security badge that proves I'm allowed to call
    """
    
    # The base address of the emissions API building
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    
    # Combining base URL with specific endpoint - like dialing an extension
    full_url = f"{base_url}/{endpoint}"
    
    # Preparing request headers - includes the security token
    headers = {
        "Authorization": f"Bearer {token}",  # Security badge
        "Content-Type": "application/json"   # How I'm formatting the message
    }
    
    # Making the actual API call
    print(f"Calling {endpoint} endpoint...")
    response = requests.post(full_url, headers=headers, json=payload)
    
    # Return the response so I can use it
    return response

# Step 3: Calculate Fugitive Emissions from Refrigeration
def calculate_fugitive_emissions(token):
    """
    Now for the main event - calculating emissions from AC/refrigeration leaks.
    These are gases that escape during normal operation or maintenance.
    """
    
    # This payload describes the refrigeration scenario
    # Think of it as filling out a form about your cooling equipment
    emission_payload = {
        "activity": {
            "activity_type": "fugitive_emission",  # Type of emission I'm calculating
            
            # Information about the refrigerant gas
            "gas": {
                "gas_type": "R-410A",  # Common AC refrigerant (each has different warming potential)
                "gas_amount": 2.5,      # How much leaked (in kg)
                "gas_unit": "kg"        # The unit of measurement
            },
            
            # Where is this equipment located?
            "location": {
                "country": "USA",       # Country affects emission factors
                "state": "California"   # Some states have specific regulations
            },
            
            # What equipment is leaking?
            "equipment": {
                "equipment_type": "commercial_ac",  # Type of cooling equipment
                "capacity": 10,                     # Cooling capacity (tons)
                "age_years": 5                      # Older equipment may leak more
            }
        },
        
        # Request configuration
        "response_format": {
            "emission_unit": "kg_co2e",  # I want results in CO2 equivalent
            "include_details": True       # Give me the calculation breakdown
        }
    }
    
    # Call the API with refrigerant leak data
    response = call_emission_api("fugitive", emission_payload, token)
    
    # Process the response
    if response.status_code == 200:
        results = response.json()
        
        # Display the results in a human-readable way
        print("\nFUGITIVE EMISSION CALCULATION RESULTS")
        print("=" * 45)
        
        emissions = results.get('emissions', {})
        print(f"Total CO2 Equivalent: {emissions.get('total_co2e', 0):.2f} kg")
        print(f"Calculation Method: {emissions.get('method', 'Unknown')}")
        
        # If I got detailed breakdown, show it
        if 'breakdown' in emissions:
            print("\nDetailed Breakdown:")
            for item, value in emissions['breakdown'].items():
                print(f"  - {item}: {value}")
        
        # Understanding Global Warming Potential (GWP)
        if 'gwp_factor' in emissions:
            print(f"\nGlobal Warming Potential of {emission_payload['activity']['gas']['gas_type']}: {emissions['gwp_factor']}")
            print("  (This means 1kg of this gas warms the planet as much as")
            print(f"   {emissions['gwp_factor']}kg of CO2)")
        
        return results
    else:
        print(f"Calculation failed: {response.text}")
        return None

# Step 4: Main Execution - Bringing It All Together
def main():
    """
    This is where I orchestrate everything I've learned.
    Think of it as the conductor leading the orchestra.
    """
    
    print("Starting Scope 1 Fugitive Emissions Calculator")
    print("-" * 50)
    
    # Step 1: Get authenticated
    token = get_auth_token()
    
    if not token:
        print("Unable to proceed without authentication")
        return
    
    # Step 2: Calculate emissions
    print("\nCalculating fugitive emissions from refrigerant leaks...")
    results = calculate_fugitive_emissions(token)
    
    # Step 3: What can I learn from this?
    if results:
        print("\nWHAT THIS MEANS:")
        print("-" * 30)
        print("- Fugitive emissions are often overlooked but can be significant")
        print("- Different refrigerants have vastly different warming potentials")
        print("- Regular maintenance reduces leaks and emissions")
        print("- This is Scope 1 because YOU own the equipment")
        
        # Practical next steps
        print("\nACTION ITEMS:")
        print("1. Schedule regular leak inspections")
        print("2. Consider switching to low-GWP refrigerants")
        print("3. Track these emissions in your sustainability reports")

# This is Python's way of saying "if someone runs this file directly, execute main()"
# It prevents the code from running if this file is imported elsewhere
if __name__ == "__main__":
    main()

"""
Before running this script, create your secrets.ini file:

[EI]
api.api_key = your_actual_api_key_here
api.client_id = your_actual_client_id_here

Save it in: ../../auth/secrets.ini (or adjust the path in line 20)

To run: python fugitive_emissions_calculator.py
"""
