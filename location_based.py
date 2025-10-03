"""
Learning to Calculate Scope 2 Location-Based Emissions from Electricity

Learning to calculate greenhouse gas emissions from electricity consumption.
These are called Scope 2 emissions because they're indirect - you don't burn the
fuel yourself, but you're responsible for emissions generated elsewhere to produce
the electricity you use.

Location-based emissions use the average emissions intensity of the electrical grid
where your facility is located. Different grids have different fuel mixes (coal,
natural gas, nuclear, renewables), so emissions vary significantly by location.
"""

import requests  
import json      
import configparser  

config = configparser.ConfigParser()

# The path '../../auth/secrets.ini' navigates up two folders then into 'auth'
config.read('../../auth/secrets.ini')

API_KEY = config['EI']['api.api_key']
CLIENT_ID = config['EI']['api.client_id']

# Step 1: Authentication Function
def get_auth_token():
    """
    Before calculating emissions, I need to authenticate with the API.
    This exchanges my permanent credentials for a temporary access token.
    It's like showing your employee badge to get a temporary visitor pass.
    """
    
    # The endpoint where I request authentication
    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    
    # Headers specify what format I'm using for data
    auth_headers = {
        "Content-Type": "application/json"  # I'm communicating in JSON format
    }
    
    # My credentials that prove I'm authorized to use this service
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    # Making the authentication request
    print("Requesting authentication token for emissions API...")
    response = requests.post(auth_url, headers=auth_headers, json=auth_data)
    
    # Checking if authentication succeeded
    if response.status_code == 200:
        # Extract the token from the response
        token = response.json()['access_token']
        print("Authentication successful - received access token")
        return token
    else:
        print(f"Authentication failed: {response.text}")
        return None

# Step 2: Create a Reusable API Calling Function
def call_emission_api(endpoint, payload, token):
    """
    This is my generic function for calling emission calculation endpoints.
    It handles the common tasks of formatting requests and authentication.
    
    Parameters:
    - endpoint: which calculation type I want (location_based, market_based, etc.)
    - payload: the data about my electricity consumption
    - token: my authentication token from step 1
    """
    
    # Base URL for emission calculations
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    
    # Building the complete URL for my specific calculation
    full_url = f"{base_url}/{endpoint}"
    
    # Headers include my authentication token and data format
    headers = {
        "Authorization": f"Bearer {token}",  # My access credentials
        "Content-Type": "application/json"   # Data format I'm using
    }
    
    # Making the API call to calculate emissions
    print(f"Calling {endpoint} emissions endpoint...")
    response = requests.post(full_url, headers=headers, json=payload)
    
    return response

# Step 3: Set Location-Based Emission Parameters
def create_location_based_payload():
    """
    Here I'm defining the parameters for location-based electricity emissions.
    Location-based method uses the average emission intensity of the local grid.
    This reflects the actual mix of energy sources (coal, gas, nuclear, renewable)
    feeding the grid where my facility operates.
    """
    
    # Building the payload with my electricity consumption data
    location_payload = {
        "activity_data": {
            # Specifying that this is electricity consumption
            "activity_type": "electricity_consumption",
            
            # My electricity usage information
            "electricity_usage": {
                "consumption_amount": 50000,     # Amount of electricity used
                "consumption_unit": "kWh",       # Kilowatt-hours (standard unit)
                "measurement_type": "actual"     # actual vs estimated consumption
            },
            
            # Facility information
            "facility_details": {
                "facility_type": "office",       # office, warehouse, datacenter, manufacturing
                "facility_size_sqft": 75000,     # Size helps validate consumption
                "operating_hours": 2080,         # Annual operating hours
                "year_built": 2010               # Age can affect efficiency
            },
            
            # Critical for location-based: WHERE is this electricity used?
            # Different locations have vastly different grid emissions
            "location": {
                "country": "USA",
                "state": "California",           # CA has cleaner grid than many states
                "zip_code": "94102",             # More precise = more accurate factors
                "grid_region": "CAMX"            # California ISO grid region
            },
            
            # Time period for this consumption
            # Grid emissions change over time as fuel mix evolves
            "time_period": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "period_type": "annual",         # annual, quarterly, monthly
                "reporting_year": 2024           # Some grids have year-specific factors
            }
        },
        
        # Calculation methodology options
        "calculation_method": {
            "method_type": "location_based",     # Using grid average emissions
            "emissions_source": "EPA_eGRID",     # EPA's database for US grids
            "include_transmission_losses": True,  # Account for line losses
            "renewable_energy_credits": False    # RECs handled in market-based method
        }
    }
    
    return location_payload

