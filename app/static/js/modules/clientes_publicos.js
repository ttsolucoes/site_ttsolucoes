document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('feedback-form');
    const msgBox = document.getElementById('mensagem-feedback');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {
            nome: formData.get('nome'),
            email: formData.get('email'),
            nota_satisfacao: parseInt(formData.get('nota_satisfacao')),
            comentario: formData.get('comentario')
        };

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                msgBox.textContent = 'Feedback enviado com sucesso!';
                form.reset();
            } else {
                msgBox.textContent = 'Erro ao enviar: ' + result.message;
            }
        } catch (error) {
            msgBox.textContent = 'Erro inesperado. Tente novamente.';
        }
    });
});
