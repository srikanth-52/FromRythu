// FromRythu - Cart Interactions
function updateCartQuantity(button, change) {
    const input = button.closest('.input-group').querySelector('.cart-qty-input');
    if (!input) return;

    let currentVal = parseFloat(input.value) || 1;
    let minVal = parseFloat(input.getAttribute('min')) || 1;
    let maxVal = parseFloat(input.getAttribute('max')) || 9999;

    let newVal = currentVal + change;
    if (newVal >= minVal && newVal <= maxVal) {
        input.value = newVal;
        const form = button.closest('form');
        if (form) form.submit();
    }
}

