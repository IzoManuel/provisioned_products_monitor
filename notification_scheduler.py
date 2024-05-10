#!/usr/bin/env python3

import logging
from provisioned_products_monitor import *
from dotenv import load_dotenv
import os

load_dotenv()

def send_stale_products_notification(response, threshold_time, webhook_url):
    stale_products = get_stale_provisioned_products(response, threshold_time)
    properties_to_extract = ["Name", "ProductName", "duration", "CreatedTime", "user_info"]
    extracted_data = extract_properties(stale_products, properties_to_extract)
    send_slack_notification(webhook_url, extracted_data)


def user_launches_notification(response, webhook_url):
    user_launches = track_user_launches(response)
    properties_to_extract = ["message", "product_count", "user_info"]
    extracted_data = extract_properties(user_launches, properties_to_extract)
    send_slack_notification(webhook_url, extracted_data)


def naming_convention_notification(users_from_s3, response, webhook_url):
    name_disc_products = check_naming_convention(users_from_s3, response)
    properties_to_extract = ["error", "provided_name", "expected_name", "user_info", "reason"]
    extracted_data = extract_properties(name_disc_products, properties_to_extract)
    send_slack_notification(webhook_url, extracted_data)


def unauthorized_users_notification(users_from_s3, response, webhook_url):
    unauthorized_users = get_unauthorized_users(users_from_s3, response)
    properties_to_extract = ["error", "email", "reason", "user_info"]
    extracted_data = extract_properties(unauthorized_users, properties_to_extract)
    send_slack_notification(webhook_url, extracted_data)


def main():
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    sc_client = initialize_service_catalog_client()

    threshold_time = get_threshold_time()

    users_from_s3 = fetch_user_info_from_s3()

    response = query_provisioned_products(sc_client)

    send_stale_products_notification(response, threshold_time, webhook_url)

    user_launches_notification(response, webhook_url)

    naming_convention_notification(users_from_s3, response, webhook_url)

    unauthorized_users_notification(users_from_s3, response, webhook_url)


if __name__ == "__main__":
    main()
