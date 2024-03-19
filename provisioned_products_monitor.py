#!/usr/bin/env python3

import os
import boto3
import requests
import logging
from datetime import datetime, timedelta, timezone
import json
from dotenv import load_dotenv
from config import *

logging.basicConfig(level=logging.INFO)

def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog', region_name='ap-south-1')

def get_threshold_time(hours=STALE_PRODUCT_THRESHOLD_HOURS):
    """Return the time threshold."""
    return datetime.now(timezone.utc) - timedelta(hours=hours)

def query_provisioned_products(sc_client):
    """Query provisioned products."""
    try:
        load_dotenv()  # Load environment variables from .env file
        environment = os.getenv('ENV')

        if environment == 'local':
            # Load provisioned products from JSON file
            with open('provisioned_products.json', 'r') as file:
                response = json.load(file)
        else:
            # Query provisioned products from AWS Service Catalog API
            response = sc_client.search_provisioned_products()
        
        # Convert datetime strings to datetime objects
        for product in response['ProvisionedProducts']:
            created_time = product['CreatedTime']
            if isinstance(created_time, str):
                product['CreatedTime'] = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        
        return response
    except Exception as e:
        logging.error(f"Error querying provisioned products: {e}")
        return None


def fetch_user_info_from_s3():
    """Fetch user information from either S3 or a local JSON file."""
    try:
        # Load environment variables
        load_dotenv()

        # Check if running locally or in production
        environment = os.getenv('ENV')

        if environment == 'local':
            # Load user information from a local JSON file
            with open('user_info.json', 'r') as file:
                user_info = json.load(file)
        else:
            # Fetch user information from S3
            s3_client = boto3.client('s3')
            bucket_name = 'dg-cohort-01'
            file_key = 'team_israel_users_info.json'
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            user_info = json.loads(response['Body'].read().decode('utf-8'))
        
        return user_info
    except Exception as e:
        logging.error(f"Error fetching user info: {e}")
        return None

def send_slack_notification(webhook_url, message_content):
    """Send a notification via Slack."""
    message_payload = {"text": f"```\n{json.dumps(message_content, indent=4)}\n```"}
    try:
        response = requests.post(webhook_url, json=message_payload)
        if response.status_code == 200:
            logging.info('Slack message sent successfully')
        else:
            logging.error(f'Failed to send Slack message, status code: {response.status_code}')
    except Exception as e:
        logging.error(f"Error sending Slack notification: {e}")


def get_duration_in_days(duration_hours):
    """Return the duration in days."""
    if duration_hours >= 24:
        duration_days = duration_hours / 24
        # Display duration in days
        return f"{int(duration_days)} day{'s' if duration_days > 1 else ''}"
    else:
        return f"{duration_hours:.2f} hours"  # Display duration in hours
        
def track_user_launches(response, threshold=HIGH_PRODUCT_COUNT_THRESHOLD):
    """Count the number of provisioned products for each user."""
    users = []

    # Create a dictionary to store the count for each user
    user_products = {}

    # Loop through the provisioned products and count the number for each user
    for product_view_detail in response['ProvisionedProducts']:
        user_arn_session = product_view_detail['UserArnSession']
        user_info = extract_user_info(product_view_detail)
        email = user_arn_session.split('/')[-1]  # Extract email from the ARN
        if email in user_products:
            user_products[email] += 1
        else:
            user_products[email] = 1

    # Convert the dictionary to a list of dictionaries
    index = 0
    for email, count in user_products.items():
        if count >= threshold:
            users.append({'message': 'number of products launched', 'index': index, 'email': email, 'product_count': count, 'product_info': product_view_detail, 'user_info': user_info})
            index += 1 

    return users

