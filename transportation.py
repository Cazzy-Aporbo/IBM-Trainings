"""
Learning to Calculate Scope 3 Transportation and Distribution Emissions

Calculate greenhouse gas emissions from transportation
and distribution in the value chain. These are Scope 3 emissions because
they occur from sources not owned or directly controlled by your organization,
but are a consequence of your business activities.

This includes business travel, employee commuting, and freight transport -
activities essential to your business but performed by third parties.
"""

import requests  
import json      
import configparser  

config = configparser.ConfigParser()
config.read('../../auth/secrets.ini')
API_KEY = config['EI']['api.api_key']
CLIENT_ID = config['EI']['api.client_id']

# Step 1: Authentication Function
def get_auth_token():
    """
    I need to authenticate before calculating emissions.
    This exchanges permanent credentials for a temporary access token.
    It's like checking in at a hotel to get your room key.
    """
    
    # Authentication endpoint
    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    
    # Headers specify the data format
    auth_headers = {
        "Content-Type": "application/json"  # Using JSON format
    }
    
    # Credentials proving I'm authorized
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    # Making authentication request
    print("Requesting authentication token...")
    response = requests.post(auth_url, headers=auth_headers, json=auth_data)
    
    # Checking authentication success
    if response.status_code == 200:
        token = response.json()['access_token']
        print("Authentication successful")
        return token
    else:
        print(f"Authentication failed: {response.text}")
        return None

# Step 2: Generic API Calling Function
def call_emission_api(endpoint, payload, token):
    """
    Reusable function for calling emission calculation endpoints.
    Handles request formatting and authentication.
    
    Parameters:
    - endpoint: calculation type (transportation, business_travel, etc.)
    - payload: data about transportation activities
    - token: authentication token from step 1
    """
    
    # Base URL for emissions API
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    
    # Complete URL with endpoint
    full_url = f"{base_url}/{endpoint}"
    
    # Headers with authentication
    headers = {
        "Authorization": f"Bearer {token}",  # Access token
        "Content-Type": "application/json"   # Data format
    }
    
    # Making API call
    print(f"Calling {endpoint} emissions calculation...")
    response = requests.post(full_url, headers=headers, json=payload)
    
    return response

