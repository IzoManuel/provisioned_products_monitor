#!/home/ubuntu/environment/dg-capstone-1-team-israel/venv/bin/python
import os
import boto3
import requests
import logging
from datetime import datetime, timedelta, timezone
import json

logging.basicConfig(level=logging.INFO)

    
def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog', region_name='ap-south-1')

def get_threshold_time(hours=8):
    """Return the time threshold."""
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def query_provisioned_products(sc_client):
    """Query provisioned products."""
    try:
        response = sc_client.search_provisioned_products()
        # Convert datetime objects to string representations
        for product in response['ProvisionedProducts']:
            product['CreatedTime'] = product['CreatedTime'].strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        return response
    except Exception as e:
        logging.error(f"Error querying provisioned products: {e}")
        return None

def fetch_user_info_from_s3():
    """Fetch user information JSON file from S3."""
    try:
        # S3 bucket and file information
        s3_client = boto3.client('s3')
        bucket_name = 'dg-cohort-01'
        file_key = 'team_israel_users_info2.json'
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        user_info_json = json.loads(response['Body'].read().decode('utf-8'))
        return user_info_json
    except Exception as e:
        logging.error(f"Error fetching user info from S3: {e}")
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
        
def track_user_launches(response, threshold=1):
    """Count the number of provisioned products for each user."""
    users = []

    # Create a dictionary to store the count for each user
    user_products = {}

    # Loop through the provisioned products and count the number for each user
    for product_view_detail in response['ProvisionedProducts']:
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
            users.append({'index': index, 'email': email, 'product_count': count, 'product_info': product_view_detail})
            index += 1 

    return users


def get_stale_provisioned_products(response, threshold_time):
    """Return provisioned products older than 8 hours."""
    stale_provisioned_products = []
    try:
        for index, product_view_detail in enumerate(response['ProvisionedProducts']):
            provisioned_time = datetime.strptime(
                product_view_detail['CreatedTime'], "%Y-%m-%dT%H:%M:%S.%f%z")
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
                    non_conforming_products.append({'index': index, 'provided_name': provided_name, 'expected_name': expected_name, 'email': user_exists['email'], 'reason': 'Naming convention not followed', 'product_info': product})
        return non_conforming_products
    except Exception as e:
        logging.error(f"Error checking naming convention: {e}")
        return None
    
def get_unauthorized_users(users, provisioned_products):
    """Check for unauthorized users."""
    non_conforming_products = []
    try:
        for index, product in enumerate(provisioned_products['ProvisionedProducts']):
            # Extract user email from ARN session
            arn_session = product.get('UserArnSession', '')
            email = arn_session.split('/')[-1]
            
            # Check if the email exists in the list of users
            user_exists = next((user for user in users if user['email'] == email), None)
            
            if not user_exists:
                non_conforming_products.append({'index': index, 'email': email, 'reason': 'User does not exist in the list of users', 'product_info': product})
        return non_conforming_products
    except Exception as e:
        logging.error(f"Error checking unauthorized users: {e}")
        return None


if __name__ == "__main__":
    try:
        sc_client = initialize_service_catalog_client()
        users = fetch_user_info_from_s3()
        threshold_time = get_threshold_time()

        if sc_client and users:
            provisioned_products = query_provisioned_products(sc_client)
            
            if provisioned_products:
                non_conforming_users = check_naming_convention(users, provisioned_products)
                non_conforming_users2 = get_unauthorized_users(users, provisioned_products)
                stale_products = get_stale_provisioned_products(provisioned_products, threshold_time)
                user_launched_products = track_user_launches(provisioned_products)
                user_info = extract_user_info(provisioned_products['ProvisionedProducts'][6])
                
                
                # if non_conforming_users:
                    # logging.info("##########Users not following naming convention:######")
                    # logging.info(non_conforming_users)
                
                # if non_conforming_users2:
                    # logging.info("##########Unauthorized users:##########")
                    # logging.info(non_conforming_users2)
                    
                if stale_products:
                    logging.info("##########Stale products:########")
                    logging.info(stale_products)
                    
                # if user_launched_products:
                    # logging.info("############Launched products count:##############")
                    # logging.info(user_launched_products)
                    
                # if user_info:
                    # logging.info('##########USER INFO#######')
                    # logging.info(user_info)
                    
                # Handle sending Slack notification if necessary
                # send_slack_notification(webhook_url, message_content)
            else:
                logging.error("No provisioned products found.")
        else:
            logging.error("Failed to initialize ServiceCatalog client or fetch user info from S3.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
