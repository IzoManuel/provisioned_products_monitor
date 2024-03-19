# Provisioned Products Monitoring Application

## Overview
The AWS Provisioned Products Monitoring System is a robust solution designed to enhance visibility and governance over provisioned products within AWS Service Catalog. This system provides real-time monitoring, user count tracking, naming convention enforcement, and unauthorized user detection, all aimed at ensuring efficient resource management and adherence to organizational policies.

## Features
- **Monitoring Stale Provisioned Products:** The application monitors provisioned products in AWS Service Catalog and identifies those that have been provisioned for more than a specified duration.
- **User Count Tracking:** It tracks the number of provisioned products launched by each user and identifies users with a high number of provisioned products.
- **Naming Convention Check:** It checks the names of the provisioned products against the prescribed convention and send alerts when these conventions are broken
- **Unauthorised User Product Launches:** When a user attempts to launch a product, the application verifies their account against a predefined list of authorized users stored in an Amazon S3 bucket.
- **Slack Notification:** Upon identification of stale provisioned products or users with a high number of provisioned products, the application sends notifications via Slack to notify the user.

## Installation
1. Clone the repository to your local or remote machine.
2. Set up AWS credentials with appropriate permissions.
3. Navigate to the project directory.
4. Install the required Python packages using `pip install -r requirements.txt`.
5. Run the Flask application by executing `python3 app.py`.
6. Access the application by visiting the provided IP address in your web browser. You will be directed to the dashboard page where all the features are available.

### Configuration
- **AWS Credentials:** Ensure that AWS credentials with appropriate permissions are configured on the system where the application will run.
- **Slack Webhook URL:** To enable Slack notification, update the `SLACK_WEBHOOK_URL` variable in the `config.py` file with the appropriate webhook URL provided by Slack.
- **Threshold Configuration:** Adjust the threshold time for identifying stale provisioned products and the threshold count for identifying users with a high number of provisioned products in the `config.py` file.
- **Notification Scheduler:** Configure the notification_scheduler.py script to run once a day using a task scheduler (e.g., cron job). This script automates the process of sending notifications at regular intervals to keep users informed about stale provisioned products and other relevant updates.

## Dependencies
- Python 3.x
- Flask
- Boto3
- Requests 

## Notes
- Ensure that the `provisioned_products.json` file is present in the root directory of the application. 
- Customize the `dashboard.html` template in the `templates` folder to modify the appearance of the dashboard as needed.
- The `provisioned_products_monitor.py` file contains functions for querying provisioned products. Modify this file to extend or customize the monitoring functionality.
- For production deployment, configure appropriate security settings, such as HTTPS, and consider deploying the application on a secure server environment.
- Monitor logs and error messages for any issues during application execution