# Step 3: Create Transportation and Distribution Parameters
def create_transportation_payload():
    """
    Setting up parameters for transportation and distribution emissions.
    This covers various Scope 3 categories including business travel,
    employee commuting, and freight transport. These emissions occur
    in your value chain but not from vehicles you own.
    """
    
    # Building comprehensive transportation emissions payload
    transport_payload = {
        "activity_data": {
            # Identifying this as transportation emissions
            "activity_type": "transportation_distribution",
            
            # BUSINESS TRAVEL - Scope 3 Category 6
            "business_travel": {
                # Air travel is often the largest component
                "air_travel": [
                    {
                        "trip_type": "domestic",
                        "class": "economy",
                        "distance": 5000,  # Total kilometers
                        "distance_unit": "km",
                        "number_of_trips": 25,
                        "travelers": 2,
                        "origin_airport": "SFO",
                        "destination_airport": "JFK",
                        "include_radiative_forcing": True  # High-altitude impact
                    },
                    {
                        "trip_type": "international",
                        "class": "business",  # Business class has higher emissions
                        "distance": 10000,
                        "distance_unit": "km",
                        "number_of_trips": 10,
                        "travelers": 1,
                        "origin_airport": "JFK",
                        "destination_airport": "LHR"
                    }
                ],
                
                # Ground travel for business
                "ground_travel": {
                    "rental_cars": {
                        "vehicle_type": "midsize",
                        "fuel_type": "gasoline",
                        "distance": 15000,
                        "distance_unit": "miles",
                        "fuel_efficiency": 30,  # Miles per gallon
                        "efficiency_unit": "mpg"
                    },
                    "rail": {
                        "distance": 5000,
                        "distance_unit": "km",
                        "rail_type": "intercity"  # intercity, light_rail, subway
                    },
                    "taxi_rideshare": {
                        "distance": 2000,
                        "distance_unit": "km",
                        "vehicle_type": "standard"
                    }
                },
                
                # Hotel stays during business travel
                "accommodation": {
                    "hotel_nights": 150,
                    "hotel_class": "standard",  # luxury hotels have higher emissions
                    "location_type": "urban"
                }
            },
            
            # EMPLOYEE COMMUTING - Scope 3 Category 7
            "employee_commuting": {
                "commute_methods": [
                    {
                        "method": "personal_vehicle",
                        "employees": 100,
                        "avg_distance_per_day": 30,  # Round trip
                        "distance_unit": "km",
                        "working_days": 220,
                        "vehicle_type": "average_car",
                        "fuel_type": "gasoline",
                        "occupancy": 1.2  # Average people per vehicle
                    },
                    {
                        "method": "public_transit",
                        "employees": 50,
                        "avg_distance_per_day": 25,
                        "distance_unit": "km",
                        "working_days": 220,
                        "transit_type": "bus"
                    },
                    {
                        "method": "walking_cycling",
                        "employees": 20,
                        "emissions": 0  # Zero emissions for active transport
                    },
                    {
                        "method": "remote_work",
                        "employees": 30,
                        "work_from_home_days": 220,
                        "home_office_energy": 3,  # kWh per day
                        "energy_unit": "kWh"
                    }
                ]
            },
            
            # FREIGHT TRANSPORT - Scope 3 Categories 4 & 9
            "freight_transport": {
                # Upstream transportation (suppliers to you)
                "upstream": [
                    {
                        "mode": "truck",
                        "distance": 50000,
                        "distance_unit": "km",
                        "weight": 100,
                        "weight_unit": "tonnes",
                        "truck_type": "heavy_duty",
                        "load_factor": 0.8  # 80% full
                    },
                    {
                        "mode": "ocean",
                        "distance": 10000,
                        "distance_unit": "km",
                        "weight": 500,
                        "weight_unit": "tonnes",
                        "vessel_type": "container_ship"
                    }
                ],
                
                # Downstream transportation (you to customers)
                "downstream": [
                    {
                        "mode": "air_freight",
                        "distance": 5000,
                        "distance_unit": "km",
                        "weight": 10,
                        "weight_unit": "tonnes",
                        "urgency": "express"  # Express shipping has higher emissions
                    },
                    {
                        "mode": "last_mile_delivery",
                        "packages": 10000,
                        "avg_distance": 15,
                        "distance_unit": "km",
                        "vehicle_type": "delivery_van"
                    }
                ]
            },
            
            # Location and time period
            "reporting_details": {
                "organization_location": {
                    "country": "USA",
                    "state": "California",
                    "city": "San Francisco"
                },
                "reporting_period": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "period_type": "annual"
                }
            }
        },
        
        # Calculation options
        "calculation_options": {
            "method": "distance_based",  # distance_based or spend_based
            "emission_factors_source": "DEFRA",  # DEFRA, EPA, or custom
            "include_well_to_tank": True,  # Include fuel production emissions
            "allocation_method": "mass"  # For freight: mass, volume, or value
        }
    }
    
    return transport_payload

