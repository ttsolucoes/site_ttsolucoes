document.addEventListener('DOMContentLoaded', function() {
    const usernameField = document.querySelector('#username');
    if (usernameField) {
        usernameField.focus();
    }
    
    const form = document.querySelector('.login-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const username = document.querySelector('#username').value.trim();
            const password = document.querySelector('#password').value.trim();
            
            if (!username || !password) {
                e.preventDefault();
                alert('Preencha todos os campos');
            }
        });
    }
});