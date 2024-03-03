#!/usr/bin/python3
import os
import boto3
import requests
import logging
from datetime import datetime, timedelta, timezone
import json

def get_users(response, threshold = 1):
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
    return sc_client.search_provisioned_products()


def send_slack_notification(webhook_url, message_content):
    """Send a notification via Slack."""
    message_payload = {"text": f"```\n{json.dumps(message_content, indent=4)}\n```"}
    response = requests.post(webhook_url, json=message_payload)
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
