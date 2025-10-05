"""
Corporate GHG Emissions Calculator 

"""

import requests  # For API communications
import json      # For data formatting
import configparser  # For secure credential management
from datetime import datetime  # For time-based calculations
from typing import Dict, List, Tuple  # For type hints


config = configparser.ConfigParser()
config.read('../../auth/secrets.ini')
API_KEY = config['EI']['api.api_key']
CLIENT_ID = config['EI']['api.client_id']

# Step 1: Universal Authentication
def get_auth_token():
    """
    Authenticating once for all emissions calculations.
    This single token works across all scope calculations.
    """
    
    auth_url = "https://api.emissions.ibm.com/v1/auth/token"
    
    auth_headers = {
        "Content-Type": "application/json"
    }
    
    auth_data = {
        "api_key": API_KEY,
        "client_id": CLIENT_ID
    }
    
    print("Authenticating with emissions API...")
    response = requests.post(auth_url, headers=auth_headers, json=auth_data)
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print("Authentication successful")
        return token
    else:
        print(f"Authentication failed: {response.text}")
        return None

# Step 2: Universal API Caller
def call_emission_api(endpoint, payload, token):
    """
    Single function to call any emission calculation endpoint.
    This handles all scopes with appropriate routing.
    """
    
    base_url = "https://api.emissions.ibm.com/v1/emissions"
    full_url = f"{base_url}/{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(full_url, headers=headers, json=payload)
    return response

# Step 3: Comprehensive Scope 1 Calculations
def calculate_scope1_emissions(token, company_data):
    """
    Calculating all Scope 1 emissions - direct emissions from sources
    you own or control. This includes stationary combustion, mobile
    combustion, fugitive emissions, and process emissions.
    """
    
    print("\n" + "="*60)
    print("CALCULATING SCOPE 1 - DIRECT EMISSIONS")
    print("="*60)
    
    scope1_total = 0
    scope1_breakdown = {}
    
    # Stationary Combustion (boilers, furnaces, generators)
    print("\nCalculating stationary combustion...")
    stationary_payload = {
        "activity_data": {
            "activity_type": "stationary_combustion",
            "fuel_consumption": {
                "fuel_type": company_data.get("heating_fuel", "natural_gas"),
                "fuel_amount": company_data.get("heating_fuel_amount", 50000),
                "fuel_unit": "therms",
                "equipment_type": "boiler"
            },
            "location": company_data.get("location", {"country": "USA", "state": "California"})
        }
    }
    
    response = call_emission_api("stationary", stationary_payload, token)
    if response.status_code == 200:
        stationary_emissions = response.json()['emissions']['CO2e']
        scope1_breakdown['stationary_combustion'] = stationary_emissions
        scope1_total += stationary_emissions
        print(f"  Stationary combustion: {stationary_emissions:.2f} tonnes CO2e")
    
    # Mobile Combustion (owned vehicles)
    print("Calculating mobile combustion...")
    mobile_payload = {
        "activity_data": {
            "activity_type": "mobile_combustion",
            "fuel_data": {
                "fuel_type": "gasoline",
                "fuel_amount": company_data.get("fleet_fuel", 10000),
                "fuel_unit": "gallons"
            },
            "vehicle_info": {
                "vehicle_count": company_data.get("fleet_size", 10),
                "vehicle_type": "delivery_van"
            }
        }
    }
    
    response = call_emission_api("mobile", mobile_payload, token)
    if response.status_code == 200:
        mobile_emissions = response.json()['emissions']['CO2e']
        scope1_breakdown['mobile_combustion'] = mobile_emissions
        scope1_total += mobile_emissions
        print(f"  Mobile combustion: {mobile_emissions:.2f} tonnes CO2e")
    
    # Fugitive Emissions (refrigerant leaks)
    print("Calculating fugitive emissions...")
    fugitive_payload = {
        "activity_data": {
            "activity_type": "fugitive_emission",
            "gas": {
                "gas_type": "R-410A",
                "gas_amount": company_data.get("refrigerant_leakage", 5),
                "gas_unit": "kg"
            }
        }
    }
    
    response = call_emission_api("fugitive", fugitive_payload, token)
    if response.status_code == 200:
        fugitive_emissions = response.json()['emissions']['CO2e']
        scope1_breakdown['fugitive'] = fugitive_emissions
        scope1_total += fugitive_emissions
        print(f"  Fugitive emissions: {fugitive_emissions:.2f} tonnes CO2e")
    
    print(f"\nTOTAL SCOPE 1: {scope1_total:.2f} tonnes CO2e")
    
    return scope1_total, scope1_breakdown