# Step 4: Calculate Location-Based Emissions
def calculate_location_based_emissions(token):
    """
    This performs the actual calculation of Scope 2 emissions from electricity.
    I send my consumption data and location, and receive back the emissions
    based on the average carbon intensity of my local electrical grid.
    """
    
    # Get my configured payload with electricity data
    payload = create_location_based_payload()
    
    # Call the API with my electricity consumption data
    response = call_emission_api("location_based", payload, token)
    
    # Process and display the results
    if response.status_code == 200:
        results = response.json()
        
        print("\nLOCATION-BASED EMISSION CALCULATION RESULTS")
        print("Scope 2 emissions from purchased electricity")
        print()
        
        # Extract emissions data from response
        emissions = results.get('emissions', {})
        
        # CO2 equivalent is the main output for Scope 2
        co2e = emissions.get('CO2e', 0)
        print(f"Total CO2 Equivalent: {co2e:.3f} metric tonnes")
        print("  This represents emissions from generating your electricity")
        print("  Based on the average fuel mix of your regional grid")
        
        # Grid emission factor (if provided)
        if 'emission_factor' in results:
            ef = results['emission_factor']
            print(f"\nGrid Emission Factor: {ef:.4f} kg CO2e/kWh")
            print("  This is the carbon intensity of your electrical grid")
            print("  Lower numbers mean cleaner electricity")
        
        # Grid composition breakdown (if available)
        if 'grid_mix' in results:
            print("\nYour Regional Grid Energy Sources:")
            grid_mix = results['grid_mix']
            for source, percentage in grid_mix.items():
                print(f"  {source}: {percentage:.1f}%")
        
        # Comparison to national average
        if 'national_average_factor' in results:
            nat_avg = results['national_average_factor']
            local_ef = results.get('emission_factor', 0)
            if local_ef > 0:
                difference = ((local_ef - nat_avg) / nat_avg) * 100
                if difference > 0:
                    print(f"\nYour grid is {difference:.1f}% more carbon-intensive than national average")
                else:
                    print(f"\nYour grid is {abs(difference):.1f}% cleaner than national average")
        
        return results
    else:
        print(f"Calculation failed: {response.text}")
        return None

# Step 5: Provide Context and Grid Comparisons
def analyze_grid_emissions(results, consumption_kwh=50000):
    """
    Let me help interpret these results by comparing different grids
    and showing how location dramatically affects Scope 2 emissions.
    """
    
    if not results:
        return
    
    emissions = results.get('emissions', {})
    co2e = emissions.get('CO2e', 0)
    
    print("\nUNDERSTANDING YOUR ELECTRICITY EMISSIONS")
    print()
    
    # Context for the emissions
    print(f"Your {co2e:.2f} tonnes CO2e from {consumption_kwh:,} kWh means:")
    
    # Equivalent comparisons
    miles_driven = co2e * 2480  # Average car emits 404g/mile
    print(f"  - Equivalent to driving {miles_driven:,.0f} miles")
    
    homes_powered = consumption_kwh / 10800  # Average home uses 10,800 kWh/year
    print(f"  - You used electricity equal to {homes_powered:.1f} average homes")
    
    trees_needed = co2e / 0.025  # One tree absorbs ~25kg CO2/year
    print(f"  - Would need {trees_needed:.0f} trees to offset annually")
    
    print("\nHOW LOCATION AFFECTS YOUR EMISSIONS")
    print("The same electricity consumption in different locations:")
    print()
    
    # Grid emission factors for various US regions (kg CO2/kWh)
    grid_factors = {
        "West Virginia (coal-heavy)": 0.850,
        "Wyoming (coal-heavy)": 0.815,
        "Indiana (coal/gas mix)": 0.720,
        "Texas (diverse mix)": 0.450,
        "California (renewable-heavy)": 0.250,
        "New York (hydro/nuclear)": 0.230,
        "Vermont (hydro/nuclear)": 0.013,
        "Iceland (geothermal/hydro)": 0.000
    }
    
    for region, factor in grid_factors.items():
        regional_emissions = (consumption_kwh * factor) / 1000  # Convert to tonnes
        print(f"  {region}: {regional_emissions:.2f} tonnes CO2e")
    
    print("\nKEY INSIGHT:")
    print("Your location's grid mix is the biggest factor in Scope 2 emissions!")
    print("The same 50,000 kWh could produce 0.65 to 42.5 tonnes CO2e depending on location")