# Step 4: Calculate Transportation Emissions
def calculate_transportation_emissions(token):
    """
    Performing the transportation and distribution emission calculation.
    This covers all transport-related Scope 3 emissions from business
    operations that don't involve company-owned vehicles.
    """
    
    # Get configured payload
    payload = create_transportation_payload()
    
    # Call API with transportation data
    response = call_emission_api("transportation", payload, token)
    
    # Process results
    if response.status_code == 200:
        results = response.json()
        
        print("\nTRANSPORTATION & DISTRIBUTION EMISSIONS RESULTS")
        print("Scope 3 emissions from value chain transportation")
        print()
        
        # Extract emissions data
        emissions = results.get('emissions', {})
        
        # Breaking down emissions by type
        # Fossil Fuel CO2: Primary emission from fuel combustion
        fossil_co2 = emissions.get('fossilFuelCO2', 0)
        print(f"Fossil Fuel CO2: {fossil_co2:.3f} metric tonnes")
        print("  Direct CO2 from burning transportation fuels")
        
        # Biogenic CO2: From biofuel components
        biogenic_co2 = emissions.get('biogenicCO2', 0)
        print(f"\nBiogenic CO2: {biogenic_co2:.3f} metric tonnes")
        print("  From biofuel blends in transportation")
        
        # Methane: From incomplete combustion
        ch4 = emissions.get('CH4', 0)
        print(f"\nMethane (CH4): {ch4:.6f} metric tonnes")
        print("  Minor emission from vehicle engines")
        
        # Nitrous Oxide: From catalytic converters and combustion
        n2o = emissions.get('N2O', 0)
        print(f"\nNitrous Oxide (N2O): {n2o:.6f} metric tonnes")
        print("  From vehicle emissions control systems")
        
        # Total CO2 Equivalent
        co2e = emissions.get('CO2e', 0)
        print(f"\nTOTAL CO2 Equivalent: {co2e:.3f} metric tonnes")
        print("  Combined impact of all greenhouse gases")
        
        # Unit confirmation
        unit = emissions.get('unitOfMeasurement', 'metric tonnes')
        print(f"\nAll measurements in: {unit}")
        
        # Category breakdown if available
        if 'category_breakdown' in results:
            print("\nEMISSIONS BY CATEGORY:")
            breakdown = results['category_breakdown']
            
            if 'business_travel' in breakdown:
                bt = breakdown['business_travel']
                print(f"\nBusiness Travel: {bt:.2f} tonnes CO2e")
                print("  Air travel, hotels, rental cars, rail")
                
            if 'employee_commuting' in breakdown:
                ec = breakdown['employee_commuting']
                print(f"\nEmployee Commuting: {ec:.2f} tonnes CO2e")
                print("  Daily travel between home and work")
                
            if 'freight_upstream' in breakdown:
                fu = breakdown['freight_upstream']
                print(f"\nUpstream Freight: {fu:.2f} tonnes CO2e")
                print("  Transportation of purchased goods")
                
            if 'freight_downstream' in breakdown:
                fd = breakdown['freight_downstream']
                print(f"\nDownstream Freight: {fd:.2f} tonnes CO2e")
                print("  Transportation of sold products")
        
        return results
    else:
        print(f"Calculation failed: {response.text}")
        return None

# Step 5: Analyze Transportation Emissions
def analyze_transportation_impact(results):
    """
    I'll analyze your transportation emissions and identify
    the biggest contributors and reduction opportunities.
    """
    
    if not results:
        return
    
    emissions = results.get('emissions', {})
    co2e = emissions.get('CO2e', 0)
    
    print("\nTRANSPORTATION EMISSIONS ANALYSIS")
    print()
    
    # Put emissions in context
    print(f"Your {co2e:.2f} tonnes of transportation CO2e equals:")
    
    # Equivalent comparisons
    cars_annual = co2e / 4.6  # Average car emits 4.6 tonnes/year
    print(f"  - {cars_annual:.1f} cars driven for a year")
    
    flights_nyc_la = co2e / 0.9  # NYC-LA round trip is ~0.9 tonnes
    print(f"  - {flights_nyc_la:.0f} round-trip flights NYC to LA")
    
    # Typical breakdown for office-based company
    print("\nTYPICAL SCOPE 3 TRANSPORTATION BREAKDOWN:")
    print("  Business Air Travel: 40-60% of transport emissions")
    print("  Employee Commuting: 30-45% of transport emissions")
    print("  Freight/Logistics: 10-30% of transport emissions")
    print("  Ground Business Travel: 5-15% of transport emissions")
    
    print("\nKEY INSIGHTS:")
    print("- Air travel often dominates despite being used by few employees")
    print("- Commuting emissions scale with employee count and location")
    print("- Last-mile delivery is the most carbon-intensive freight segment")
    print("- Remote work can significantly reduce commuting emissions")

