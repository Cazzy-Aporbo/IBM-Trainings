"""
Learning to Calculate Scope 1 Stationary Emissions from Fuel Combustion

Calculate greenhouse gas emissions from stationary sources.
These are emissions from equipment that burns fuel but doesn't move - like
boilers, furnaces, heaters, and generators at your facilities.

Stationary combustion is often the largest source of Scope 1 emissions for
buildings and manufacturing facilities. If you own the equipment, these are
your direct emissions that you control.
Python 3.6+
"""

import requests  # This allows me to communicate with web APIs
import json      # JSON is the data format that APIs understand
import configparser  # This reads configuration files securely

# Setting up a configuration parser to handle my API credentials
# Keeping credentials in a separate file is a security best practice
config = configparser.ConfigParser()

# Reading the credentials from a secure location
# The path '../../auth/secrets.ini' means go up two directories, then into 'auth'
config.read('../../auth/secrets.ini')

# Extracting my API credentials from the configuration
# These credentials are like my ID card for accessing the emissions API
API_KEY = config['EI']['api.api_key']
CLIENT_ID = config['EI']['api.client_id']

# Step 1: Authentication Function
def get_auth_token():
    """
    I need to authenticate before I can calculate emissions.
    This function trades my permanent credentials for a temporary access token.
    Think of it like getting a visitor pass at a building's security desk.
    """
    
    # The URL where I request authentication
    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    
    # Headers tell the API what format I'm using for communication
    auth_headers = {
        "Content-Type": "application/json"  # I'm sending data in JSON format
    }
    
    # My credentials that prove I'm authorized to use this API
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    # Sending the authentication request
    print("Requesting authentication token for emissions API...")
    response = requests.post(auth_url, headers=auth_headers, json=auth_data)
    
    # Checking if I successfully authenticated
    if response.status_code == 200:
        # Extracting the access token from the response
        token = response.json()['access_token']
        print("Authentication successful - token received")
        return token
    else:
        print(f"Authentication failed: {response.text}")
        return None

# Step 2: Generic API Calling Function
def call_emission_api(endpoint, payload, token):
    """
    This is my reusable function for calling any emission calculation endpoint.
    It handles the technical details of making API requests.
    
    Parameters:
    - endpoint: which type of emission calculation (stationary, mobile, etc.)
    - payload: the data describing my emission scenario
    - token: my authentication token proving I'm allowed to use the API
    """
    
    # The base URL for all emission calculations
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    
    # Building the complete URL for my specific calculation
    full_url = f"{base_url}/{endpoint}"
    
    # Headers include my authentication and data format
    headers = {
        "Authorization": f"Bearer {token}",  # My access pass
        "Content-Type": "application/json"   # Format I'm using
    }
    
    # Making the actual API call
    print(f"Calling {endpoint} emissions calculation...")
    response = requests.post(full_url, headers=headers, json=payload)
    
    return response

# Step 3: Create Stationary Emission Parameters
def create_stationary_emission_payload():
    """
    Here I'm defining the parameters for my stationary combustion scenario.
    This describes what fuel is being burned and how it's being used.
    Stationary sources include boilers, furnaces, heaters, generators, and
    any other equipment that burns fuel but doesn't move.
    """
    
    # Building the data structure that describes my stationary combustion
    stationary_payload = {
        "activity_data": {
            # Specifying that this is stationary combustion
            "activity_type": "stationary_combustion",
            
            # Information about the fuel being burned
            "fuel_consumption": {
                "fuel_type": "natural_gas",     # Common fuels: natural_gas, fuel_oil, propane, coal
                "fuel_amount": 10000,            # Amount of fuel consumed
                "fuel_unit": "therms",          # Units: therms, gallons, tons, cubic_feet, etc.
                "heating_value": "higher"       # Higher or lower heating value (affects calculations)
            },
            
            # Details about the combustion equipment
            "equipment_details": {
                "equipment_type": "boiler",     # boiler, furnace, heater, generator, etc.
                "equipment_age": 10,            # Age affects efficiency
                "efficiency_rating": 0.85,      # 85% efficiency
                "capacity": "5_MMBtu",          # Equipment capacity
                "usage_hours": 2000            # Annual operating hours
            },
            
            # Purpose of the combustion
            "combustion_purpose": {
                "primary_use": "comfort_heating",  # comfort_heating, process_heat, electricity
                "building_type": "office",         # office, warehouse, manufacturing, etc.
                "building_size_sqft": 50000       # Size of facility being heated
            },
            
            # Location information (affects emission factors)
            "location": {
                "country": "USA",
                "state": "New York",
                "zip_code": "10001"  # More specific location for accurate factors
            },
            
            # Time period for this fuel consumption
            "time_period": {
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
                "period_type": "quarterly"  # Can be daily, monthly, quarterly, annual
            }
        },
        
        # Options for how I want the calculation performed
        "calculation_options": {
            "emission_factors_source": "EPA",      # EPA, IPCC, or custom factors
            "include_upstream": False,              # Just combustion, not fuel production
            "calculation_method": "fuel_analysis", # Based on fuel composition
            "global_warming_potential": "AR5"      # Which GWP values to use
        }
    }
    
    return stationary_payload

