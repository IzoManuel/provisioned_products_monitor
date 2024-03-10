#!/home/ubuntu/environment/dg-capstone-1-team-israel/venv/bin/python
import os
import boto3
import requests
import logging
from datetime import datetime, timedelta, timezone
import json

logging.basicConfig(level=logging.INFO)

def track_user_launches(response, threshold = 1):
    """Count the number of provisioned products for each user."""
    users = []

    # Create a dictionary to store the count for each user
    user_products = {}

    # Loop through the provisioned products and count the number for each user
    for product_view_detail in response:
        user_arn_session = product_view_detail['UserArnSession']
        email = user_arn_session.split('/')[-1]  # Extract email from the ARN
        if email in user_products:
            user_products[email] += 1
        else:
            user_products[email] = 1

    # Convert the dictionary to a list of dictionaries
    index = 0
    for email, count in user_products.items():
        if count >= threshold:
            users.append({'index': index, 'email': email, 'product_count': count})
            index += 1 

    return users
    
def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog', region_name='ap-south-1')

def get_threshold_time(hours=8):
    """Return the time threshold."""
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def query_provisioned_products(sc_client):
    """Query provisioned products."""
    response = sc_client.search_provisioned_products()
    # Convert datetime objects to string representations
    for product in response['ProvisionedProducts']:
        product['CreatedTime'] = product['CreatedTime'].strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    return response



def send_slack_notification(webhook_url, message_content):
    """Send a notification via Slack."""
    message_payload = {"text": f"```\n{json.dumps(message_content, indent=4)}\n```"}
    response = requests.post(webhook_url, json=message_payload)
    
    # logging.info(f"Slack API request: {message_payload}")
    
    if response.status_code == 200:
        logging.info('Slack message sent successfully')
    else:
        logging.error(f'Failed to send Slack message, status code: {response.status_code}')


def get_duration_in_days(duration_hours):
    """Return the duration in days."""
    if duration_hours >= 24:
        duration_days = duration_hours / 24
        # Display duration in days
        return f"{int(duration_days)} day{'s' if duration_days > 1 else ''}"
    else:
        return f"{duration_hours:.2f} hours"  # Display duration in hours


def get_stale_provisioned_products(response, threshold_time):
    """Return provisioned products older than 8 hours."""
    stale_provisioned_products = []
    for index, product_view_detail in enumerate(response['ProvisionedProducts']):
        provisioned_time = datetime.strptime(
            product_view_detail['CreatedTime'], "%Y-%m-%dT%H:%M:%S.%f%z")
        duration = datetime.now(timezone.utc) - provisioned_time
        duration_hours = duration.total_seconds() / 3600
        if provisioned_time < threshold_time:
            duration_str = get_duration_in_days(duration_hours)
            product_view_detail['index'] = index
            product_view_detail['duration'] = duration_str
            stale_provisioned_products.append(product_view_detail)

    return stale_provisioned_products
    
def extract_user_info(response):
    """Extract first name, last name, and email from the response."""
    user_info = []
    for product_view_detail in response['ProvisionedProducts']:
        user_arn_session = product_view_detail['UserArnSession']
        email = user_arn_session.split('/')[-1]  # Extract email from the ARN session
        parts = product_view_detail['Name'].split('-')  # Split name to extract first name and last name
        if len(parts) >= 3:
            first_name = parts[0]
            last_name = parts[1]
            user_info.append({'first_name': first_name, 'last_name': last_name, 'email': email})
    return user_info
    
def write_info_to_json(info, filename):
    """Write user information extracted from the response to a JSON file."""
    with open(filename, 'w') as json_file:
        json.dump(info, json_file, indent=4)



sc_client = initialize_service_catalog_client()

provisioned_products = query_provisioned_products(sc_client)

user_info = extract_user_info(provisioned_products)

write_info_to_json(user_info, "user_info.json")