# Step 6: Provide Reduction Strategies
def provide_reduction_strategies():
    """
    I'll outline practical strategies for reducing each category
    of transportation and distribution emissions.
    """
    
    print("\nTRANSPORTATION EMISSION REDUCTION STRATEGIES")
    print()
    
    print("1. BUSINESS TRAVEL REDUCTIONS")
    print("   Policy Changes:")
    print("   - Implement travel approval thresholds")
    print("   - Mandate economy class for flights under 6 hours")
    print("   - Require virtual meeting consideration first")
    print("   - Set annual travel budgets with carbon limits")
    
    print("\n   Behavioral Changes:")
    print("   - Combine multiple meetings into single trips")
    print("   - Choose direct flights (takeoff/landing use most fuel)")
    print("   - Select rail over air for distances under 500km")
    print("   - Use video conferencing for regular meetings")
    
    print("\n2. EMPLOYEE COMMUTING REDUCTIONS")
    print("   Infrastructure Support:")
    print("   - Provide EV charging stations")
    print("   - Offer secure bicycle storage and showers")
    print("   - Subsidize public transit passes")
    print("   - Create carpooling programs and apps")
    
    print("\n   Policy Support:")
    print("   - Implement hybrid/remote work policies")
    print("   - Offer flexible hours to avoid peak traffic")
    print("   - Provide commuter benefits pre-tax")
    print("   - Locate offices near public transit")
    
    print("\n3. FREIGHT & LOGISTICS OPTIMIZATION")
    print("   Upstream (Suppliers to You):")
    print("   - Consolidate orders to reduce shipments")
    print("   - Choose local suppliers when possible")
    print("   - Specify low-carbon shipping in contracts")
    print("   - Optimize packaging to reduce weight/volume")
    
    print("\n   Downstream (You to Customers):")
    print("   - Offer slower, consolidated shipping options")
    print("   - Use regional distribution centers")
    print("   - Optimize delivery routes with software")
    print("   - Transition to electric delivery vehicles")
    
    print("\n4. MODAL SHIFT OPPORTUNITIES")
    print("   Replace High-Carbon with Low-Carbon Modes:")
    print("   - Air freight → Ocean freight (90% reduction)")
    print("   - Truck → Rail (75% reduction)")
    print("   - Personal car → Public transit (50% reduction)")
    print("   - Taxi → Walking/cycling (100% reduction)")

# Step 7: Compare Scope 1, 2, and 3 Transportation
def explain_scope_differences():
    """
    Let me clarify the important distinctions between transportation
    emissions across all three scopes to avoid confusion.
    """
    
    print("\nUNDERSTANDING TRANSPORTATION ACROSS SCOPES")
    print()
    
    print("SCOPE 1 - Direct Transportation:")
    print("  What: Vehicles YOU own or control")
    print("  Examples:")
    print("  - Company car fleet")
    print("  - Owned delivery trucks")
    print("  - Corporate aircraft")
    print("  Control: Direct - you buy the fuel")
    
    print("\nSCOPE 2 - Electric Transportation:")
    print("  What: Electricity for vehicles YOU own")
    print("  Examples:")
    print("  - Charging company electric vehicles")
    print("  - Electric forklifts in warehouses")
    print("  - Electric company shuttles")
    print("  Control: Indirect - you buy electricity")
    
    print("\nSCOPE 3 - Value Chain Transportation:")
    print("  What: Transportation by OTHERS for your business")
    print("  Examples:")
    print("  - Employee flights on commercial airlines")
    print("  - Employee personal cars for commuting")
    print("  - Third-party shipping and logistics")
    print("  - Customer travel to your locations")
    print("  Control: Influence through policies and choices")
    
    print("\nWHY THE DISTINCTION MATTERS:")
    print("- Avoids double counting between organizations")
    print("- Different reduction strategies for each")
    print("- Scope 3 often largest but hardest to control")
    print("- Complete picture requires all three scopes")

# Step 8: Calculate Potential Reductions
def estimate_reduction_potential(current_emissions):
    """
    I'll estimate potential emission reductions from various
    transportation strategies based on typical achievement rates.
    """
    
    print("\nPOTENTIAL EMISSION REDUCTION SCENARIOS")
    print()
    
    # Reduction strategies and typical impact
    strategies = {
        "30% remote work adoption": 0.10,
        "Travel policy (economy class, approval)": 0.15,
        "20% air-to-rail shift": 0.08,
        "Fleet electrification (downstream)": 0.12,
        "Logistics optimization": 0.10,
        "Public transit incentives": 0.05
    }
    
    print(f"Starting emissions: {current_emissions:.2f} tonnes CO2e")
    print()
    
    cumulative_reduction = 0
    for strategy, reduction_factor in strategies.items():
        reduction = current_emissions * reduction_factor
        cumulative_reduction += reduction
        print(f"{strategy}:")
        print(f"  Potential reduction: {reduction:.2f} tonnes")
        print(f"  Remaining emissions: {current_emissions - reduction:.2f} tonnes")
        print()
    
    # Realistic combined impact (not simply additive)
    realistic_total = current_emissions * 0.35
    print("REALISTIC COMBINED IMPACT:")
    print(f"  Total potential reduction: {realistic_total:.2f} tonnes (35%)")
    print(f"  Achievable emissions: {current_emissions - realistic_total:.2f} tonnes")
    
    print("\nIMPLEMENTATION TIMELINE:")
    print("  Immediate (0-6 months): Travel policies, remote work")
    print("  Short-term (6-12 months): Transit incentives, route optimization")
    print("  Medium-term (1-2 years): Modal shifts, supplier requirements")
    print("  Long-term (2-5 years): Fleet electrification, infrastructure")

