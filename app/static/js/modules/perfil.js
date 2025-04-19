document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.log-details small').forEach(el => {
        const date = new Date(el.textContent);
        el.textContent = date.toLocaleString();
    });
});