# Step 4: Comprehensive Scope 2 Calculations
def calculate_scope2_emissions(token, company_data):
    """
    Calculating all Scope 2 emissions - indirect emissions from
    purchased electricity, steam, heating, and cooling. I'll calculate
    both location-based and market-based methods.
    """
    
    print("\n" + "="*60)
    print("CALCULATING SCOPE 2 - PURCHASED ENERGY EMISSIONS")
    print("="*60)
    
    electricity_kwh = company_data.get("electricity_consumption", 500000)
    
    # Location-Based Method
    print("\nCalculating location-based emissions...")
    location_payload = {
        "activity_data": {
            "activity_type": "electricity_consumption",
            "electricity_usage": {
                "consumption_amount": electricity_kwh,
                "consumption_unit": "kWh"
            },
            "location": company_data.get("location", {"country": "USA", "state": "California"})
        },
        "calculation_method": {
            "method_type": "location_based"
        }
    }
    
    response = call_emission_api("location_based", location_payload, token)
    location_based = 0
    if response.status_code == 200:
        location_based = response.json()['emissions']['CO2e']
        print(f"  Location-based: {location_based:.2f} tonnes CO2e")
    
    # Market-Based Method
    print("Calculating market-based emissions...")
    renewable_percentage = company_data.get("renewable_energy_percent", 30)
    
    market_payload = {
        "activity_data": {
            "activity_type": "electricity_consumption_market",
            "total_consumption": {
                "amount": electricity_kwh,
                "unit": "kWh"
            },
            "electricity_sources": [
                {
                    "source_type": "grid_mix",
                    "amount": electricity_kwh * (1 - renewable_percentage/100),
                    "unit": "kWh"
                },
                {
                    "source_type": "renewable_energy_certificates",
                    "amount": electricity_kwh * (renewable_percentage/100),
                    "unit": "kWh",
                    "emission_factor": 0
                }
            ]
        }
    }
    
    response = call_emission_api("market_based", market_payload, token)
    market_based = 0
    if response.status_code == 200:
        market_based = response.json()['emissions']['CO2e']
        print(f"  Market-based: {market_based:.2f} tonnes CO2e")
    
    print(f"\nTOTAL SCOPE 2:")
    print(f"  Location-based: {location_based:.2f} tonnes CO2e")
    print(f"  Market-based: {market_based:.2f} tonnes CO2e")
    
    return location_based, market_based

