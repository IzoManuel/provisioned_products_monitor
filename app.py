#!/usr/bin/python3
import logging
from flask import Flask, render_template
from jinja2 import Environment, FileSystemLoader
from config import *
from provisioned_products_monitor import *

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def stale_provisioned_products():
    try:
        # Initialize Service Catalog client
        sc_client = initialize_service_catalog_client()
        
        # Query provisioned products
        response = query_provisioned_products(sc_client)

        # Get threshold time
        threshold_time = get_threshold_time()
        
        # Fetch user info from S3
        users = fetch_user_info_from_s3()

        # Get stale provisioned products
        stale_products = get_stale_provisioned_products(response, threshold_time)
        
        # Track user launches
        users = track_user_launches(response)
        
        # Check naming convention
        non_conforming_products = check_naming_convention(users, provisioned_products)
        
        # Get unauthorized users
        unauthorized_users = get_unauthorized_users(users, stale_products)

        # Render template with data
        return render_template('dashboard.html', stale_products=stale_products, users=users, non_conforming_products=non_conforming_products, unauthorized_users=unauthorized_users)
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