# Step 4: Calculate Stationary Emissions
def calculate_stationary_emissions(token):
    """
    This function performs the actual emission calculation for stationary combustion.
    I send data about fuel burned in stationary equipment and receive back
    the resulting greenhouse gas emissions.
    """
    
    # Getting my configured payload
    payload = create_stationary_emission_payload()
    
    # Making the API call with my stationary combustion data
    response = call_emission_api("stationary", payload, token)
    
    # Processing and displaying the results
    if response.status_code == 200:
        results = response.json()
        
        print("\nSTATIONARY EMISSION CALCULATION RESULTS")
        print("Emissions from fuel combustion in stationary equipment")
        print()
        
        # Extracting emission values from the response
        emissions = results.get('emissions', {})
        
        # Fossil Fuel CO2: The primary emission from burning fossil fuels
        fossil_co2 = emissions.get('fossilFuelCO2', 0)
        print(f"Fossil Fuel CO2: {fossil_co2:.3f} metric tonnes")
        print("  This is carbon released from fossil fuels formed over millions of years")
        print("  It adds new carbon to the atmosphere-biosphere system")
        
        # Biogenic CO2: From any biomass or biofuel components
        biogenic_co2 = emissions.get('biogenicCO2', 0)
        print(f"\nBiogenic CO2: {biogenic_co2:.3f} metric tonnes")
        print("  This carbon was recently in the atmosphere (absorbed by plants)")
        print("  Often considered carbon-neutral in GHG accounting")
        
        # Methane: A potent greenhouse gas from incomplete combustion
        ch4 = emissions.get('CH4', 0)
        print(f"\nMethane (CH4): {ch4:.6f} metric tonnes")
        print("  CH4 has 25 times the warming potential of CO2")
        print("  Results from incomplete combustion, especially in older equipment")
        
        # Nitrous Oxide: Another powerful greenhouse gas
        n2o = emissions.get('N2O', 0)
        print(f"\nNitrous Oxide (N2O): {n2o:.6f} metric tonnes")
        print("  N2O has 298 times the warming potential of CO2")
        print("  Forms at high combustion temperatures")
        
        # Total CO2 Equivalent: All gases converted to equivalent CO2 impact
        co2e = emissions.get('CO2e', 0)
        print(f"\nTOTAL CO2 Equivalent: {co2e:.3f} metric tonnes")
        print("  This combines all greenhouse gases using their global warming potentials")
        print("  This is the number to use for carbon footprint reporting")
        
        # Unit of measurement confirmation
        unit = emissions.get('unitOfMeasurement', 'metric tonnes')
        print(f"\nAll measurements in: {unit}")
        
        return results
    else:
        print(f"Emission calculation failed: {response.text}")
        return None

# Step 5: Provide Context and Recommendations
def analyze_stationary_emissions(results):
    """
    Let me help interpret these emission results and suggest
    practical ways to reduce stationary combustion emissions.
    """
    
    if not results:
        return
    
    emissions = results.get('emissions', {})
    co2e = emissions.get('CO2e', 0)
    
    print("\nCONTEXT FOR YOUR STATIONARY EMISSIONS")
    print()
    
    # Putting emissions in perspective
    print(f"Your {co2e:.2f} tonnes of CO2e from stationary combustion equals:")
    
    # Natural gas: about 5.3 tonnes CO2e per home per year for heating
    homes_heated = co2e / 5.3
    print(f"  - Heating {homes_heated:.1f} average homes for one year")
    
    # Forest carbon sequestration: about 0.84 tonnes CO2 per acre per year
    forest_acres = co2e / 0.84
    print(f"  - Would need {forest_acres:.1f} acres of forest to offset annually")
    
    # Gallons of gasoline: about 0.00887 tonnes CO2e per gallon
    gasoline_gallons = co2e / 0.00887
    print(f"  - Burning {gasoline_gallons:.0f} gallons of gasoline")
    
    print("\nEMISSION REDUCTION STRATEGIES FOR STATIONARY SOURCES")
    print()
    
    print("1. Equipment Efficiency Improvements:")
    print("   - Upgrade to high-efficiency boilers (90%+ AFUE rating)")
    print("   - Install economizers to recover waste heat")
    print("   - Regular maintenance and tuning for optimal combustion")
    print("   - Replace old equipment (15+ years) with modern alternatives")
    
    print("\n2. Operational Optimization:")
    print("   - Implement setback temperatures during unoccupied hours")
    print("   - Install programmable thermostats and building automation")
    print("   - Optimize start-up and shut-down procedures")
    print("   - Monitor combustion efficiency with regular stack testing")
    
    print("\n3. Fuel Switching Options:")
    print("   - Convert from fuel oil to natural gas (22% less CO2)")
    print("   - Explore renewable natural gas (RNG) from biomass")
    print("   - Consider electric heat pumps for moderate climates")
    print("   - Investigate biomass options for appropriate applications")
    
    print("\n4. Building Envelope Improvements:")
    print("   - Add insulation to reduce heating demand")
    print("   - Seal air leaks and improve weatherization")
    print("   - Upgrade windows and doors")
    print("   - These reduce fuel needs rather than emissions per unit fuel")
    
    print("\n5. Heat Recovery Systems:")
    print("   - Install heat exchangers to capture waste heat")
    print("   - Use combined heat and power (CHP) systems")
    print("   - Implement thermal storage for load shifting")