# Step 5: Comprehensive Scope 3 Calculations
def calculate_scope3_emissions(token, company_data):
    """
    Calculating Scope 3 emissions - all indirect value chain emissions.
    The GHG Protocol defines 15 categories of Scope 3. I'll calculate
    the most common and significant ones.
    """
    
    print("\n" + "="*60)
    print("CALCULATING SCOPE 3 - VALUE CHAIN EMISSIONS")
    print("="*60)
    
    scope3_total = 0
    scope3_breakdown = {}
    
    # Category 1: Purchased Goods and Services
    print("\nCategory 1: Purchased goods and services...")
    annual_spend = company_data.get("annual_procurement_spend", 5000000)
    # Using spend-based method with average emission factors
    purchased_goods = annual_spend * 0.00035  # Average kg CO2e per dollar
    scope3_breakdown['purchased_goods'] = purchased_goods
    scope3_total += purchased_goods
    print(f"  Estimated: {purchased_goods:.2f} tonnes CO2e")
    
    # Category 2: Capital Goods
    print("Category 2: Capital goods...")
    capital_spend = company_data.get("capital_expenditure", 1000000)
    capital_goods = capital_spend * 0.00045  # Higher factor for capital goods
    scope3_breakdown['capital_goods'] = capital_goods
    scope3_total += capital_goods
    print(f"  Estimated: {capital_goods:.2f} tonnes CO2e")
    
    # Category 3: Fuel and Energy Related (not in Scope 1 or 2)
    print("Category 3: Fuel and energy related activities...")
    # Well-to-tank emissions for Scope 1 fuels and T&D losses for electricity
    fuel_energy = (scope3_breakdown.get('stationary_combustion', 0) * 0.2)  # 20% WTT
    scope3_breakdown['fuel_energy_related'] = fuel_energy
    scope3_total += fuel_energy
    print(f"  Estimated: {fuel_energy:.2f} tonnes CO2e")
    
    # Category 4: Upstream Transportation
    print("Category 4: Upstream transportation...")
    upstream_transport = annual_spend * 0.00008  # Transport factor
    scope3_breakdown['upstream_transport'] = upstream_transport
    scope3_total += upstream_transport
    print(f"  Estimated: {upstream_transport:.2f} tonnes CO2e")
    
    # Category 5: Waste Generated
    print("Category 5: Waste generated in operations...")
    employees = company_data.get("employee_count", 100)
    waste_emissions = employees * 0.2  # 0.2 tonnes per employee annually
    scope3_breakdown['waste'] = waste_emissions
    scope3_total += waste_emissions
    print(f"  Estimated: {waste_emissions:.2f} tonnes CO2e")
    
    # Category 6: Business Travel
    print("Category 6: Business travel...")
    business_travel_payload = {
        "activity_data": {
            "activity_type": "business_travel",
            "air_travel": {
                "total_miles": company_data.get("annual_air_miles", 500000),
                "class_mix": "economy"
            }
        }
    }
    
    response = call_emission_api("business_travel", business_travel_payload, token)
    if response.status_code == 200:
        business_travel = response.json()['emissions']['CO2e']
    else:
        business_travel = company_data.get("annual_air_miles", 500000) * 0.00015
    
    scope3_breakdown['business_travel'] = business_travel
    scope3_total += business_travel
    print(f"  Calculated: {business_travel:.2f} tonnes CO2e")
    
    # Category 7: Employee Commuting
    print("Category 7: Employee commuting...")
    avg_commute_miles = company_data.get("avg_commute_miles", 20)
    working_days = 220
    commuting = employees * avg_commute_miles * working_days * 0.0004
    scope3_breakdown['commuting'] = commuting
    scope3_total += commuting
    print(f"  Estimated: {commuting:.2f} tonnes CO2e")
    
    # Category 11: Use of Sold Products (if applicable)
    print("Category 11: Use of sold products...")
    if company_data.get("sells_energy_using_products", False):
        products_sold = company_data.get("products_sold", 10000)
        product_lifetime_energy = company_data.get("product_lifetime_kwh", 1000)
        use_of_products = products_sold * product_lifetime_energy * 0.0004
        scope3_breakdown['use_of_products'] = use_of_products
        scope3_total += use_of_products
        print(f"  Estimated: {use_of_products:.2f} tonnes CO2e")
    else:
        print("  Not applicable")
    
    # Category 12: End-of-Life Treatment
    print("Category 12: End-of-life treatment of sold products...")
    if company_data.get("sells_physical_products", False):
        product_weight = company_data.get("annual_product_weight_tonnes", 100)
        end_of_life = product_weight * 0.5  # Average disposal factor
        scope3_breakdown['end_of_life'] = end_of_life
        scope3_total += end_of_life
        print(f"  Estimated: {end_of_life:.2f} tonnes CO2e")
    else:
        print("  Not applicable")
    
    print(f"\nTOTAL SCOPE 3: {scope3_total:.2f} tonnes CO2e")
    
    return scope3_total, scope3_breakdown

