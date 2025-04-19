document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.register-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const password = form.querySelector('#password').value;
            const confirm = form.querySelector('#confirm').value;
            
            if (password !== confirm) {
                e.preventDefault();
                alert('As senhas não coincidem!');
            }
        });
    }
});