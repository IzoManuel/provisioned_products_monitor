#!/usr/bin/python3
from jinja2 import Environment, FileSystemLoader
import os
import boto3
import requests
import logging
from datetime import datetime, timedelta, timezone
import json
from config import *

def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog')

def get_threshold_time(hours=8):
    """Return the time threshold."""
    return datetime.now(timezone.utc) - timedelta(hours=hours)

def query_provisioned_products(sc_client):
    """Query provisioned products."""
    return sc_client.search_provisioned_products()

def send_slack_notification(webhook_url, message_content):
    """Send a notification via Slack."""
    message_payload = {"text": f"```\n{json.dumps(message_content, indent = 4)}\n```"}
    response = requests.post(webhook_url, json = message_payload)
    if response.status_code == 200:
        logging.info('Slack message sent successfully')
    else:
        logging.error(f'Failed to send Slack message, status code: {response.status_code}')

def get_duration_in_days(duration_hours):
    """Return the duration in days."""
    if duration_hours >= 24:
        duration_days = duration_hours / 24
        return f"{int(duration_days)} day{'s' if duration_days > 1 else ''}"  # Display duration in days
    else:
        return f"{duration_hours:.2f} hours"  # Display duration in hours

def get_stale_provisioned_products(response, threshold_time):
    """Return provisioned products older than 8 hours."""
    stale_provisioned_products = []
    for product_view_detail in response['ProvisionedProducts']:
        provisioned_time = datetime.strptime(product_view_detail['CreatedTime'], "%Y-%m-%dT%H:%M:%S.%f%z")
        duration = datetime.now(timezone.utc) - provisioned_time
        duration_hours = duration.total_seconds() / 3600 
        if provisioned_time < threshold_time:
            duration_str = get_duration_in_days(duration_hours)
            stale_provisioned_products.append({
                'name': product_view_detail['Name'],
                'status': product_view_detail['Status'],
                'duration': duration_str
            })
    return stale_provisioned_products

def generate_dashboard(provisioned_products):
    """Generate and save the dashboard HTML."""
    base_dir = get_base_dir()

    # Load the Jinja environment
    env = Environment(loader=FileSystemLoader(os.path.join(base_dir, 'templates')))
    template = env.get_template('template.html')

    # Render the template with the provisioned products data
    html_content = template.render(provisioned_products=provisioned_products)

    # Write HTML content to a file
    output_file_path = os.path.join(base_dir, 'dashboard.html')
    with open(output_file_path, 'w') as f:
        f.write(html_content)

    print(f'Dashboard generated and saved to: {output_file_path}')


def main():
    # Send Slack notification
    webhook_url = 'https://hooks.slack.com/services/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'
    # Initialize AWS ServiceCatalog client
    # sc_client = initialize_service_catalog_client()

    # Get the time threshold (8 hours ago)
    threshold_time = get_threshold_time(1)

    # Query provisioned products
    # response = query_provisioned_products(sc_client)

    # Read and print JSON file content
    with open(os.path.join(get_base_dir(), 'provisioned_products.json'), 'r') as file:
        response = json.load(file)

    # Check for provisioned products that have been provisioned for more than 8 hours
    provisioned_products = get_stale_provisioned_products(response, threshold_time)

    generate_dashboard(provisioned_products)

if __name__ == "__main__":
    main()
