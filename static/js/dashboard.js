// Function to show details for selected row
stale_emails = extractEmails(stale_products);
launches_emails = extractEmails(users);
disc_emails = extractEmails(name_disc_products);
unauthorized_emails = extractEmails(unauthorized_users);
// Variable to store the check value
let currentCheck = null;

let isConfirming = false;

function showProductDetailsForRow(index) {
  currentCheck = "stale";
  // Get the selected product using its index
  let selectedProduct = stale_products[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedProductItemDetails");

  detailsDiv.innerHTML = `<div>
                             <p><strong class="text-gray-600">Product Name:</strong> ${selectedProduct.Name}</p>
                             <p><strong class="text-gray-600">Duration:</strong> ${selectedProduct.duration}</p>
                             <p><strong class="text-gray-600">Status:</strong> ${selectedProduct.Status}</p>
                             </div>`;
  // Define selectedItemDetailsRow
  let selectedProductItemDetailsRow = document.getElementById(
    "selectedProductItemDetailsRow"
  );

  // Convert JSON data to a formatted JSON string
  const formattedJson = JSON.stringify(selectedProduct, null, 2);

  // Display the formatted JSON string on the webpage
  document.getElementById("selectedStaleProdItemFormattedJSON").textContent =
    formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedProductItemDetailsRow) {
    selectedProductItemDetailsRow.style.display = "block";
    showToast("Scroll downwards to view additional details.");

    appendEmailButton(detailsDiv, selectedProduct.user_info.email);
  } else {
    console.error("selectedItemDetailsRow is undefined");
  }
}

// Function to create and append an email button
function appendEmailButton(detailsDiv, userEmail) {
  // Create the email button
  let emailButton = document.createElement("button");
  emailButton.textContent = "Send email alert";
  emailButton.className = "btn bg-warning font-semibold h-10";

  // Add event listener to the button
  emailButton.addEventListener("click", function () {
    // Disable the button and show a spinner
    emailButton.disabled = true;
    emailButton.innerHTML = `
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    `;

    // Call sendEmail function
    sendEmail(userEmail, emailButton);
  });

  // Append the button to the details div
  detailsDiv.appendChild(emailButton);
}

// Function to show details for selected row
function showUserDetailsForRow(index) {
  currentCheck = "launches";
  // Get the selected product using its index
  let user = users[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedUserItemDetails");
  detailsDiv.innerHTML = `<div>
                            <p><strong class="text-gray-600">User email:</strong> ${user.email}</p>
                            <p><strong class="text-gray-600">Number of provisioned products:</strong> ${user.product_count}</p>
                          <div>`;
  // Define selectedItemDetailsRow
  let selectedUserItemDetailsRow = document.getElementById(
    "selectedUserItemDetailsRow"
  );

  // Convert JSON data to a formatted JSON string
  const formattedJson = JSON.stringify(user, null, 2);

  // Display the formatted JSON string on the webpage
  document.getElementById("selectedUserLaunchItemFormattedJSON").textContent =
    formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedUserItemDetailsRow) {
    selectedUserItemDetailsRow.style.display = "block";
    showToast("Scroll downwards to view additional details.");

    appendEmailButton(detailsDiv, user.email);
  } else {
    console.error("selectedItemDetailsRow is undefined");
  }
}

// Function to show details for selected row
function showNameDiscDetailsForRow(index) {
  currentCheck = "name-disc";
  // Get the selected product using its index
  let name_disc_product = name_disc_products[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedNameDiscItemDetails");
  detailsDiv.innerHTML = `<div>
                            <p><strong class="text-gray-600">Provided name:</strong> ${name_disc_product.provided_name}</p>
                            <p><strong class="text-gray-600">Expected name:</strong> ${name_disc_product.expected_name}</p>
                            <p><strong class="text-gray-600">User email:</strong> ${name_disc_product.email}</p>
                          </div>`;
  // Define selectedItemDetailsRow
  let selectedNameDiscItemDetailsRow = document.getElementById(
    "selectedNameDiscItemDetailsRow"
  );
  // Convert JSON data to a formatted JSON string
  const formattedJson = JSON.stringify(name_disc_product, null, 2);

  // Display the formatted JSON string on the webpage
  document.getElementById("selectedNameDiscItemFormattedJSON").textContent =
    formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedNameDiscItemDetailsRow) {
    selectedNameDiscItemDetailsRow.style.display = "block";
    showToast("Scroll downwards to view additional details.");

    appendEmailButton(detailsDiv, name_disc_product.user_info.email);
  } else {
    console.error("selectedNameDiscItemDetailsRow is undefined");
  }
}

