document.addEventListener('DOMContentLoaded', function() {
    const timestampEl = document.querySelector('.error-timestamp');
    if (timestampEl) {
        timestampEl.textContent = new Date().toLocaleString();
    };
});