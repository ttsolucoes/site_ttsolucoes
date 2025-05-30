function configurarUIInicial() {
    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    
    if (isMobile) {
        // Em mobile, começa mostrando apenas o chat area
        document.querySelector('.chat-list').classList.remove('show');
        document.querySelector('.chat-area').classList.remove('hide');
        document.getElementById('toggle-chat-list').textContent = 'Mostrar Conversas';
    } else {
        // Em desktop, mostra ambos
        document.querySelector('.chat-list').classList.add('show');
        document.querySelector('.chat-area').classList.remove('hide');
        document.getElementById('toggle-chat-list').textContent = 'Ocultar Conversas';
    }
}

// Chamar no DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
    configurarUIInicial();
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");
    const conversasContainer = document.getElementById("conversas-container");
    const novaConversaBtn = document.getElementById("nova-conversa-btn");
    
    const username = "{{ users.username }}";
    const userId = "{{ users.id }}";
    const empresa = "{{ empresa }}";
    const ehSuporte = "{{ eh_suporte }}" === "True";
    let sessaoAtiva = null;

    // Carrega as conversas do usuário
    async function carregarConversas() {
        try {
            const response = await fetch('/api/sessoes');
            if (!response.ok) throw new Error('Erro ao carregar conversas');
            
            const sessoes = await response.json();
            conversasContainer.innerHTML = '';
            
            if (sessoes.length === 0 && !ehSuporte) {
                // Usuário sem conversas - cria uma nova automaticamente
                await criarConversa();
                return;
            }
            
            sessoes.forEach(sessao => {
                const conversaEl = document.createElement('div');
                conversaEl.className = 'conversa-item';
                if (sessao.id === sessaoAtiva) {
                    conversaEl.classList.add('ativa');
                }
                
                const titulo = ehSuporte && sessao.usuario_nome ? 
                    `${sessao.titulo} (${sessao.usuario_nome})` : 
                    sessao.titulo;
                
                conversaEl.innerHTML = `
                    <div class="conversa-titulo">${titulo}</div>
                    <div class="conversa-data">${formatarData(sessao.atualizado_em)}</div>
                `;
                
                conversaEl.addEventListener('click', () => carregarMensagens(sessao.id));
                conversasContainer.appendChild(conversaEl);
            });
            
            // Se não houver sessão ativa e existirem conversas, carrega a primeira
            if (!sessaoAtiva && sessoes.length > 0) {
                carregarMensagens(sessoes[0].id);
            }
        } catch (error) {
            console.error('Erro ao carregar conversas:', error);
            mostrarNotificacao('Erro ao carregar conversas', 'error');
        }
    }

    // Formata a data para exibição
    function formatarData(dataString) {
        const data = new Date(dataString);
        return data.toLocaleDateString() + ' ' + data.toLocaleTimeString();
    }

    // Carrega as mensagens de uma sessão
    async function carregarMensagens(sessaoId) {
        try {
            const response = await fetch(`/api/sessoes/${sessaoId}/mensagens`);
            if (!response.ok) throw new Error('Erro ao carregar mensagens');
            
            const mensagens = await response.json();
            sessaoAtiva = sessaoId;
            renderMensagens(mensagens);
            carregarConversas(); // Atualiza a lista para marcar a conversa ativa
        } catch (error) {
            console.error('Erro ao carregar mensagens:', error);
            mostrarNotificacao('Erro ao carregar mensagens', 'error');
        }
    }

    // Renderiza as mensagens no chat
    function renderMensagens(mensagens) {
        chatBox.innerHTML = "";
        mensagens.forEach(msg => {
            const msgEl = document.createElement("div");
            msgEl.classList.add("chat-message");
            
            if (msg.autor === username) {
                msgEl.classList.add("me");
            } else if (msg.eh_suporte) {
                msgEl.classList.add("suporte");
            } else {
                msgEl.classList.add("other");
            }
            
            msgEl.innerHTML = `
                <div class="msg-autor">${msg.autor}</div>
                <div class="msg-texto">${msg.mensagem}</div>
                <div class="msg-data">${formatarData(msg.enviada_em)}</div>
            `;
            
            chatBox.appendChild(msgEl);
        });
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Cria uma nova conversa
    async function criarConversa() {
        try {
            const primeiraMsg = prompt("Digite sua mensagem inicial para o suporte:");
            if (!primeiraMsg) return;
            
            const response = await fetch('/api/sessoes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    titulo: '', // Será gerado automaticamente
                    primeira_msg: primeiraMsg 
                })
            });
            
            if (!response.ok) throw new Error('Erro ao criar conversa');
            
            const novaSessao = await response.json();
            carregarConversas();
            carregarMensagens(novaSessao.id);
            mostrarNotificacao('Conversa criada com sucesso', 'success');
        } catch (error) {
            console.error('Erro ao criar conversa:', error);
            mostrarNotificacao('Erro ao criar conversa', 'error');
        }
    }

    // Envia uma mensagem
    async function enviarMensagem(mensagem) {
        if (!sessaoAtiva) {
            await criarConversa();
            return;
        }
        
        try {
            const response = await fetch(`/api/sessoes/${sessaoAtiva}/mensagens`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mensagem })
            });
            
            if (!response.ok) throw new Error('Erro ao enviar mensagem');
            
            const novaMsg = await response.json();
            carregarMensagens(sessaoAtiva);
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            mostrarNotificacao('Erro ao enviar mensagem', 'error');
        }
    }

    // Mostra notificações para o usuário
    function mostrarNotificacao(mensagem, tipo = 'info') {
        const notificacao = document.createElement('div');
        notificacao.className = `notificacao notificacao-${tipo}`;
        notificacao.textContent = mensagem;
        
        document.body.appendChild(notificacao);
        setTimeout(() => {
            notificacao.remove();
        }, 3000);
    }

    // Event Listeners
    form.addEventListener("submit", async e => {
        e.preventDefault();
        const novaMsg = input.value.trim();
        if (!novaMsg) return;

        await enviarMensagem(novaMsg);
        input.value = "";
    });

    novaConversaBtn.addEventListener('click', criarConversa);

    // Inicialização
    carregarConversas();
    
    // Atualiza as mensagens a cada 5 segundos (para suporte)
    if (ehSuporte) {
        setInterval(() => {
            if (sessaoAtiva) {
                carregarMensagens(sessaoAtiva);
            }
        }, 5000);
    }
});

window.addEventListener('resize', () => {
    configurarUIInicial();
});