// Function to show details for selected row
function showUnauthUserDetailsForRow(index) {
  currentCheck = "unauthorized";
  // Get the selected product using its index
  let unauthorized_user = unauthorized_users[index];
  // Display details in the details section
  let detailsDiv = document.getElementById("selectedUnauthUserItemDetails");
  detailsDiv.innerHTML = `<div>
                            <p><strong class="text-gray-600">Product Name:</strong> ${unauthorized_user.product_info.ProductName}</p>
                            <p><strong class="text-gray-600">User Email:</strong> ${unauthorized_user.email}</p>
                          </div>`;
  // Define selectedItemDetailsRow
  let selectedUnauthUserItemDetailsRow = document.getElementById(
    "selectedUnauthUserItemDetailsRow"
  );
  // Convert JSON data to a formatted JSON string
  const formattedJson = JSON.stringify(unauthorized_user, null, 2);

  // Display the formatted JSON string on the webpage
  document.getElementById("selectedUnauthUserItemFormattedJSON").textContent =
    formattedJson;

  // Check if selectedItemDetailsRow is defined before setting its display property
  if (selectedUnauthUserItemDetailsRow) {
    selectedUnauthUserItemDetailsRow.style.display = "block";
    showToast("Scroll downwards to view additional details.");

    appendEmailButton(detailsDiv, unauthorized_user.email);
  } else {
    console.error("selectedUnauthUserItemDetailsRow is undefined");
  }
}

async function sendEmail(userEmail, button) {
  try {
    const response = await fetch("/send-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: [userEmail], check: currentCheck }),
    });

    if (response.ok) {
      // Handle success
      showToast("Email sent successfully");
    } else {
      // Handle error
      showToast("Failed to send email");
    }
  } catch (error) {
    // Handle network errors
    console.error("Error:", error);
  } finally {
    // Enable the button and remove the spinner
    button.disabled = false;
    button.textContent = "Send email alert";
  }
}

async function sendBulkEmail(emailList, check) {
  // Declare bulkEmailButton variable outside of if-else statements
  let bulkEmailButton;

  if (check == "stale") {
    bulkEmailButton = document.getElementById("staleBulkEmailButton");
  } else if (check == "launches") {
    bulkEmailButton = document.getElementById("launchesBulkEmailButton");
  } else if (check == "name-disc") {
    bulkEmailButton = document.getElementById("nameDiscEmailButton");
  } else if (check == "unauthorized") {
    bulkEmailButton = document.getElementById("unauthBulkEmailButton");
  }

  // Ensure bulkEmailButton is defined before proceeding
  if (bulkEmailButton) {
    // Disable the button and show a spinner
    bulkEmailButton.disabled = true;
    bulkEmailButton.innerHTML = `
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="sr-only">Loading...</span>
      </div>
    `;

    try {
      const response = await fetch("/send-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: emailList, check: check }),
      });

      if (response.ok) {
        // Handle success
        showToast("Bulk email sent successfully");
      } else {
        // Handle error
        showToast("Failed to send bulk email");
      }
    } catch (error) {
      // Handle network errors
      console.error("Error:", error);
    } finally {
      // Enable the button and remove the spinner
      bulkEmailButton.disabled = false;
      bulkEmailButton.textContent = "Send bulk email";
    }
  } else {
    console.error("Bulk email button not found for check:", check);
  }
}

function confirmBulkEmail(emailList, check) {
  // Get the bulk email button based on the check parameter
  let bulkEmailButton;
  if (check == "stale") {
    bulkEmailButton = document.getElementById("staleBulkEmailButton");
  } else if (check == "launches") {
    bulkEmailButton = document.getElementById("launchesBulkEmailButton");
  } else if (check == "name-disc") {
    bulkEmailButton = document.getElementById("nameDiscEmailButton");
  } else if (check == "unauthorized") {
    bulkEmailButton = document.getElementById("unauthBulkEmailButton");
  } else {
    console.error("Invalid check:", check);
    return;
  }

  // Check if already confirming
  if (isConfirming) {
    // Send bulk email
    sendBulkEmail(emailList, check);
    return;
  }

  // Change button text to confirm
  bulkEmailButton.style.color = "red"
  bulkEmailButton.textContent = "Confirm";
  // Set flag to indicate confirming
  isConfirming = true;

  // After 3 seconds, reset button text and flag
  setTimeout(() => {
    bulkEmailButton.textContent = "Send bulk email";
    bulkEmailButton.style.color = ""
    isConfirming = false;
  }, 3000);
}

// Function to show toast notification
function showToast(message) {
  // Get the toast element
  let toastElement = document.getElementById("liveToast");
  // Update the toast message
  let toastBody = toastElement.querySelector(".toast-body");
  toastBody.textContent = message;
  // Show the toast
  let toast = new bootstrap.Toast(toastElement);
  toast.show();
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

function extractEmails(response) {
  let emails = [];

  response.forEach((item) => {
    // Check if the item has a 'user_info' property and it contains an 'email' value
    if (item.user_info && item.user_info.email) {
      // Push the email to the 'emails' array
      emails.push(item.user_info.email);
    }
  });
  // Return the array of emails
  return emails;
}

function resetIsConfirming() {
  isConfirming = false;
}
