# Provisioned Products Monitoring Application

## Features
- **Monitoring Stale Provisioned Products:** The application monitors provisioned products in AWS Service Catalog and identifies those that have been provisioned for more than a specified duration.
- **User Count Tracking:** It tracks the number of provisioned products launched by each user and identifies users with a high number of provisioned products.
- **Slack Notification:** Upon identification of stale provisioned products or users with a high number of provisioned products, the application sends notifications via Slack to notify the user.

## Dependencies
- Python 3
- Flask
- Boto3
- Requests library

## Configuration
- **AWS Credentials:** Ensure that AWS credentials with appropriate permissions are configured on the system where the application will run.
- **Slack Webhook URL:** To enable Slack notification, update the `slack_webhook_url` variable in the `config.py` file with the appropriate webhook URL provided by Slack.
- **Threshold Configuration:** Adjust the threshold time for identifying stale provisioned products and the threshold count for identifying users with a high number of provisioned products in the `config.py` file.

## Usage
1. Clone the repository to your local or remote machine.
2. Set up AWS credentials with appropriate permissions.
3. Install the required Python packages using `pip install -r requirements.txt`.
4. Run the Flask application by executing `python app.py`.
5. Access the application in your web browser at `http://localhost:5000`.

## Notes
- Ensure that the `provisioned_products.json` file is present in the root directory of the application. This file contains the response data from the AWS Service Catalog API, Currently used for testing purposes. It shall be dropped later
- Customize the `dashboard.html` template in the `templates` folder to modify the appearance of the dashboard as needed.
- The `provisioned_products_monitor.py` file contains functions for querying provisioned products, calculating duration, and processing data. Modify this file to extend or customize the monitoring functionality.
- For production deployment, configure appropriate security settings, such as HTTPS, and consider deploying the application on a secure server environment.
- Monitor logs and error messages for any issues during application execution, and handle exceptions gracefully to ensure smooth operation.
- Use version control (e.g., Git) to track changes and collaborate on the codebase effectively. Push the code to a remote repository, such as GitHub, for backup and version management.
