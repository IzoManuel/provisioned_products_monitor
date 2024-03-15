// Function to show details for selected row
function showProductDetailsForRow(index) {
    // Get the selected product using its index
    console.log('Openning')
    let selectedProduct = stale_products[index];
    console.log(selectedProduct)
    // Display details in the details section
    let detailsDiv = document.getElementById('selectedItemDetails');
    console.log(detailsDiv)
    detailsDiv.innerHTML = `<p><strong class="text-gray-600">Product Name:</strong> ${selectedProduct.Name}</p>
                             <p><strong class="text-gray-600 text-red-500">Duration:</strong> ${selectedProduct.duration}</p>
                             <p><strong class="text-gray-600">Status:</strong> ${selectedProduct.Status}</p>`;
    selectedItemDetailsRow.style.display = 'block';
}

// Listen for radio button changes
document.querySelectorAll('.radio').forEach(radio => {
    radio.addEventListener('change', function() {
        let selectedIndex = parseInt(this.id.replace('radio', ''));
        showProductDetailsForRow(selectedIndex);
    });
});

// Function to show details for selected row
function showUserDetailsForRow(index) {
    // Get the selected product using its index
    console.log('Openning'+index)
    let user = users[index];
    console.log(user)
    // Display details in the details section
    let detailsDiv = document.getElementById('selectedItemDetails');
    detailsDiv.innerHTML = `<p><strong class="text-gray-600">User email:</strong> ${user.email}</p>
                             <p><strong class="text-gray-600">Number of provisioned products:</strong> ${user.product_count}</p>`;
    selectedItemDetailsRow.style.display = 'block';
}

// Listen for radio button changes
document.querySelectorAll('.radio').forEach(radio => {
    radio.addEventListener('change', function() {
        let selectedIndex = parseInt(this.id.replace('radio', ''));
        showUserDetailsForRow(selectedIndex);
    });
});