# Step 6: Calculate Potential Savings
def estimate_reduction_potential(current_emissions):
    """
    I'll estimate how much you could reduce emissions through
    various improvement strategies based on typical reduction percentages.
    """
    
    print("\nPOTENTIAL EMISSION REDUCTIONS")
    print()
    
    # Typical reduction percentages from various strategies
    reductions = {
        "Equipment upgrade (to 95% efficiency)": 0.15,
        "Operational optimization": 0.10,
        "Building envelope improvements": 0.20,
        "Fuel switching (oil to gas)": 0.22,
        "Heat recovery installation": 0.08
    }
    
    print("Based on typical improvement factors:")
    print()
    
    total_possible_reduction = 0
    for strategy, reduction_factor in reductions.items():
        reduction_amount = current_emissions * reduction_factor
        total_possible_reduction += reduction_amount
        print(f"{strategy}:")
        print(f"  Potential reduction: {reduction_amount:.2f} tonnes CO2e")
        print(f"  New emissions: {current_emissions - reduction_amount:.2f} tonnes CO2e")
        print()
    
    # Combined effect (not simply additive due to interactions)
    combined_reduction = current_emissions * 0.40  # Realistic combined improvement
    print(f"Realistic combined improvement potential:")
    print(f"  Could reduce emissions by ~40%: {combined_reduction:.2f} tonnes CO2e")
    print(f"  Achieving: {current_emissions - combined_reduction:.2f} tonnes CO2e annually")

# Step 7: Main Orchestration Function
def main():
    """
    This is the main function that coordinates the entire stationary
    emission calculation process from authentication through recommendations.
    """
    
    print("STATIONARY COMBUSTION EMISSIONS CALCULATOR")
    print("Calculating Scope 1 emissions from fuel burned in stationary equipment")
    print()
    
    # Step 1: Get authenticated
    print("Step 1: Authenticating with emissions API")
    token = get_auth_token()
    
    if not token:
        print("Cannot proceed without valid authentication")
        return
    
    # Step 2: Calculate emissions
    print("\nStep 2: Calculating stationary combustion emissions")
    results = calculate_stationary_emissions(token)
    
    # Step 3: Provide analysis and context
    if results:
        print("\nStep 3: Analyzing results and providing context")
        analyze_stationary_emissions(results)
        
        # Step 4: Estimate reduction potential
        emissions = results.get('emissions', {})
        co2e = emissions.get('CO2e', 0)
        if co2e > 0:
            estimate_reduction_potential(co2e)
        
        # Remind why these are Scope 1
        print("\nWHY THESE ARE SCOPE 1 EMISSIONS:")
        print()
        print("- You own or control the combustion equipment")
        print("- The fuel is burned directly at your facility")
        print("- You have direct control over these emissions through:")
        print("  - Equipment choices and maintenance")
        print("  - Operational decisions")
        print("  - Fuel purchasing decisions")
        print("\nRegular monitoring helps track progress toward reduction goals")

# Running the main function when the script is executed
if __name__ == "__main__":
    main()

"""
Setup Instructions:

Before running this script, create a secrets.ini file:

[EI]
api.api_key = your_actual_api_key_here
api.client_id = your_actual_client_id_here

Save at: ../../auth/secrets.ini (or adjust path in line 22)

Run with: python stationary_emissions_calculator.py

Understanding Stationary Emissions:

Stationary combustion includes all fuel burning in fixed equipment:
- Boilers for steam or hot water
- Furnaces for space heating
- Heaters for process heat
- Generators for backup power
- Ovens and kilns in manufacturing
- Any other fixed combustion equipment

Output Definitions:
- fossilFuelCO2: CO2 from fossil fuel combustion
- biogenicCO2: CO2 from biomass (often reported separately)
- CH4: Methane from incomplete combustion
- N2O: Nitrous oxide from high-temperature combustion
- CO2e: Total impact as CO2 equivalent

Emission factors vary by fuel type:
- Natural Gas: ~53 kg CO2/MMBtu
- Fuel Oil #2: ~73 kg CO2/MMBtu
- Propane: ~63 kg CO2/MMBtu
- Coal: ~95 kg CO2/MMBtu
"""
