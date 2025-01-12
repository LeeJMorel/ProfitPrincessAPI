from flask import Flask, request, jsonify
import requests
from config import API_KEY
import csv
from urllib.parse import unquote
import json
from flask_cors import CORS

"""
This app is designed for low user count as it retrieves the income statements 
every time a company is called and it also does not hold more than one 
company income statement at a time. 

This is because our dashboard currently only showcases one company.

To scale up possible options include exploring bulk income statements 
to reduce total API calls, or adding to an array as each income statement 
is fetched to create a temporary database for simple comparative analysis.

Filters and sorting are individual methods for future maintainability and testing.
"""

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

BASE_URL = "https://financialmodelingprep.com"

bulk_profiles = []
current_income = []  # Stores the currently selected company's income statement

@app.before_request
def load_company_profiles():
    """
    Load company profiles on the first request.
    
    Args:
        None
    
    Returns:
        None
    """
        
    if not bulk_profiles:
        fetch_profiles()

def fetch_profiles():
    """
    Fetch and cache bulk company profiles.
    
    Args:
        None
    
    Returns:
        list: A list of company profiles (dictionaries).
    """

    global bulk_profiles
    try:
        profile_url = f"{BASE_URL}/stable/profile-bulk?part=0&apikey={API_KEY}"
        response = requests.get(profile_url)

        if response.status_code == 200:
            csv_data = response.text.splitlines()
            reader = csv.DictReader(csv_data)
            bulk_profiles = [row for row in reader]  # Convert to list of dictionaries
            print(f"Fetched {len(bulk_profiles)} company profiles.")
            return bulk_profiles
        else:
            print("Failed to fetch company profiles.")
            return []
    except Exception as e:
        print(f"Error fetching company profiles: {e}")
        return []

@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    """
    Fetch company profile by symbol.
    
    Args:
        symbol (str): The company symbol to search for.
    
    Returns:
        dict: The company profile if found, or an error message if not found.
    """

    symbol = request.args.get('query')

    if not bulk_profiles:
        fetch_profiles()

    company = next((profile for profile in bulk_profiles if profile['symbol'].strip() == symbol.strip()), None)
    if company:
        print(f"Fetched {company} profile.")
        return jsonify(company), 200
    else:
        return jsonify({"error": "Company not found"}), 404
    
@app.route('/fetch-income', methods=['GET'])
def fetch_income():
    """
    Fetch income statement for a specific company.
    
    Args:
        symbol (str): The company symbol to retrieve income statement for.
    
    Returns:
        dict: The income statement if found, or an error message if not found.
    """

    global current_income
    symbol = request.args.get('query')
    
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400

    try:
        income_statement_url = f"{BASE_URL}/api/v3/income-statement/{symbol}?period=annual&apikey={API_KEY}"
        response = requests.get(income_statement_url)
        
        if response.status_code == 200:
            current_income = response.json()
            print(f"Income statement for {symbol} successfully loaded.")
            return jsonify(current_income), 200
        else:
            print(f"Failed to fetch income statement for {symbol}.")
            return jsonify({"error": "Failed to fetch income statement"}), 404
    except Exception as e:
        print(f"Error fetching income statement: {e}")
        return jsonify({"error": "Internal server error"}), 500

def filter_income(data, filter_fields):
    """
    Filters income statement data based on provided filter fields.
    
    Args:
        data (List[dict]): The dataset to filter (income statements).
        filter_fields (dict): Dictionary of fields (e.g., 'revenue', 'date') with [min, max] ranges.
    
    Returns:
        List[dict]: Filtered dataset that matches the given conditions.
    
    Notes:
        - Numeric fields (e.g., 'revenue', 'netIncome') are filtered based on the given range.
        - 'Date' is filtered by year (converted from "YYYY-MM-DD").
        - Fields not in the data are skipped.
    """
        
    filtered_data = data[:]
    
    for field, value in filter_fields.items():
        if field.endswith("_min"):
            base_field = field[:-4]  
            min_value = value
            max_value = filter_fields.get(f"{base_field}_max")
            if max_value is not None:
                if base_field == "date":
                    # Extract year from date strings
                    min_year = min_value
                    max_year = max_value
                    filtered_data = [
                        record for record in filtered_data
                        if min_year <= int(record.get(base_field, "0000-00-00")[:4]) <= max_year
                    ]
                else:
                    # Handle numeric fields
                    filtered_data = [
                        record for record in filtered_data
                        if min_value <= record.get(base_field, float('inf')) <= max_value
                    ]
        elif field.endswith("_max"):
            continue 
            
    return filtered_data


def sort_income(data, field, ascending=True):
    """
    Sort the income statement by the specified field.
    
    Args:
        data (List[dict]): The dataset to sort.
        field (str): The field to sort by (any valid field in the income statement).
        ascending (bool): Whether to sort in ascending order. Default is True.
    
    Returns:
        List[dict]: Sorted income statement.
    """
    
    if not data:
        return []
    
    if field not in data[0]:
        raise ValueError(f"Invalid field '{field}'. Please provide a valid field name.")

    return sorted(
        data,
        key=lambda x: (
            int(x[field][:4]) if field == 'date' and isinstance(x[field], str) else x[field]
        ),
        reverse=not ascending
    )

@app.route('/filter-sort-income', methods=['GET'])
def filter_sort_income():
    """
    Endpoint to filter and sort income statements based on user input.
    
    Expects JSON payload with optional parameters:
        - sort_field (str): Field to sort by ('date', 'revenue', 'netIncome').
        - ascending (bool): Sort order, default is ascending.
        - fields (dict): Dictionary of fields with min/max ranges to filter by. 
          Example: {"revenue": [min_value, max_value], "netIncome": [min_value, max_value], "date": [min_year, max_year]}.
    
    Returns:
        JSON: Filtered and sorted income statements.
    """

    global current_income
    params = request.args.get('query')
    
    if not params:
        return jsonify({"error": "Params required"}), 400

    try:
        # Parse the query string into a dictionary
        params_dict = json.loads(params)

        # Extract query parameters
        sort_field = params_dict.get('sort_field')
        ascending = params_dict.get('ascending', True)
        filter_fields = params_dict.get('fields', {})

        filtered_data = current_income[:]  # Start with the full dataset
        
        filtered_data = filter_income(current_income, filter_fields)
        
        if sort_field:
            filtered_data = sort_income(filtered_data, sort_field, ascending)
        
        return jsonify(filtered_data), 200
    
    except Exception as e:
        print(f"Error in filter_sort_income: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400



if __name__ == '__main__':
    app.run()