# Step 6: Comprehensive Analysis
def analyze_complete_footprint(scope1, scope2_location, scope2_market, scope3, breakdowns):
    """
    Now I'll analyze your complete carbon footprint across all scopes
    and provide insights about your emissions profile.
    """
    
    print("\n" + "="*60)
    print("COMPLETE CARBON FOOTPRINT ANALYSIS")
    print("="*60)
    
    # Total emissions (using location-based for Scope 2)
    total_location = scope1 + scope2_location + scope3
    total_market = scope1 + scope2_market + scope3
    
    print(f"\nTOTAL EMISSIONS:")
    print(f"  With location-based Scope 2: {total_location:.2f} tonnes CO2e")
    print(f"  With market-based Scope 2: {total_market:.2f} tonnes CO2e")
    
    # Scope breakdown
    print(f"\nSCOPE BREAKDOWN (using location-based):")
    scope1_pct = (scope1 / total_location) * 100
    scope2_pct = (scope2_location / total_location) * 100
    scope3_pct = (scope3 / total_location) * 100
    
    print(f"  Scope 1: {scope1:.2f} tonnes ({scope1_pct:.1f}%)")
    print(f"  Scope 2: {scope2_location:.2f} tonnes ({scope2_pct:.1f}%)")
    print(f"  Scope 3: {scope3:.2f} tonnes ({scope3_pct:.1f}%)")
    
    # Visual representation
    print("\nEMISSION DISTRIBUTION:")
    print("  " + "█" * int(scope1_pct/2) + f" Scope 1 ({scope1_pct:.1f}%)")
    print("  " + "▓" * int(scope2_pct/2) + f" Scope 2 ({scope2_pct:.1f}%)")
    print("  " + "░" * int(scope3_pct/2) + f" Scope 3 ({scope3_pct:.1f}%)")
    
    # Identify hotspots
    print("\nEMISSION HOTSPOTS (top 5 categories):")
    all_categories = []
    
    # Combine all emission sources
    for category, amount in breakdowns['scope1'].items():
        all_categories.append(("Scope 1 - " + category, amount))
    all_categories.append(("Scope 2 - Electricity", scope2_location))
    for category, amount in breakdowns['scope3'].items():
        all_categories.append(("Scope 3 - " + category, amount))
    
    # Sort and display top 5
    all_categories.sort(key=lambda x: x[1], reverse=True)
    for i, (category, amount) in enumerate(all_categories[:5], 1):
        pct = (amount / total_location) * 100
        print(f"  {i}. {category}: {amount:.2f} tonnes ({pct:.1f}%)")
    
    # Benchmark comparisons
    print("\nINDUSTRY COMPARISONS:")
    employees = 100  # Default assumption
    intensity = total_location / employees
    
    print(f"  Your intensity: {intensity:.2f} tonnes CO2e per employee")
    print(f"  Industry benchmarks:")
    print(f"    Tech/Office: 2-5 tonnes/employee")
    print(f"    Manufacturing: 10-50 tonnes/employee")
    print(f"    Retail: 5-15 tonnes/employee")
    print(f"    Logistics: 20-100 tonnes/employee")
    
    # Equivalencies
    print("\nCONTEXT EQUIVALENCIES:")
    print(f"  Your {total_location:.0f} tonnes equals:")
    
    cars = total_location / 4.6
    print(f"    - {cars:.0f} cars driven for a year")
    
    homes = total_location / 8.5
    print(f"    - Energy for {homes:.0f} homes for a year")
    
    trees = total_location / 0.025
    print(f"    - CO2 absorbed by {trees:.0f} trees annually")
    
    flights = total_location / 0.9
    print(f"    - {flights:.0f} round-trip flights NYC to LA")
    
    return total_location, total_market

