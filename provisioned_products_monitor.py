#!/usr/bin/python3
from jinja2 import Environment, FileSystemLoader
import os
import boto3
import requests
from datetime import datetime, timedelta

def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog')

def get_slack_webhook_url():
    """Return the Slack webhook URL."""
    return 'YOUR_SLACK_WEBHOOK_URL'

def get_threshold_time():
    """Return the time threshold (8 hours ago)."""
    return datetime.now() - timedelta(hours=8)

def query_provisioned_products(sc_client):
    """Query provisioned products."""
    return sc_client.search_provisioned_products()

def notify_slack_about_product(product_name, webhook_url):
    """Notify Slack about the provisioned product."""
    message = {
        'text': f"Provisioned product '{product_name}' has been provisioned for more than 8 hours."
    }
    requests.post(webhook_url, json=message)


def main():
    # Initialize AWS ServiceCatalog client
    sc_client = initialize_service_catalog_client()

    # Get Slack webhook URL
    slack_webhook_url = get_slack_webhook_url()

    # Get the time threshold (8 hours ago)
    threshold_time = get_threshold_time()

    # Query provisioned products
    response = query_provisioned_products(sc_client)

    # Check for provisioned products that have been provisioned for more than 8 hours
    provisioned_products = []
    for product_view_detail in response['ProvisionedProducts']:
        provisioned_time = product_view_detail['CreatedTime']
        if provisioned_time < threshold_time:
            notify_slack_about_product(product_view_detail['Name'], slack_webhook_url)
        provisioned_products.append({'name': product_view_detail['Name'], 'status': product_view_detail['Status']})

    provisioned_products = [
    {'name': 'Product 1', 'status': 'Active'},
    {'name': 'Product 2', 'status': 'Inactive'},
    {'name': 'Product 3', 'status': 'Active'}
]

    # Load the Jinja environment
    env = Environment(loader=FileSystemLoader('/var/www/html/templates/'))
    template = env.get_template('template.html')

    # Render the template with the provisioned products data
    html_content = template.render(provisioned_products=provisioned_products)

    # Write HTML content to a file
    output_file_path = '/var/www/html/dashboard.html'
    with open(output_file_path, 'w') as f:
        f.write(html_content)

    print(f'Dashboard generated and saved to: {output_file_path}')

if __name__ == "__main__":
    main()