# Step 9: Main Orchestration Function
def main():
    """
    Coordinating the complete Scope 3 transportation emissions calculation,
    from authentication through analysis and reduction strategies.
    """
    
    print("SCOPE 3 TRANSPORTATION & DISTRIBUTION EMISSIONS CALCULATOR")
    print("Calculating value chain emissions from business travel,")
    print("commuting, and freight transport")
    print()
    
    # Authenticate
    print("Step 1: Authenticating with emissions API")
    token = get_auth_token()
    
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Calculate emissions
    print("\nStep 2: Calculating transportation emissions")
    results = calculate_transportation_emissions(token)
    
    if results:
        emissions = results.get('emissions', {})
        co2e = emissions.get('CO2e', 0)
        
        # Analyze impact
        print("\nStep 3: Analyzing transportation impact")
        analyze_transportation_impact(results)
        
        # Provide strategies
        print("\nStep 4: Identifying reduction opportunities")
        provide_reduction_strategies()
        
        # Explain scopes
        print("\nStep 5: Understanding scope boundaries")
        explain_scope_differences()
        
        # Estimate reductions
        if co2e > 0:
            print("\nStep 6: Estimating reduction potential")
            estimate_reduction_potential(co2e)
        
        # Key takeaways
        print("\nKEY TAKEAWAYS FOR SCOPE 3 TRANSPORTATION:")
        print()
        print("1. Often represents 5-15% of total corporate emissions")
        print("2. Business air travel typically dominates this category")
        print("3. Commuting emissions vary greatly by location and policy")
        print("4. Reduction requires influencing behavior, not direct control")
        print("5. Success depends on employee engagement and alternatives")
        print()
        print("IMMEDIATE ACTIONS:")
        print("- Conduct employee commute survey")
        print("- Analyze business travel patterns")
        print("- Implement virtual-first meeting policy")
        print("- Set carbon budgets for departments")
        print("- Track and report monthly to build awareness")

# Execute main function
if __name__ == "__main__":
    main()

"""
Setup Instructions:

Create secrets.ini file:

[EI]
api.api_key = your_api_key_here
api.client_id = your_client_id_here

Save at: ../../auth/secrets.ini

Run: python transportation_emissions.py

Understanding Scope 3 Transportation Categories:

Category 4: Upstream transportation and distribution
- Transportation of purchased products between suppliers and company
- Inbound logistics
- Transportation between company facilities

Category 6: Business travel
- Employee transportation for business activities
- In vehicles not owned by the company
- Includes air, rail, rental cars, hotels

Category 7: Employee commuting
- Employee travel between home and work
- All modes of transport
- Can include remote work energy use

Category 9: Downstream transportation and distribution
- Transportation of sold products to customers
- Outbound logistics
- Last-mile delivery

Emission Factors Vary Significantly:

Mode of Transport (g CO2e per tonne-km):
- Air freight: 500-1500
- Truck: 60-150  
- Rail: 10-40
- Ocean freight: 10-40
- Barge: 30-50

Business Travel (g CO2e per passenger-km):
- Domestic flight: 200-300
- International flight: 100-150
- Car: 100-200
- Train: 20-80
- Bus: 20-50

Key Challenges:
- Data collection from employees and suppliers
- Influencing behavior vs direct control
- Balancing business needs with emissions
- Geographic and infrastructure constraints
"""