# Step 7: Science-Based Targets and Pathways
def calculate_reduction_pathway(total_emissions):
    """
    I'll calculate science-based reduction targets aligned with
    limiting global warming to 1.5°C as per the Paris Agreement.
    """
    
    print("\n" + "="*60)
    print("SCIENCE-BASED REDUCTION PATHWAY")
    print("="*60)
    
    # Science-based target: 4.2% annual reduction for 1.5°C
    annual_reduction_rate = 0.042
    
    print("\n1.5°C ALIGNED TARGETS:")
    print(f"  Current emissions: {total_emissions:.2f} tonnes CO2e")
    
    # Calculate targets
    years = [1, 3, 5, 10]
    for year in years:
        target = total_emissions * ((1 - annual_reduction_rate) ** year)
        reduction = total_emissions - target
        reduction_pct = (reduction / total_emissions) * 100
        print(f"  Year {year}: {target:.2f} tonnes (reduce {reduction:.2f} tonnes / {reduction_pct:.1f}%)")
    
    # Net Zero pathway
    print("\nNET ZERO PATHWAY:")
    print("  Near-term: 50% reduction by 2030")
    target_2030 = total_emissions * 0.5
    print(f"    2030 target: {target_2030:.2f} tonnes")
    
    print("  Long-term: 90% reduction by 2050")
    target_2050 = total_emissions * 0.1
    print(f"    2050 target: {target_2050:.2f} tonnes")
    print(f"    Residual emissions to offset: {target_2050:.2f} tonnes")
    
    # Annual action required
    years_to_2030 = 6  # Assuming current year is 2024
    annual_reduction_2030 = (total_emissions - target_2030) / years_to_2030
    
    print(f"\nANNUAL ACTION REQUIRED:")
    print(f"  Must reduce {annual_reduction_2030:.2f} tonnes per year until 2030")
    print(f"  That's {annual_reduction_2030/12:.2f} tonnes per month")
    print(f"  Or {annual_reduction_2030/52:.2f} tonnes per week")
    
    return target_2030, target_2050

# Step 8: Prioritized Reduction Roadmap
def create_reduction_roadmap(scope1, scope2, scope3, breakdowns):
    """
    I'll create a prioritized roadmap for emission reductions
    based on impact, feasibility, and cost-effectiveness.
    """
    
    print("\n" + "="*60)
    print("PRIORITIZED REDUCTION ROADMAP")
    print("="*60)
    
    print("\nQUICK WINS (0-6 months):")
    print("High impact, low cost, immediate implementation")
    print()
    print("1. Energy Efficiency:")
    print("   - LED lighting upgrade (10-15% of electricity)")
    print("   - HVAC optimization (20-30% of heating/cooling)")
    print("   - Equipment scheduling and shutdown protocols")
    potential_1 = scope2 * 0.20
    print(f"   Potential reduction: {potential_1:.2f} tonnes")
    
    print("\n2. Travel Policies:")
    print("   - Virtual-first meeting policy")
    print("   - Economy class mandate for flights")
    print("   - Approval thresholds for travel")
    potential_2 = breakdowns['scope3'].get('business_travel', 0) * 0.30
    print(f"   Potential reduction: {potential_2:.2f} tonnes")
    
    print("\nMEDIUM-TERM INITIATIVES (6-18 months):")
    print("Moderate investment, significant impact")
    print()
    print("3. Renewable Energy:")
    print("   - Purchase renewable energy certificates")
    print("   - Switch to green utility tariff")
    print("   - Install solar panels (if feasible)")
    potential_3 = scope2 * 0.50
    print(f"   Potential reduction: {potential_3:.2f} tonnes")
    
    print("\n4. Fleet Transition:")
    print("   - Begin transitioning to electric vehicles")
    print("   - Implement route optimization")
    print("   - Driver efficiency training")
    potential_4 = breakdowns['scope1'].get('mobile_combustion', 0) * 0.40
    print(f"   Potential reduction: {potential_4:.2f} tonnes")
    
    print("\nLONG-TERM TRANSFORMATIONS (18+ months):")
    print("Strategic changes, highest impact")
    print()
    print("5. Supply Chain Engagement:")
    print("   - Supplier sustainability requirements")
    print("   - Local sourcing initiatives")
    print("   - Circular economy practices")
    potential_5 = breakdowns['scope3'].get('purchased_goods', 0) * 0.25
    print(f"   Potential reduction: {potential_5:.2f} tonnes")
    
    print("\n6. Building Upgrades:")
    print("   - Deep energy retrofits")
    print("   - Electrification of heating")
    print("   - On-site renewable generation")
    potential_6 = breakdowns['scope1'].get('stationary_combustion', 0) * 0.60
    print(f"   Potential reduction: {potential_6:.2f} tonnes")
    
    total_potential = sum([potential_1, potential_2, potential_3, 
                          potential_4, potential_5, potential_6])
    
    print(f"\nTOTAL REDUCTION POTENTIAL: {total_potential:.2f} tonnes")
    print(f"Approximately {(total_potential/(scope1+scope2+scope3))*100:.1f}% reduction achievable")