def get_stale_provisioned_products(response, threshold_time):
    """Return provisioned products older than 8 hours."""
    stale_provisioned_products = []
    try:
        for index, product_view_detail in enumerate(response['ProvisionedProducts']):
            provisioned_time_str = product_view_detail['CreatedTime']
            if isinstance(provisioned_time_str, str):  # Check if provisioned_time_str is a string
                provisioned_time = datetime.strptime(
                    provisioned_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            else:
                provisioned_time = provisioned_time_str  # If it's already a datetime object, use it directly
            
            duration = datetime.now(timezone.utc) - provisioned_time
            duration_hours = duration.total_seconds() / 3600
            if provisioned_time < threshold_time:
                duration_str = get_duration_in_days(duration_hours)
                product_view_detail['index'] = index
                product_view_detail['duration'] = duration_str
                product_view_detail['user_info'] = extract_user_info(product_view_detail)
                stale_provisioned_products.append(product_view_detail)
        return stale_provisioned_products
    except Exception as e:
        logging.error(f"Error getting stale provisioned products: {e}")
        return None

    
    
def extract_users_infos(response):
    """Extract first name, last name, and email from the response."""
    user_info = []
    try:
        for product_view_detail in response['ProvisionedProducts']:
            user_arn_session = product_view_detail['UserArnSession']
            email = user_arn_session.split('/')[-1]  # Extract email from the ARN session
            parts = product_view_detail['Name'].split('-')  # Split name to extract first name and last name
            if len(parts) >= 3:
                first_name = parts[0]
                last_name = parts[1]
                user_info.append({'first_name': first_name, 'last_name': last_name, 'email': email})
        return user_info
    except Exception as e:
        logging.error(f"Error extracting user info: {e}")
        return None
    
def extract_user_info(product_view_detail):
    """Extract first name, last name, and email from the response."""
    user_info = {}
    try:
        user_arn_session = product_view_detail['UserArnSession']
        email = user_arn_session.split('/')[-1]  # Extract email from the ARN session
        parts = product_view_detail['Name'].split('-')  # Split name to extract first name and last name
        if len(parts) >= 3:
            first_name = parts[0]
            last_name = parts[1]
            user_info = {'first_name': first_name, 'last_name': last_name, 'email': email}
        return user_info
    except Exception as e:
        logging.error(f"Error extracting user info: {e}")
        return None

    
def write_info_to_json(info, filename):
    """Write user information extracted from the response to a JSON file."""
    try:
        with open(filename, 'w') as json_file:
            json.dump(info, json_file, indent=4)
        logging.info(f"User information written to file: {filename}")
    except Exception as e:
        logging.error(f"Error writing user info to JSON file: {e}")
        
def check_naming_convention(users, provisioned_products):
    """Check naming convention and user existence."""
    non_conforming_products = []
    counter = 0
    try:
        for index, product in enumerate(provisioned_products['ProvisionedProducts']):
            # Extract user email from ARN session
            arn_session = product.get('UserArnSession', '')
            email = arn_session.split('/')[-1]
            
            # Check if the email exists in the list of users
            user_exists = next((user for user in users if user['email'] == email), None)
            # Check naming convention
            product_name = product.get('ProductName', '')

            if user_exists:
                expected_name = f"{user_exists['first_name']}-{user_exists['last_name']}-{product_name}"
                provided_name = product.get('Name', '')
                if provided_name !=  expected_name:
                    non_conforming_products.append({'error':'naming convention violated','index': counter, 'provided_name': provided_name, 'expected_name': expected_name, 'email': user_exists['email'], 'reason': 'Naming convention not followed', 'product_info': product, 'user_info': user_exists})
                    counter += 1
        return non_conforming_products
    except Exception as e:
        logging.error(f"Error checking naming convention: {e}")
        return None
    
def get_unauthorized_users(users, provisioned_products):
    """Check for unauthorized users."""
    non_conforming_products = []
    counter = 0
    try:
        for index, product in enumerate(provisioned_products['ProvisionedProducts']):
            # Extract user email from ARN session
            
            arn_session = product.get('UserArnSession', '')
            email = arn_session.split('/')[-1]
            
            # Check if the email exists in the list of users
            user_exists = next((user for user in users if user['email'] == email), None)
            
            if not user_exists:
                user_info = extract_user_info(product)
                non_conforming_products.append({'error': 'unauthorised product launch','index': counter, 'email': email, 'user_info': user_info, 'reason': 'User does not exist in the list of users', 'product_info': product})
                counter += 1
        return non_conforming_products
    except Exception as e:
        logging.error(f"Error checking unauthorized users: {e}")
        return None

def extract_properties(stale_products, properties):
    extracted_products = []
    for product in stale_products:
        extracted_product = {}
        for prop in properties:
            value = product.get(prop)
            if isinstance(value, datetime):
                # Convert datetime objects to ISO 8601 formatted strings
                value = value.isoformat()
            extracted_product[prop] = value
        extracted_products.append(extracted_product)
    return extracted_products

