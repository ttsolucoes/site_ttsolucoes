document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('create-user-form');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            username: form.username.value,
            email: form.email.value,
            senha: form.senha.value,
            cargo: form.cargo.value,
            acesso_api: form.acesso_api.checked
        };
    
        try {
            const response = await fetch('/usuario_novo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                alert('Usuário criado com sucesso!');
                window.location.href = "/usuarios";
            } else {
                throw new Error('Erro ao criar usuário');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao criar usuário');
        }
    });
});