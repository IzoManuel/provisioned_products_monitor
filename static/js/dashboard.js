// Function to show details for selected row
function showDetailsForRow(index) {
    // Get the selected product using its index
    console.log('Openning')
    let selectedProduct = provisioned_products[index];
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
        showDetailsForRow(selectedIndex);
    });
});
