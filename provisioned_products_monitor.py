#!/usr/bin/env python3

import os
import boto3
import requests
import logging
from datetime import datetime, timedelta, timezone
import json
from dotenv import load_dotenv
import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders

logging.basicConfig(level=logging.INFO)
# Load environment variables from .env file
load_dotenv()

def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog', region_name='ap-south-1')

def get_threshold_time(hours=config.stale_product_threshold_hours):
    """Return the time threshold."""
    return datetime.now(timezone.utc) - timedelta(hours=hours)

def query_provisioned_products(sc_client):
    """Query provisioned products."""
    try:
        environment = os.environ.get('ENV')
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
        environment = os.environ.get('ENV')
        if environment == 'local':
            # Load user information from a local JSON file
            with open('user_info.json', 'r') as file:
                user_info = json.load(file)
        else:
            # Fetch user information from S3
            s3_client = boto3.client('s3')
            bucket_name = config.bucket_name
            file_key = config.file_key
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

def send_email_notification(from_email, to_email, subject, body, csv_data=None, cc=None):
    try:
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = os.environ.get("SMTP_PORT")
        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")

        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(to_email)
        msg['Subject'] = subject

        # Add CC recipients if provided
        if cc:
            msg['Cc'] = ', '.join(cc)
            to_email += cc

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Attach CSV file
        if csv_data:
            # Convert CSV data to string
            csv_content = '\n'.join([','.join(row) for row in csv_data])

            attachment = MIMEBase('text', 'csv')
            attachment.set_payload(csv_content.encode('utf-8'))
            attachment.add_header('Content-Disposition',
                                  f'attachment; filename="{subject}.csv"')
            encoders.encode_base64(attachment)
            msg.attach(attachment)

        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.sendmail(from_email, to_email, msg.as_string())

        logging.info('Email sent successfully!')
    except Exception as e:
        logging.error(f'Error sending email: {e}')
        raise e

def send_custom_email(email, check):
    try:
        # Specify email details based on the type of email
        from_email = 'israel7manuel@gmail.com'
        to_email = email
        subject = 'Your Provisioned Product Alert'
        if check == "stale":
            subject = 'Stale Provisioned Products Alert'
            body = 'This is to notify you that you currently have stale products. Please login into you deploy guru aws account and terminate.'
        elif check == "unauthorized":
            subject = 'Unauthorized Provisioned Product Alert'
            body = 'This is to notify you that you currently unauthorised to launch a product. Please login into you deploy guru aws account and terminate.'
        elif check == "launches":
            subject = 'Threeshold Exceeded Alert'
            body = 'This is to notify you that you have currently exceeded the threshold for launched products per person. Please login into you deploy guru aws account and terminate.'
        elif check == "name-disc":
            subject = 'Naming Discrepancy Provisioned Product Alert'
            body = 'This is to notify you that you have broken the naming convention when provisioning you product. Please login into you deploy guru aws account and terminate.'
        else:
            # Single email
            body = 'This is to notify you about your provisioned product.'

        send_email_notification(from_email, to_email, subject, body)
    except Exception as e:
        raise e
    
def get_duration_in_days(duration_hours):
    """Return the duration in days."""
    if duration_hours >= 24:
        duration_days = duration_hours / 24
        # Display duration in days
        return f"{int(duration_days)} day{'s' if duration_days > 1 else ''}"
    else:
        return f"{duration_hours:.2f} hours"  # Display duration in hours
        
def track_user_launches2(response, threshold=config.high_product_count_threshold):
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
            naming_discrepancy = has_naming_discrepancies(product, users, counter)
            if naming_discrepancy:

                non_conforming_products.append(naming_discrepancy)
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
            unauthorized_product = has_unauthorized_launches(product, users, counter)
            if unauthorized_product:
                non_conforming_products.append(unauthorized_product)
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