# Step 6: Suggest Reduction Strategies
def provide_reduction_strategies(co2e_emissions):
    """
    I'll provide practical strategies for reducing Scope 2 emissions,
    both through reducing consumption and choosing cleaner electricity.
    """
    
    print("\nSTRATEGIES TO REDUCE SCOPE 2 EMISSIONS")
    print()
    
    print("1. REDUCE ELECTRICITY CONSUMPTION")
    print("   Energy Efficiency Improvements:")
    print("   - LED lighting upgrade can reduce lighting energy by 75%")
    print("   - HVAC optimization can save 20-30% on heating/cooling")
    print("   - Smart building controls for automated efficiency")
    print("   - Equipment upgrades to ENERGY STAR certified models")
    
    print("\n2. SHIFT TO CLEANER ELECTRICITY SOURCES")
    print("   On-site Generation:")
    print("   - Install solar panels (eliminates grid emissions for that portion)")
    print("   - Consider wind turbines where feasible")
    print("   - Explore geothermal for heating/cooling")
    
    print("\n   Clean Energy Procurement:")
    print("   - Purchase Renewable Energy Credits (RECs)")
    print("   - Enter Power Purchase Agreements (PPAs) for renewable energy")
    print("   - Choose green power programs from your utility")
    print("   - Consider Virtual Power Purchase Agreements (VPPAs)")
    
    print("\n3. OPTIMIZE WHEN YOU USE ELECTRICITY")
    print("   Time-of-Use Strategies:")
    print("   - Shift loads to times when grid is cleanest (often midday with solar)")
    print("   - Use battery storage to time-shift consumption")
    print("   - Participate in demand response programs")
    
    print("\n4. LOCATION-BASED VS MARKET-BASED ACCOUNTING")
    print("   Understanding Both Methods:")
    print("   - Location-based: What I calculated here (grid average)")
    print("   - Market-based: Accounts for renewable energy purchases")
    print("   - Report both for complete transparency")
    
    # Calculate potential savings
    print(f"\nPOTENTIAL IMPACT FOR YOUR {co2e_emissions:.2f} TONNES:")
    
    efficiency_reduction = co2e_emissions * 0.25
    print(f"  25% efficiency improvement: Save {efficiency_reduction:.2f} tonnes")
    
    solar_offset = co2e_emissions * 0.40
    print(f"  40% solar installation: Offset {solar_offset:.2f} tonnes")
    
    combined = co2e_emissions * 0.55
    print(f"  Combined approach: Reduce by {combined:.2f} tonnes")