# Step 9: Cost-Benefit Analysis
def analyze_costs_and_benefits(total_emissions):
    """
    I'll provide a rough cost-benefit analysis of emission
    reduction strategies to help prioritize investments.
    """
    
    print("\n" + "="*60)
    print("COST-BENEFIT ANALYSIS")
    print("="*60)
    
    # Carbon pricing context
    print("\nCARBON PRICING CONTEXT:")
    print("  EU ETS price: ~$80-100/tonne CO2e")
    print("  California cap-and-trade: ~$30-40/tonne")
    print("  Voluntary offset market: ~$10-50/tonne")
    print("  Internal carbon price (best practice): $50-100/tonne")
    
    carbon_price = 50  # Conservative estimate
    annual_carbon_cost = total_emissions * carbon_price
    
    print(f"\nYour potential carbon liability:")
    print(f"  At $50/tonne: ${annual_carbon_cost:,.0f} annually")
    print(f"  At $100/tonne: ${annual_carbon_cost*2:,.0f} annually")
    
    # ROI of reduction strategies
    print("\nRETURN ON INVESTMENT BY STRATEGY:")
    
    strategies = [
        {
            "name": "LED Lighting",
            "cost": 50000,
            "annual_savings": 15000,
            "emission_reduction": 50,
            "payback_years": 3.3
        },
        {
            "name": "Solar Installation",
            "cost": 500000,
            "annual_savings": 75000,
            "emission_reduction": 200,
            "payback_years": 6.7
        },
        {
            "name": "Fleet Electrification",
            "cost": 200000,
            "annual_savings": 30000,
            "emission_reduction": 100,
            "payback_years": 6.7
        },
        {
            "name": "Building Insulation",
            "cost": 100000,
            "annual_savings": 20000,
            "emission_reduction": 75,
            "payback_years": 5.0
        }
    ]
    
    for strategy in strategies:
        carbon_value = strategy["emission_reduction"] * carbon_price
        total_annual_value = strategy["annual_savings"] + carbon_value
        
        print(f"\n{strategy['name']}:")
        print(f"  Investment: ${strategy['cost']:,}")
        print(f"  Energy savings: ${strategy['annual_savings']:,}/year")
        print(f"  Carbon value: ${carbon_value:,}/year (@$50/tonne)")
        print(f"  Total value: ${total_annual_value:,}/year")
        print(f"  Payback period: {strategy['payback_years']:.1f} years")
    
    print("\nADDITIONAL BENEFITS (not quantified above):")
    print("  - Enhanced brand reputation")
    print("  - Employee attraction and retention")
    print("  - Risk mitigation (regulatory/physical)")
    print("  - Customer preference and loyalty")
    print("  - Access to green financing")
    print("  - Supply chain resilience")