def generate_product_summary(response, users):
    product_summary = {}
    threshold_time = get_threshold_time()

    for product_view_detail in response['ProvisionedProducts']:
        product_name = product_view_detail.get('ProductName', '')

        if product_name not in product_summary:
            product_summary[product_name] = {
                'total_products': 0,
                'stale_products': 0,
                'naming_discrepancies': 0,
                'unauthorized_launches': 0
            }
        
        product_summary[product_name]['total_products'] += 1

        # Check if the product is stale
        if is_stale_product(product_view_detail, threshold_time):
            product_summary[product_name]['stale_products'] += 1

        # Check if the product has naming discrepancies
        if has_naming_discrepancies(product_view_detail, users):
            product_summary[product_name]['naming_discrepancies'] += 1

        # Check if the product has unauthorized launches
        if has_unauthorized_launches(product_view_detail, users):
            product_summary[product_name]['unauthorized_launches'] += 1

    return product_summary

def is_stale_product(product_view_detail, threshold_time):
    """Check if a product is stale based on the threshold time."""
    try:
        provisioned_time_str = product_view_detail['CreatedTime']
        if isinstance(provisioned_time_str, str):  # Check if provisioned_time_str is a string
            provisioned_time = datetime.strptime(
                provisioned_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            provisioned_time = provisioned_time_str  # If it's already a datetime object, use it directly

        return provisioned_time < threshold_time
    except Exception as e:
        logging.error(f"Error checking stale product: {e}")
        return False

def has_user_launches(product_view_detail, users, threshold=config.high_product_count_threshold):
    """Check if a product has user launches greater than or equal to the threshold."""
    try:
        user_arn_session = product_view_detail['UserArnSession']
        email = user_arn_session.split('/')[-1]  # Extract email from the ARN
        user_count = sum(1 for user in users if user['email'] == email)
        return user_count >= threshold
    except Exception as e:
        logging.error(f"Error checking user launches: {e}")
        return False

def has_naming_discrepancies(product_view_detail, users, counter=None):
    """Check if a product has naming discrepancies."""
    try:
        arn_session = product_view_detail.get('UserArnSession', '')
        email = arn_session.split('/')[-1]

        # Check if the email exists in the list of users
        user_exists = next((user for user in users if user['email'] == email), None)
        # Check naming convention
        product_name = product_view_detail.get('ProductName', '')

        if user_exists:
            expected_name = f"{user_exists['first_name']}-{user_exists['last_name']}-{product_name}"
            provided_name = product_view_detail.get('Name', '')
            if provided_name !=  expected_name:
                return {'error':'naming convention violated','index': counter, 'provided_name': provided_name, 'expected_name': expected_name, 'email': user_exists['email'], 'reason': 'Naming convention not followed', 'product_info': product_view_detail, 'user_info': user_exists}
            else:
                return None
        else:
            return None
    except Exception as e:
        logging.error(f"Error checking naming discrepancies: {e}")
        return None

def has_unauthorized_launches(product, users, counter=None):
    """Check if a product has unauthorized launches."""
    try:
        arn_session = product.get('UserArnSession', '')
        email = arn_session.split('/')[-1]

        # Check if the email exists in the list of users
        user_exists = next((user for user in users if user['email'] == email), None)
        
        if not user_exists:
            user_info = extract_user_info(product)
            if counter is not None:
                return {'error': 'unauthorised product launch','index': counter, 'email': email, 'user_info': user_info, 'reason': 'User does not exist in the list of users', 'product_info': product}
            else:
                return {'error': 'unauthorised product launch', 'email': email, 'user_info': user_info, 'reason': 'User does not exist in the list of users', 'product_info': product}
        else:
            return None
    except Exception as e:
        logging.error(f"Error checking unauthorized users: {e}")
        return None

def track_user_launches(response, threshold=config.high_product_count_threshold):
    """Count the number of provisioned products for each user."""
    users = []

    # Create a dictionary to store the count for each user
    user_products = {}

    # Group products by user email
    for product_view_detail in response['ProvisionedProducts']:
        user_arn_session = product_view_detail['UserArnSession']
        email = user_arn_session.split('/')[-1]  # Extract email from the ARN
        if email in user_products:
            user_products[email].append(product_view_detail)
        else:
            user_products[email] = [product_view_detail]

    # Loop through the user products and count the number for each user
    counter = 0
    for email, products in user_products.items():
        product_count = len(products)
        if product_count >= threshold:
            user_info = extract_user_info(products[0])  # Assuming all products belong to the same user
            users.append({
                'message': 'number of products launched',
                'index': counter,
                'email': email,
                'product_count': product_count,
                'product_info': products,  # All products belonging to the user
                'user_info': user_info
            })
            counter += 1

    return users
