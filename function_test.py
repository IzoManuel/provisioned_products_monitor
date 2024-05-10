#!/usr/bin/env python3

import logging
from provisioned_products_monitor import *

# Configure logging
logging.basicConfig(filename='function_test.log', level=logging.INFO)

if __name__ == "__main__":
    try:
        # Initialize Service Catalog client
        sc_client = initialize_service_catalog_client()
        
        # Fetch user info from S3
        users = fetch_user_info_from_s3()
        
        # Get threshold time
        threshold_time = get_threshold_time()

        if sc_client and users:
            # Query provisioned products
            provisioned_products = query_provisioned_products(sc_client)
            
            if provisioned_products:
                # Check naming convention
                non_conforming_users = check_naming_convention(users, provisioned_products)
                
                # Get unauthorized users
                non_conforming_users2 = get_unauthorized_users(users, provisioned_products)
                
                # Get stale provisioned products
                stale_products = get_stale_provisioned_products(provisioned_products, threshold_time)
                
                # Track user launches
                user_launched_products = track_user_launches(provisioned_products)
                
                # Extract user info
                user_info = extract_user_info(provisioned_products['ProvisionedProducts'][6])
                
                # Log results
                if non_conforming_users:
                    logging.info("########Users not following naming convention:########")
                    logging.info(non_conforming_users)
                
                if non_conforming_users2:
                    logging.info("########Unauthorized users:########S")
                    logging.info(non_conforming_users2)
                if stale_products:
                    logging.info("########Stale products:########")
                    logging.info(stale_products)
                    
                if user_launched_products:
                    logging.info("########Launched products count:########")
                    logging.info(user_launched_products)
                    
                if user_info:
                    logging.info("########User info:########")
                    logging.info(user_info)
                    
            else:
                logging.error("No provisioned products found.")
        else:
            logging.error("Failed to initialize ServiceCatalog client or fetch user info from S3.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