# Step 10: Main Orchestration
def main():
    """
    This is the main function that orchestrates the complete
    corporate carbon footprint calculation across all scopes.
    """
    
    print("COMPREHENSIVE CORPORATE GHG EMISSIONS CALCULATOR")
    print("Calculating your complete carbon footprint across all scopes")
    print()
    
    # Example company data (in reality, this would be input by user)
    company_data = {
        # Basic info
        "company_name": "Example Corp",
        "industry": "Technology",
        "employee_count": 100,
        "location": {"country": "USA", "state": "California"},
        
        # Scope 1 data
        "heating_fuel": "natural_gas",
        "heating_fuel_amount": 50000,  # therms
        "fleet_size": 10,
        "fleet_fuel": 10000,  # gallons
        "refrigerant_leakage": 5,  # kg
        
        # Scope 2 data
        "electricity_consumption": 500000,  # kWh
        "renewable_energy_percent": 30,
        
        # Scope 3 data
        "annual_procurement_spend": 5000000,  # dollars
        "capital_expenditure": 1000000,
        "annual_air_miles": 500000,
        "avg_commute_miles": 20,
        "sells_energy_using_products": False,
        "sells_physical_products": False
    }
    
    # Authenticate
    print("Step 1: Authenticating...")
    token = get_auth_token()
    
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Calculate all scopes
    print("\nStep 2: Calculating emissions across all scopes...")
    
    scope1, scope1_breakdown = calculate_scope1_emissions(token, company_data)
    scope2_location, scope2_market = calculate_scope2_emissions(token, company_data)
    scope3, scope3_breakdown = calculate_scope3_emissions(token, company_data)
    
    # Store breakdowns
    breakdowns = {
        'scope1': scope1_breakdown,
        'scope3': scope3_breakdown
    }
    
    # Analyze complete footprint
    print("\nStep 3: Analyzing complete footprint...")
    total_location, total_market = analyze_complete_footprint(
        scope1, scope2_location, scope2_market, scope3, breakdowns
    )
    
    # Calculate reduction pathway
    print("\nStep 4: Setting science-based targets...")
    target_2030, target_2050 = calculate_reduction_pathway(total_location)
    
    # Create roadmap
    print("\nStep 5: Creating reduction roadmap...")
    create_reduction_roadmap(scope1, scope2_location, scope3, breakdowns)
    
    # Analyze costs and benefits
    print("\nStep 6: Analyzing costs and benefits...")
    analyze_costs_and_benefits(total_location)
    
    # Final summary
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    
    print(f"\nYOUR CARBON FOOTPRINT:")
    print(f"  Total: {total_location:.2f} tonnes CO2e")
    print(f"  Per employee: {total_location/company_data['employee_count']:.2f} tonnes")
    
    print(f"\nKEY FINDINGS:")
    print(f"  - Scope 3 represents {(scope3/total_location)*100:.1f}% of total emissions")
    print(f"  - Renewable energy reduces Scope 2 by {((scope2_location-scope2_market)/scope2_location)*100:.1f}%")
    print(f"  - Quick wins could reduce emissions by ~20% in 6 months")
    
    print(f"\nRECOMMENDED NEXT STEPS:")
    print("  1. Set science-based targets publicly")
    print("  2. Implement quick wins immediately")
    print("  3. Develop detailed Scope 3 inventory")
    print("  4. Engage suppliers on emissions")
    print("  5. Report progress quarterly")
    
    print(f"\nCLIMATE ACTION IS URGENT:")
    print("  Every tonne reduced matters.")
    print("  Start today, improve continuously.")
    print("  Your actions inspire others.")
    
    print("\n" + "="*60)
    print("Thank you for calculating your complete carbon footprint!")
    print("Remember: You can't manage what you don't measure.")
    print("="*60)

# Execute the calculator
if __name__ == "__main__":
    main()

"""
Comprehensive Emissions Calculator Setup:

Create secrets.ini:
[EI]
api.api_key = your_api_key_here
api.client_id = your_client_id_here

Save at: ../../auth/secrets.ini
Run: python comprehensive_emissions_calculator.py

Understanding Your Complete Footprint:

SCOPE 1 (Direct): 5-10% typical
- You burn the fuel
- You own the equipment
- You have direct control

SCOPE 2 (Energy): 10-20% typical
- You purchase electricity
- Someone else generates it
- You control through purchasing

SCOPE 3 (Value Chain): 70-85% typical
- Others emit for your business
- Upstream and downstream
- You influence through engagement

The Importance of All Three Scopes:
- Complete picture of climate impact
- Identifies all reduction opportunities
- Prevents emissions shifting between scopes
- Required for net-zero commitments
- Builds stakeholder trust

Remember: Most emissions hide in Scope 3!
"""
