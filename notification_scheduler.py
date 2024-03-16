#!/usr/bin/env python3

from provisioned_products_monitor import *
import logging

def send_stale_provisioned_products_notification(webhook_url, response, threshold_time):
    """Send a notification to Slack with stale provisioned products appended."""
    stale_provisioned_products = get_stale_provisioned_products(response, threshold_time)
 
    if stale_provisioned_products:
        message_content = ""
        for product in stale_provisioned_products:
            message_content += f"Product Name: {product['Name']}\n"
            message_content += f"Duration: {product['duration']}\n"
            message_content += f"Status: {product['Status']}\n\n"

        send_slack_notification(webhook_url, message_content)
    else:
        logging.info("No stale provisioned products found.")


def main():
    
    sc_client = initialize_service_catalog_client()
    
    response = query_provisioned_products(sc_client)
    
    threshold_time = get_threshold_time()
    # Send Slack notification
    webhook_url = 'https://hooks.slack.com/services/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'
    send_stale_provisioned_products_notification(webhook_url, response, threshold_time)
    
if __name__ == "__main__":
    main()