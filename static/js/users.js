// Function to show details for selected row
function showDetailsForRow(index) {
    // Get the selected product using its index
    console.log('Openning'+index)
    let user = users[index];
    console.log(user)
    // Display details in the details section
    let detailsDiv = document.getElementById('selectedItemDetails');
    detailsDiv.innerHTML = `<p><strong class="text-gray-600">Product Name:</strong> ${user.email}</p>
                             <p><strong class="text-gray-600">Duration:</strong> ${user.product_count}</p>`;
    selectedItemDetailsRow.style.display = 'block';
}

// Listen for radio button changes
document.querySelectorAll('.radio').forEach(radio => {
    radio.addEventListener('change', function() {
        let selectedIndex = parseInt(this.id.replace('radio', ''));
        showDetailsForRow(selectedIndex);
    });
});