# Step 7: Compare Scope 1 vs Scope 2
def explain_scope_differences():
    """
    Let me clarify the important distinction between Scope 1 and Scope 2
    emissions and why they're categorized differently.
    """
    
    print("\nUNDERSTANDING SCOPE 2 VS SCOPE 1")
    print()
    
    print("SCOPE 1 (Direct Emissions):")
    print("  - Fuel YOU burn directly")
    print("  - Equipment YOU own and operate")
    print("  - Examples: Company vehicles, on-site boilers, refrigerant leaks")
    print("  - Control: Direct and immediate")
    
    print("\nSCOPE 2 (Indirect - Purchased Energy):")
    print("  - Emissions from electricity YOU purchase")
    print("  - Generated elsewhere but caused by your demand")
    print("  - Examples: Grid electricity, purchased steam, district cooling")
    print("  - Control: Indirect through purchasing decisions")
    
    print("\nWHY THE DISTINCTION MATTERS:")
    print("  - Avoids double counting (utility reports as Scope 1, you as Scope 2)")
    print("  - Different reduction strategies for each")
    print("  - Helps identify where you have most control")
    print("  - Required for complete carbon accounting")
    
    print("\nREPORTING CONSIDERATIONS:")
    print("  - Most standards require reporting both Scope 1 and 2")
    print("  - Location-based method is typically required")
    print("  - Market-based method shows impact of renewable purchases")
    print("  - Together they give complete picture of operational emissions")

# Step 8: Main Orchestration Function
def main():
    """
    This coordinates the entire Scope 2 emission calculation process,
    from authentication through analysis and recommendations.
    """
    
    print("SCOPE 2 LOCATION-BASED EMISSIONS CALCULATOR")
    print("Calculating indirect emissions from purchased electricity")
    print()
    
    # Authenticate first
    print("Step 1: Authenticating with emissions API")
    token = get_auth_token()
    
    if not token:
        print("Cannot proceed without valid authentication")
        return
    
    # Calculate emissions
    print("\nStep 2: Calculating location-based electricity emissions")
    results = calculate_location_based_emissions(token)
    
    # Analyze and provide context
    if results:
        emissions = results.get('emissions', {})
        co2e = emissions.get('CO2e', 0)
        
        print("\nStep 3: Analyzing your electricity emissions")
        analyze_grid_emissions(results)
        
        print("\nStep 4: Identifying reduction opportunities")
        provide_reduction_strategies(co2e)
        
        print("\nStep 5: Understanding emission scopes")
        explain_scope_differences()
        
        # Summary message
        print("\nKEY TAKEAWAYS:")
        print()
        print("1. Your Scope 2 emissions depend heavily on your local grid mix")
        print("2. You can reduce through efficiency AND cleaner energy procurement")
        print("3. Location-based shows grid reality, market-based shows your choices")
        print("4. Track monthly to identify patterns and measure improvement")
        print("5. Consider both on-site generation and renewable energy purchases")

# Running the main function when script is executed
if __name__ == "__main__":
    main()

"""
Setup Instructions:

Before running, create a secrets.ini file:

[EI]
api.api_key = your_actual_api_key_here
api.client_id = your_actual_client_id_here

Save at: ../../auth/secrets.ini (or adjust path)

Run with: python location_based_emissions.py

Understanding Location-Based Emissions:

Location-based method reflects the average emissions intensity of grids
where electricity consumption occurs. It uses regional grid emission
factors that represent the mix of energy sources in that region.

Key Factors Affecting Grid Emissions:
- Coal: ~820-1000 kg CO2/MWh (highest emissions)
- Natural Gas: ~350-450 kg CO2/MWh (moderate emissions)  
- Nuclear: ~12 kg CO2/MWh (lifecycle emissions only)
- Wind: ~11 kg CO2/MWh (lifecycle emissions only)
- Solar: ~48 kg CO2/MWh (lifecycle emissions only)
- Hydro: ~24 kg CO2/MWh (lifecycle emissions only)

Grid Emission Factors Vary Widely:
- West Virginia: ~850 g CO2/kWh (85% coal)
- California: ~250 g CO2/kWh (50% renewable, 35% natural gas)
- Vermont: ~13 g CO2/kWh (60% hydro, 20% nuclear)
- France: ~60 g CO2/kWh (70% nuclear)
- Poland: ~750 g CO2/kWh (75% coal)

This variation means the same electricity consumption can have
vastly different carbon footprints depending on location!
"""
