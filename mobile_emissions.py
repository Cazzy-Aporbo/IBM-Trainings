"""
Learning to Calculate Scope 1 Mobile Emissions from Fleet Fuel
Calculate greenhouse gas emissions from vehicle fleets.
These are called "mobile emissions" because they come from moving sources
like cars, trucks, and delivery vehicles that burn fuel.

Mobile emissions are a major component of Scope 1 emissions for many organizations.
If you own the vehicles, the emissions from their fuel consumption are YOUR direct emissions.
"""

import requests  # For making HTTP requests to the emissions API
import json      # For handling JSON data format that APIs use
import configparser  # For safely reading API credentials from a config file

# Setting up the configuration reader to handle credentials securely
# Never put API keys directly in code - that's a security risk!
config = configparser.ConfigParser()

# Reading credentials from a separate file
# The path '../../auth/secrets.ini' navigates up two folders, then into 'auth'
config.read('../../auth/secrets.ini')

# Extracting the API credentials I'll need to authenticate
# Think of these as the keys to access the emissions calculation service
API_KEY = config['EI']['api.api_key']
CLIENT_ID = config['EI']['api.client_id']

# Step 1: Authentication - Getting Permission to Use the API
def get_auth_token():
    """
    Before I can calculate emissions, I need to prove I'm authorized.
    This function exchanges my permanent credentials for a temporary access token.
    It's like showing your driver's license to rent a car.
    """
    
    # The endpoint where I request authentication
    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    
    # Setting up the request headers - telling the API what format I'm using
    auth_headers = {
        "Content-Type": "application/json"  # I'm sending JSON-formatted data
    }
    
    # My credentials - proving who I am to the API
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    # Making the authentication request
    print("Requesting authentication token for emissions API...")
    response = requests.post(auth_url, headers=auth_headers, json=auth_data)
    
    # Checking if authentication was successful
    if response.status_code == 200:
        # Extract the token from the response
        token = response.json()['access_token']
        print("Authentication successful - received access token")
        return token
    else:
        print(f"Authentication failed with error: {response.text}")
        return None

# Step 2: Create a Universal Function for Calling Emission APIs
def call_emission_api(endpoint, payload, token):
    """
    This is my reusable function for calling different emission calculation endpoints.
    It handles the common tasks: formatting the request, adding authentication, and sending data.
    
    Parameters:
    - endpoint: which specific calculation I want (mobile, stationary, fugitive, etc.)
    - payload: the data about my emissions scenario
    - token: my authentication token from step 1
    """
    
    # Base URL for all emission calculations
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    
    # Creating the complete URL by adding the specific endpoint
    full_url = f"{base_url}/{endpoint}"
    
    # Setting up headers with authentication token
    # Bearer token is a standard way to include authentication in API requests
    headers = {
        "Authorization": f"Bearer {token}",  # My access token
        "Content-Type": "application/json"   # Data format I'm using
    }
    
    # Making the API call to calculate emissions
    print(f"Calling {endpoint} calculation endpoint...")
    response = requests.post(full_url, headers=headers, json=payload)
    
    return response

# Step 3: Set Up Mobile Emission Parameters
def create_mobile_emission_payload():
    """
    This function creates the data structure describing my fleet's fuel consumption.
    Each field tells the API something important about how my vehicles operate.
    """
    
    # Building the payload - this is like filling out a detailed form about my fleet
    mobile_payload = {
        "activity_data": {
            # What type of calculation am I doing?
            "activity_type": "mobile_combustion",
            
            # Information about the fuel my fleet uses
            "fuel_data": {
                "fuel_type": "gasoline",  # Type of fuel (gasoline, diesel, natural_gas, etc.)
                "fuel_amount": 1000,       # How much fuel was consumed
                "fuel_unit": "gallons"     # Unit of measurement for fuel
            },
            
            # Details about my vehicle fleet
            "vehicle_info": {
                "vehicle_type": "delivery_van",    # What kind of vehicles
                "vehicle_count": 5,                # How many vehicles
                "model_year": 2020,                # Average model year (affects efficiency)
                "annual_mileage": 15000            # Miles driven per vehicle per year
            },
            
            # Geographic location (affects emission factors)
            "location": {
                "country": "USA",
                "state": "Texas"  # Different regions may have different fuel standards
            },
            
            # Time period for this consumption
            "time_period": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "period_type": "monthly"  # Can be daily, monthly, quarterly, annual
            }
        },
        
        # How I want the results formatted
        "calculation_options": {
            "emission_factors_source": "EPA",  # Use EPA emission factors
            "include_upstream": False,          # Just direct emissions, not production
            "calculation_method": "fuel_based"  # Calculate from fuel, not distance
        }
    }
    
    return mobile_payload

