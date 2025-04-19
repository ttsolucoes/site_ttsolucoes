document.addEventListener('DOMContentLoaded', () => {

    // Troca de abas
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(tab => tab.classList.remove('active'));
    
            this.classList.add('active');
            const target = this.getAttribute('data-tab');
            document.getElementById(target).classList.add('active');
        });
    });

    // Ações de botões
    document.body.addEventListener('click', async (e) => {
        if (e.target.classList.contains('btn-save')) {
            await salvarUsuario(e.target);
        }
        if (e.target.classList.contains('btn-logs')) {  // CORREÇÃO AQUI (de 'btn-log' para 'btn-logs')
            console.log('Botão de logs clicado');
            await visualizarLog(e.target);
        }
        if (e.target.classList.contains('btn-delete')) {
            await deletarUsuario(e.target);
        }
    
        if (e.target.classList.contains('btn-detail')) {
            abrirDetalhe(e.target);
        }
        if (e.target.classList.contains('btn-approve')) {
            await aprovarSolicitacao(e.target);
        }
        if (e.target.classList.contains('btn-reject')) {
            await rejeitarSolicitacao(e.target);
        }
        if (e.target.classList.contains('close')) {
            fecharModal();
        }
    });

    // Salvar dados de usuário interno
    async function salvarUsuario(button) {
        const row = button.closest('tr');
        const username = button.dataset.username;
        const tipo = button.dataset.tipo;
        const email = row.querySelector('.email-input')?.value;
        const cargo = row.querySelector('.cargo-select')?.value;
        const senha = row.querySelector('.senha-input')?.value;

        let data = { tipo, cargo, email };

        if (senha && senha !== '******') {
            data.senha_nova = senha;
        }

        const response = await fetch(`/usuarios/${username}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const resData = await response.json();

        alert(resData.message);
    }

    // Ver log do usuário
    async function visualizarLog(button) {
        const username = button.dataset.username;
        console.log(`Buscando logs para: ${username}`);
        
        try {
            const response = await fetch(`/logs_usuario/${username}`);
            const result = await response.json();
    
            if (result.success) {
                const modal = document.getElementById('detalheModal');
                modal.innerHTML = `
                    <div class="modal-content">
                        <span class="close">&times;</span>
                        <h2>Logs de ${username}</h2>
                        <div class="logs-container">
                            ${result.logs.map(log => `<p>${log}</p>`).join('')}
                        </div>
                    </div>
                `;
                modal.style.display = 'block';
    
                // Adiciona listener para o botão close
                modal.querySelector('.close').addEventListener('click', () => {
                    modal.style.display = 'none';
                });
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Erro ao buscar logs:', error);
            alert('Erro ao carregar logs');
        }
    }

    // Remover usuário ou solicitação
    async function deletarUsuario(button) {
        const username = button.dataset.username;
        const tipo = button.dataset.tipo;

        if (!confirm(`Tem certeza que deseja remover ${username}?`)) return;

        const response = await fetch(`/usuarios/${username}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo })
        });
        const result = await response.json();

        if (result.success) {
            button.closest('tr').remove();
        }
        alert(result.message);
    }

    // Função para abrir o modal com os detalhes da solicitação
    function abrirDetalhe(button) {
        const dados = JSON.parse(button.dataset.info);  // Lê as informações JSON associadas ao botão
        const modal = document.getElementById('detalheModal');

        // Preenche os dados no modal
        modal.querySelector('.modal-content .detalhe-username').textContent = dados.username;
        modal.querySelector('.modal-content .detalhe-email').textContent = dados.email;
        modal.querySelector('.modal-content .detalhe-origem').textContent = dados.origem;

        // Armazena dados no modal
        modal.dataset.username = dados.username;
        modal.dataset.origem = dados.origem;
        modal.dataset.id = dados.id;

        // Exibe o modal
        modal.style.display = 'block';
    }

    // Função para fechar o modal
    function fecharModal() {
        document.getElementById('detalheModal').style.display = 'none';
    }

    // Adicionando o evento de fechar ao clicar no "X"
    document.querySelector('.close').addEventListener('click', fecharModal);

    // Adicionando o evento de fechar ao clicar fora do modal
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('detalheModal');
        if (event.target === modal) {
            fecharModal();
        }
    });

    // Aprovar Solicitação
    async function aprovarSolicitacao(button) {
        const modal = document.getElementById('detalheModal');
        const username = modal.dataset.username;
        const origem = modal.dataset.origem;
        const idSolicitacao = modal.dataset.id;

        // Mensagem para o suporte aprovar ou reprovar
        let mensagem = `Solicitação de ${username}:\nOrigem: ${origem}\nDeseja aprovar esta solicitação?`;

        if (confirm(mensagem)) {
            if (origem === 'recuperar_acesso') {
                const novaSenha = prompt("Informe a nova senha:");
                if (!novaSenha) return alert("Senha não informada.");

                const response = await fetch(`/recuperar_acesso/${username}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tipo: 'aprovar_senha',
                        id_solicitacao: idSolicitacao,
                        nova_senha: novaSenha
                    })
                });

                const result = await response.json();
                alert(result.message);
            } else if (origem === 'novo_usuario') {
                // Aprovar novo usuário
                const response = await fetch(`/usuarios/${username}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tipo: 'interno', cargo: 'user' })
                });

                const result = await response.json();
                alert(result.message);
            } else if (origem === 'alterar_usuario') {
                // Aprovar alteração de status
                const response = await fetch(`/solicitacoes/${idSolicitacao}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: 'finalizado' })
                });

                const result = await response.json();
                alert(result.message);
            }
        }

        fecharModal();
    }

    // Rejeitar Solicitação
    async function rejeitarSolicitacao(button) {
        const modal = document.getElementById('detalheModal');
        const username = modal.dataset.username;

        if (!confirm(`Deseja realmente rejeitar ${username}?`)) return;

        const response = await fetch(`/usuarios/${username}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo: 'publicos' })
        });

        const result = await response.json();
        alert(result.message);
        fecharModal();
    }

});

document.body.addEventListener('click', async (e) => {
    if (e.target.classList.contains('btn-resolver')) {
        const row = e.target.closest('tr');
        const username = row.dataset.username;
        const origem = row.querySelector('td:nth-child(3)').textContent.trim().toLowerCase();
        const id = e.target.dataset.id;

        if (origem === 'novos_usuarios') {
            if (confirm(`Deseja aprovar o usuário ${username}?`)) {
                const response = await fetch(`/solicitacao/novo_usuario/${id}`, { method: 'PUT' });
                const result = await response.json();
                alert(result.message);
                if (result.success) row.remove();
            }
        } else if (origem === 'recuperar_acesso') {
            const novaSenha = prompt("Digite a nova senha para o usuário:");
            if (novaSenha) {
                const response = await fetch(`/recuperar_acesso/${username}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tipo: 'aprovar_senha',
                        id_solicitacao: id,
                        nova_senha: novaSenha
                    })
                });
                const result = await response.json();
                alert(result.message);
                if (result.success) row.remove();
            }
        }
    }
});

window.addEventListener('click', (event) => {
    const modal = document.getElementById('detalheModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
