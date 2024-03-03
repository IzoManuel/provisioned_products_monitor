#!/usr/bin/python3
from flask import Flask, render_template
from jinja2 import Environment, FileSystemLoader
from config import *
from provisioned_products_monitor import *

app = Flask(__name__)


@app.route('/')
def stale_provisioned_products():

    with open(os.path.join(get_base_dir(), 'provisioned_products.json'), 'r') as file:
        response = json.load(file)

    threshold_time = get_threshold_time()

    provisioned_products = get_stale_provisioned_products(
        response, threshold_time)

    

    return render_template('dashboard.html', provisioned_products=provisioned_products)


def initialize_service_catalog_client():
    """Initialize AWS ServiceCatalog client."""
    return boto3.client('servicecatalog')

@app.route('/users')
def users():
    with open(os.path.join(get_base_dir(), 'provisioned_products.json'), 'r') as file:
        response = json.load(file)

    users = get_users(response['ProvisionedProducts'])

    return render_template('users.html', users = users)




if __name__ == "__main__":
    # main()
    app.run(debug=True)