# Step 4: Calculate Mobile Emissions
def calculate_mobile_emissions(token):
    """
    This is where I actually calculate the emissions from my fleet.
    I'll send the fuel consumption data and get back the greenhouse gas emissions.
    """
    
    # Get the payload with all my fleet data
    payload = create_mobile_emission_payload()
    
    # Call the API with my fleet data
    response = call_emission_api("mobile", payload, token)
    
    # Process and display the results
    if response.status_code == 200:
        results = response.json()
        
        print("\nMOBILE EMISSION CALCULATION RESULTS")
        print("=" * 45)
        
        # Extract the emissions data from the response
        emissions = results.get('emissions', {})
        
        # Let me explain each component of the emissions:
        
        # Fossil Fuel CO2: This is the main emission from burning gasoline/diesel
        fossil_co2 = emissions.get('fossilFuelCO2', 0)
        print(f"Fossil Fuel CO2: {fossil_co2:.3f} metric tonnes")
        print("  (This is carbon that was locked underground for millions of years)")
        
        # Biogenic CO2: From any biofuel blends (like ethanol in gasoline)
        biogenic_co2 = emissions.get('biogenicCO2', 0)
        print(f"Biogenic CO2: {biogenic_co2:.3f} metric tonnes")
        print("  (This carbon was recently in the atmosphere, absorbed by plants)")
        
        # Methane (CH4): A powerful greenhouse gas from incomplete combustion
        ch4 = emissions.get('CH4', 0)
        print(f"Methane (CH4): {ch4:.6f} metric tonnes")
        print("  (CH4 is 25x more potent than CO2 for warming)")
        
        # Nitrous Oxide (N2O): Another potent greenhouse gas from combustion
        n2o = emissions.get('N2O', 0)
        print(f"Nitrous Oxide (N2O): {n2o:.6f} metric tonnes")
        print("  (N2O is 298x more potent than CO2 for warming)")
        
        # Total CO2 Equivalent: All gases converted to CO2 impact
        co2e = emissions.get('CO2e', 0)
        print(f"\nTOTAL CO2 Equivalent: {co2e:.3f} metric tonnes")
        print("  (This combines all greenhouse gases into one comparable number)")
        
        # Show the unit of measurement
        unit = emissions.get('unitOfMeasurement', 'metric tonnes')
        print(f"Unit of Measurement: {unit}")
        
        return results
    else:
        print(f"Calculation failed: {response.text}")
        return None

# Step 5: Analyze and Interpret Results
def analyze_emissions(results):
    """
    Let me help interpret what these emission numbers mean
    and suggest practical actions based on the results.
    """
    
    if not results:
        return
    
    emissions = results.get('emissions', {})
    co2e = emissions.get('CO2e', 0)
    
    print("\nEMISSION ANALYSIS")
    print("-" * 40)
    
    # Put the emissions in context
    print(f"Your fleet's {co2e:.2f} tonnes of CO2e is equivalent to:")
    
    # Average car emits about 4.6 tonnes CO2 per year
    cars_equivalent = co2e / 4.6
    print(f"  - {cars_equivalent:.1f} passenger cars driven for one year")
    
    # One tree absorbs about 0.025 tonnes CO2 per year
    trees_needed = co2e / 0.025
    print(f"  - Would require {trees_needed:.0f} trees to offset annually")
    
    # Average home uses about 8.5 tonnes CO2 per year
    homes_equivalent = co2e / 8.5
    print(f"  - {homes_equivalent:.1f} homes' annual energy use")
    
    print("\nREDUCTION STRATEGIES")
    print("-" * 40)
    print("Based on your mobile emissions, consider these actions:")
    print("1. Fleet Optimization:")
    print("   - Route optimization to reduce total miles driven")
    print("   - Implement anti-idling policies")
    print("   - Regular maintenance for optimal fuel efficiency")
    
    print("\n2. Vehicle Upgrades:")
    print("   - Transition to hybrid or electric vehicles")
    print("   - Choose more fuel-efficient models when replacing vehicles")
    print("   - Right-size vehicles to match actual needs")
    
    print("\n3. Alternative Fuels:")
    print("   - Consider biodiesel or renewable diesel")
    print("   - Explore compressed natural gas (CNG) options")
    print("   - Investigate hydrogen for long-haul routes")
    
    print("\n4. Driver Training:")
    print("   - Eco-driving techniques can reduce fuel use by 10-20%")
    print("   - Monitor and reward fuel-efficient driving")

# Step 6: Main Execution Function
def main():
    """
    This orchestrates the entire mobile emissions calculation process.
    I'll authenticate, calculate emissions, and provide actionable insights.
    """
    
    print("MOBILE EMISSIONS CALCULATOR FOR FLEET VEHICLES")
    print("=" * 50)
    print("Calculating Scope 1 emissions from your vehicle fleet")
    print()
    
    # First, I need to authenticate
    print("Step 1: Authentication")
    print("-" * 30)
    token = get_auth_token()
    
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Now calculate the emissions
    print("\nStep 2: Emission Calculation")
    print("-" * 30)
    results = calculate_mobile_emissions(token)
    
    # Finally, analyze what these numbers mean
    if results:
        print("\nStep 3: Analysis & Recommendations")
        print("-" * 30)
        analyze_emissions(results)
        
        # Remind about Scope 1 classification
        print("\nREMEMBER:")
        print("-" * 30)
        print("These are Scope 1 emissions because:")
        print("- You own or control these vehicles")
        print("- The fuel is burned directly by your operations")
        print("- You have direct control over reducing these emissions")
        print("\nTrack these monthly to measure your progress toward reduction goals!")

# Python's standard way to run the main function when the script is executed
if __name__ == "__main__":
    main()

"""
Setup Instructions:
Before running this script, create a secrets.ini file with your API credentials:

[EI]
api.api_key = your_actual_api_key_here
api.client_id = your_actual_client_id_here

Save this file at: ../../auth/secrets.ini (or adjust the path in line 22)

To run the calculator:
python mobile_emissions_calculator.py

Understanding the Output:
- fossilFuelCO2: Direct CO2 from burning petroleum-based fuels
- biogenicCO2: CO2 from biofuel components (considered carbon-neutral)
- CH4: Methane emissions from incomplete combustion
- N2O: Nitrous oxide from high-temperature combustion
- CO2e: Total warming impact expressed as CO2 equivalent

All values are in metric tonnes (1 metric tonne = 1,000 kg = 2,204.6 lbs)
"""
