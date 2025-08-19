function calcTotal() {
    const price = parseInt(document.getElementById('가격').value.replace(/,/g, '')) || 0;
    const qty = parseInt(document.getElementById('수량').value.replace(/,/g, '')) || 0;
    const discount = parseInt(document.getElementById('할인금액').value.replace(/,/g, '')) || 0;
    const total = Math.max(0, (price - discount) * qty);
    document.getElementById('구매금액').value = total;
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('가격').addEventListener('input', calcTotal);
    document.getElementById('수량').addEventListener('input', calcTotal);
    document.getElementById('할인금액').addEventListener('input', calcTotal);
});
