// Function to show details for selected row
function showProductDetailsForRow(index) {
  // Get the selected product using its index
  let selectedProduct = stale_products[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedProductItemDetails");

  detailsDiv.innerHTML = `<p><strong class="text-gray-600">Product Name:</strong> ${selectedProduct.Name}</p>
                             <p><strong class="text-gray-600">Duration:</strong> ${selectedProduct.duration}</p>
                             <p><strong class="text-gray-600">Status:</strong> ${selectedProduct.Status}</p>`;
  // Define selectedItemDetailsRow
  let selectedProductItemDetailsRow = document.getElementById(
    "selectedProductItemDetailsRow"
  );

  // Convert JSON data to a formatted JSON string
  const formattedJson = JSON.stringify(selectedProduct, null, 2);

  // Display the formatted JSON string on the webpage
  document.getElementById("selectedStaleProdItemFormattedJSON").textContent = formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedProductItemDetailsRow) {
    selectedProductItemDetailsRow.style.display = "block";
  } else {
    console.error("selectedItemDetailsRow is undefined");
  }
}

// Function to show details for selected row
function showUserDetailsForRow(index) {
  // Get the selected product using its index
  let user = users[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedUserItemDetails");
  detailsDiv.innerHTML = `<p><strong class="text-gray-600">User email:</strong> ${user.email}</p>
                             <p><strong class="text-gray-600">Number of provisioned products:</strong> ${user.product_count}</p>`;
  // Define selectedItemDetailsRow
  let selectedUserItemDetailsRow = document.getElementById(
    "selectedUserItemDetailsRow"
  );

    // Convert JSON data to a formatted JSON string
    const formattedJson = JSON.stringify(user, null, 2);

    // Display the formatted JSON string on the webpage
    document.getElementById("selectedUserLaunchItemFormattedJSON").textContent = formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedUserItemDetailsRow) {
    selectedUserItemDetailsRow.style.display = "block";
  } else {
    console.error("selectedItemDetailsRow is undefined");
  }
}

// Function to show details for selected row
function showNameDiscDetailsForRow(index) {
  // Get the selected product using its index
  let name_disc_product = name_disc_products[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedNameDiscItemDetails");
  detailsDiv.innerHTML = `<p><strong class="text-gray-600">Provided name:</strong> ${name_disc_product.provided_name}</p>
                             <p><strong class="text-gray-600">Expected name:</strong> ${name_disc_product.expected_name}</p>
                             <p><strong class="text-gray-600">User email:</strong> ${name_disc_product.email}</p>`;
  // Define selectedItemDetailsRow
  let selectedNameDiscItemDetailsRow = document.getElementById(
    "selectedNameDiscItemDetailsRow"
  );
  // Convert JSON data to a formatted JSON string
  const formattedJson = JSON.stringify(name_disc_product, null, 2);

  // Display the formatted JSON string on the webpage
  document.getElementById("selectedNameDiscItemFormattedJSON").textContent = formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedNameDiscItemDetailsRow) {
    selectedNameDiscItemDetailsRow.style.display = "block";
  } else {
    console.error("selectedNameDiscItemDetailsRow is undefined");
  }
}

// Function to show details for selected row
function showUnauthUserDetailsForRow(index) {
  // Get the selected product using its index
  let unauthorized_user = unauthorized_users[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedUnauthUserItemDetails");
  detailsDiv.innerHTML = `<p><strong class="text-gray-600">Product Name:</strong> ${unauthorized_user.product_info.ProductName}</p>
                             <p><strong class="text-gray-600">User Email:</strong> ${unauthorized_user.email}</p>`;
  // Define selectedItemDetailsRow
  let selectedUnauthUserItemDetailsRow = document.getElementById(
    "selectedUnauthUserItemDetailsRow"
  );
    // Convert JSON data to a formatted JSON string
    const formattedJson = JSON.stringify(unauthorized_user, null, 2);

    // Display the formatted JSON string on the webpage
    document.getElementById("selectedUnauthUserItemFormattedJSON").textContent = formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedUnauthUserItemDetailsRow) {
    selectedUnauthUserItemDetailsRow.style.display = "block";
  } else {
    console.error("selectedUnauthUserItemDetailsRow is undefined");
  }
}

// Listen for radio button changes
document.querySelectorAll(".radio").forEach((radio) => {
  radio.addEventListener("change", function () {
    let selectedIndex = parseInt(this.id.replace("radio", ""));
    let type = this.getAttribute("data-type");
    if (type === "stale-product") {
      showProductDetailsForRow(selectedIndex);
    } else if (type === "user-launch-count") {
      showUserDetailsForRow(selectedIndex);
    } else if (type == "name-disc-product") {
      showNameDiscDetailsForRow(selectedIndex);
    } else if (type == "unauth-user") {
      showUnauthUserDetailsForRow;
    } else {
      console.error("Invalid data-type attribute");
    }
  });
});
