"""
Learning to Calculate Scope 2 Market-Based Emissions from Electricity

Learning to calculate market-based emissions from purchased electricity.
While location-based emissions use grid averages, market-based emissions reflect
the specific electricity products you've chosen to purchase - including renewable
energy certificates (RECs), power purchase agreements (PPAs), and green tariffs.

Market-based accounting shows the impact of your energy procurement decisions
and demonstrates how choosing cleaner energy reduces your carbon footprint.
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
    Think of it like using a keycard to get a daily visitor badge.
    """
    

    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    auth_headers = {
        "Content-Type": "application/json"  # Using JSON format
    }
    
    # Credentials to prove I'm authorized
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    # Making the authentication request
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
    Handles request formatting and authentication headers.
    
    Parameters:
    - endpoint: type of calculation (market_based, location_based, etc.)
    - payload: data about electricity consumption and contracts
    - token: authentication token from step 1
    """
    
    # Base URL for emissions API
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    
    # Complete URL with specific endpoint
    full_url = f"{base_url}/{endpoint}"
    
    # Headers with authentication and format
    headers = {
        "Authorization": f"Bearer {token}",  # Access token
        "Content-Type": "application/json"   # Data format
    }
    
    # Making the API call
    print(f"Calling {endpoint} emissions calculation...")
    response = requests.post(full_url, headers=headers, json=payload)
    
    return response

# Step 3: Create Market-Based Emission Parameters
def create_market_based_payload():
    """
    Setting up parameters for market-based electricity emissions.
    Market-based method accounts for any contractual instruments
    you've purchased for electricity - RECs, PPAs, green tariffs, etc.
    This shows the emissions of the specific electricity you chose to buy.
    """
    
    # Building the payload with electricity consumption and contracts
    market_payload = {
        "activity_data": {
            # Identifying this as electricity with specific procurement
            "activity_type": "electricity_consumption_market",
            
            # Total electricity consumption
            "total_consumption": {
                "amount": 100000,              # Total electricity used
                "unit": "kWh",                 # Kilowatt-hours
                "reporting_period": "annual"   # Annual consumption
            },
            
            # Breaking down electricity by procurement type
            # This is what makes it "market-based"
            "electricity_sources": [
                {
                    # Standard grid electricity (no special procurement)
                    "source_type": "grid_mix",
                    "amount": 40000,  # 40% from standard grid
                    "unit": "kWh",
                    "supplier": "Local_Utility",
                    "product_name": "Standard_Grid_Mix",
                    "emission_factor_source": "residual_mix"  # Uses residual mix factor
                },
                {
                    # Green power product from utility
                    "source_type": "green_power_product",
                    "amount": 30000,  # 30% from green tariff
                    "unit": "kWh",
                    "supplier": "Local_Utility",
                    "product_name": "100_Percent_Wind",
                    "certification": "Green-e",  # Third-party certified
                    "emission_factor": 0  # Zero emissions for certified renewable
                },
                {
                    # Renewable Energy Certificates (RECs)
                    "source_type": "unbundled_RECs",
                    "amount": 20000,  # 20% covered by RECs
                    "unit": "kWh",
                    "rec_details": {
                        "vintage_year": 2024,  # Year RECs were generated
                        "technology": "solar",  # Solar, wind, hydro, etc.
                        "location": "In_State",  # Geographic match matters
                        "certification": "Green-e"  # Certification standard
                    },
                    "emission_factor": 0  # RECs claim zero emissions
                },
                {
                    # Power Purchase Agreement (PPA)
                    "source_type": "PPA",
                    "amount": 10000,  # 10% from direct PPA
                    "unit": "kWh",
                    "ppa_details": {
                        "project_name": "Desert_Solar_Farm",
                        "technology": "solar_pv",
                        "location": "Arizona",
                        "additionality": True,  # New renewable capacity
                        "vintage": 2024
                    },
                    "emission_factor": 0  # Direct renewable purchase
                }
            ],
            
            # Facility location (affects residual mix factors)
            "location": {
                "country": "USA",
                "state": "California",
                "zip_code": "94102",
                "grid_region": "CAMX"
            },
            
            # Reporting period
            "time_period": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "reporting_year": 2024
            }
        },
        
        # Market-based specific options
        "calculation_options": {
            "method_type": "market_based",
            "hierarchy_approach": "GHG_Protocol",  # Following GHG Protocol hierarchy
            "residual_mix_source": "Green-e",      # Source for residual factors
            "include_line_losses": True,           # Account for transmission losses
            "certificate_tracking": True           # Track certificate retirement
        }
    }
    
    return market_payload

# Step 4: Calculate Market-Based Emissions
def calculate_market_based_emissions(token):
    """
    Performing the market-based emission calculation.
    This accounts for your specific electricity procurement choices,
    showing how renewable energy purchases reduce your Scope 2 emissions.
    """
    
    # Get configured payload
    payload = create_market_based_payload()
    
    # Call API with market-based data
    response = call_emission_api("market_based", payload, token)
    
    # Process results
    if response.status_code == 200:
        results = response.json()
        
        print("\nMARKET-BASED EMISSION CALCULATION RESULTS")
        print("Scope 2 emissions accounting for energy procurement choices")
        print()
        
        # Extract emissions
        emissions = results.get('emissions', {})
        
        # Total market-based emissions
        co2e = emissions.get('CO2e', 0)
        print(f"Total Market-Based CO2e: {co2e:.3f} metric tonnes")
        print("  This reflects your specific electricity purchasing decisions")
        
        # Breakdown by source (if provided)
        if 'source_breakdown' in emissions:
            print("\nEmissions by Electricity Source:")
            for source in emissions['source_breakdown']:
                source_name = source.get('source_type', 'Unknown')
                source_emissions = source.get('emissions', 0)
                source_amount = source.get('amount', 0)
                print(f"  {source_name}:")
                print(f"    Amount: {source_amount:,} kWh")
                print(f"    Emissions: {source_emissions:.3f} tonnes CO2e")
        
        # Compare to location-based (if provided)
        if 'location_based_equivalent' in results:
            location_based = results['location_based_equivalent']
            reduction = location_based - co2e
            reduction_pct = (reduction / location_based) * 100 if location_based > 0 else 0
            
            print(f"\nComparison to Location-Based Method:")
            print(f"  Location-based emissions: {location_based:.3f} tonnes CO2e")
            print(f"  Market-based emissions: {co2e:.3f} tonnes CO2e")
            print(f"  Reduction achieved: {reduction:.3f} tonnes ({reduction_pct:.1f}%)")
        
        return results
    else:
        print(f"Calculation failed: {response.text}")
        return None

# Step 5: Explain Market-Based Accounting Principles
def explain_market_based_principles():
    """
    Let me explain the key principles and hierarchy of market-based
    Scope 2 accounting according to the GHG Protocol.
    """
    
    print("\nMARKET-BASED ACCOUNTING PRINCIPLES")
    print()
    
    print("GHG PROTOCOL SCOPE 2 QUALITY CRITERIA:")
    print("Contractual instruments must meet ALL these criteria:")
    print("1. Conveyed with purchased energy (bundled) or separately (unbundled)")
    print("2. Tracked and redeemed/retired/cancelled by or on behalf of reporter")
    print("3. As close as possible to period of electricity consumption")
    print("4. From same market where consumption occurs")
    
    print("\nEMISSION FACTOR HIERARCHY (in order of preference):")
    print()
    print("1. Energy Attribute Certificates (Best)")
    print("   - Unbundled RECs, GOs (Guarantees of Origin)")
    print("   - Must be certified, tracked, and retired")
    print("   - Emission factor: 0 for renewable sources")
    
    print("\n2. Power Purchase Agreements (PPAs)")
    print("   - Direct contracts with generators")
    print("   - Physical or virtual PPAs")
    print("   - Best if additional (new capacity)")
    
    print("\n3. Green Power Products")
    print("   - Utility green tariffs")
    print("   - Must be certified (e.g., Green-e)")
    print("   - Supplier-specific emission factors")
    
    print("\n4. Supplier-Specific Factors")
    print("   - Standard utility product emission factors")
    print("   - Must be verified and certified")
    
    print("\n5. Residual Mix (Last Resort)")
    print("   - Grid mix minus claimed renewable energy")
    print("   - Higher than location-based factors")
    print("   - Penalizes not making clean energy choices")
    
    print("\n6. Location-Based Factors (If No Residual Mix)")
    print("   - Same as location-based method")
    print("   - Used when no other data available")

# Step 6: Analyze Procurement Strategy Impact
def analyze_procurement_impact(results):
    """
    I'll analyze how different procurement strategies affect emissions
    and provide recommendations for optimization.
    """
    
    if not results:
        return
    
    emissions = results.get('emissions', {})
    co2e = emissions.get('CO2e', 0)
    
    print("\nANALYZING YOUR ENERGY PROCUREMENT STRATEGY")
    print()
    
    # Example calculations for 100,000 kWh annual consumption
    total_kwh = 100000
    
    print("SCENARIO COMPARISON (for 100,000 kWh):")
    print()
    
    # Different procurement scenarios
    scenarios = {
        "100% Grid (No Action)": {
            "grid": 100, "green": 0, "recs": 0, "ppa": 0,
            "emissions": total_kwh * 0.450 / 1000  # Assuming US average
        },
        "Current Strategy (Mixed)": {
            "grid": 40, "green": 30, "recs": 20, "ppa": 10,
            "emissions": co2e
        },
        "50% Renewable (Moderate)": {
            "grid": 50, "green": 30, "recs": 20, "ppa": 0,
            "emissions": (total_kwh * 0.5 * 0.450) / 1000
        },
        "100% Renewable (Ambitious)": {
            "grid": 0, "green": 40, "recs": 30, "ppa": 30,
            "emissions": 0
        }
    }
    
    for scenario_name, details in scenarios.items():
        print(f"{scenario_name}:")
        print(f"  Grid: {details['grid']}%, Green Tariff: {details['green']}%")
        print(f"  RECs: {details['recs']}%, PPA: {details['ppa']}%")
        print(f"  Emissions: {details['emissions']:.2f} tonnes CO2e")
        print()

# Step 7: Provide Renewable Energy Procurement Guidance
def provide_procurement_guidance():
    """
    I'll explain different renewable energy procurement options
    and their relative benefits for reducing Scope 2 emissions.
    """
    
    print("\nRENEWABLE ENERGY PROCUREMENT OPTIONS")
    print()
    
    print("1. UNBUNDLED RECs (Easiest to Start)")
    print("   Pros:")
    print("   - Easy to purchase in any quantity")
    print("   - Flexible and scalable")
    print("   - Immediate emissions reduction claim")
    print("   Cons:")
    print("   - No additionality guarantee")
    print("   - Price volatility")
    print("   - Less impactful than direct procurement")
    print("   Best for: Quick wins, filling gaps")
    
    print("\n2. GREEN POWER PRODUCTS (Utility Programs)")
    print("   Pros:")
    print("   - Simple billing through utility")
    print("   - Often locally sourced")
    print("   - No capital investment")
    print("   Cons:")
    print("   - Premium pricing")
    print("   - Limited availability")
    print("   - May not drive new renewable development")
    print("   Best for: Small to medium facilities")
    
    print("\n3. POWER PURCHASE AGREEMENTS (Most Impactful)")
    print("   Physical PPAs:")
    print("   - Direct connection to renewable project")
    print("   - Long-term price stability")
    print("   - Drives new renewable development")
    print("   Virtual PPAs:")
    print("   - Financial hedge without physical delivery")
    print("   - Access to best renewable resources")
    print("   - Scalable across locations")
    print("   Best for: Large energy users, long-term commitment")
    
    print("\n4. ON-SITE GENERATION (Maximum Control)")
    print("   Solar/Wind Installation:")
    print("   - Complete control over source")
    print("   - Visible commitment")
    print("   - Potential cost savings")
    print("   - Resilience benefits")
    print("   Best for: Facilities with space and capital")
    
    print("\nKEY DECISION FACTORS:")
    print("- Energy consumption volume")
    print("- Geographic location and grid mix")
    print("- Budget and financial structure")
    print("- Sustainability goals and commitments")
    print("- Stakeholder expectations")

# Step 8: Compare Location vs Market-Based Methods
def compare_accounting_methods():
    """
    I'll clarify when to use location-based versus market-based
    accounting and why both are important for complete reporting.
    """
    
    print("\nLOCATION-BASED VS MARKET-BASED COMPARISON")
    print()
    
    print("WHEN TO USE EACH METHOD:")
    print()
    
    print("Location-Based Method:")
    print("  Purpose: Shows physical emissions from local grid")
    print("  Use when:")
    print("  - No renewable energy purchases")
    print("  - Establishing baseline emissions")
    print("  - Comparing facilities across regions")
    print("  - Required for GHG Protocol dual reporting")
    
    print("\nMarket-Based Method:")
    print("  Purpose: Shows impact of procurement choices")
    print("  Use when:")
    print("  - You purchase renewable energy")
    print("  - Demonstrating climate action")
    print("  - Setting and tracking reduction targets")
    print("  - Stakeholder reporting on sustainability")
    
    print("\nDUAL REPORTING BEST PRACTICES:")
    print("1. Always calculate both methods")
    print("2. Report both transparently")
    print("3. Explain the difference clearly")
    print("4. Use market-based for target setting")
    print("5. Track location-based for grid improvements")
    
    print("\nCOMMON MISCONCEPTIONS:")
    print("- RECs don't physically change your electricity")
    print("- Market-based isn't 'cheating' - it drives renewable investment")
    print("- Location-based shows grid reality, market-based shows your choices")
    print("- Both methods are valid and serve different purposes")

# Step 9: Main Orchestration Function
def main():
    """
    Coordinating the complete market-based emissions calculation,
    from authentication through analysis and strategic recommendations.
    """
    
    print("SCOPE 2 MARKET-BASED EMISSIONS CALCULATOR")
    print("Accounting for renewable energy procurement in emissions")
    print()
    
    # Authenticate
    print("Step 1: Authenticating with emissions API")
    token = get_auth_token()
    
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Calculate emissions
    print("\nStep 2: Calculating market-based emissions")
    results = calculate_market_based_emissions(token)
    
    if results:
        # Explain principles
        print("\nStep 3: Understanding market-based accounting")
        explain_market_based_principles()
        
        # Analyze impact
        print("\nStep 4: Analyzing procurement strategy impact")
        analyze_procurement_impact(results)
        
        # Provide guidance
        print("\nStep 5: Renewable energy procurement options")
        provide_procurement_guidance()
        
        # Compare methods
        print("\nStep 6: Comparing accounting methods")
        compare_accounting_methods()
        
        # Key takeaways
        print("\nKEY TAKEAWAYS FOR MARKET-BASED ACCOUNTING:")
        print()
        print("1. Your energy choices directly impact reported emissions")
        print("2. Quality criteria ensure credible renewable claims")
        print("3. Different procurement options suit different situations")
        print("4. Dual reporting (both methods) provides complete picture")
        print("5. Market-based method rewards renewable energy investment")
        print()
        print("NEXT STEPS:")
        print("- Set renewable energy targets")
        print("- Evaluate procurement options for your situation")
        print("- Track and retire certificates properly")
        print("- Report both location and market-based emissions")
        print("- Consider joining RE100 or similar initiatives")

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

Run: python market_based_emissions.py

Understanding Market-Based Emissions:
Market-based emissions reflect the emissions from electricity that
an organization has purposefully chosen (or not chosen) through
contractual instruments. This includes:

- Renewable Energy Certificates (RECs) in North America
- Guarantees of Origin (GOs) in Europe  
- International RECs (I-RECs) in other markets
- Power Purchase Agreements (PPAs)
- Green power products/green tariffs
- Direct ownership of generation

Key Concepts:
ADDITIONALITY: Whether your purchase drives new renewable development
VINTAGE: The year when renewable energy was generated
GEOGRAPHIC MATCHING: Proximity of generation to consumption
TEMPORAL MATCHING: When generation occurs vs consumption
CERTIFICATION: Third-party verification of renewable claims

Quality Standards:
- Green-e (North America)
- EKOenergy (Europe)
- I-REC Standard (International)

The Residual Mix Factor:
When you don't purchase renewable energy, you get the "residual mix" -
the emissions left after others have claimed the renewable portion.
This is often HIGHER than the location-based grid average!

Supply Chain Note:
While the lesson intro mentioned supply chain emissions, those are
typically Scope 3, not Scope 2. Market-based Scope 2 specifically
refers to purchased electricity, steam, heating, and cooling.
"""
