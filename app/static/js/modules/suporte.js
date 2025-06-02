window.sessaoAtiva = null;
window.currentChatStatus = 'ABERTO';

async function mostrarNotificacao(mensagem, tipo = 'info') {
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao notificacao-${tipo}`;
    notificacao.textContent = mensagem;
    
    document.body.appendChild(notificacao);
    setTimeout(() => notificacao.remove(), 3000);
}

async function atualizarMensagensSessaoAtiva() {
    if (!sessaoAtiva) return;

    try {
        const response = await fetch(`/api/sessoes/${sessaoAtiva}/mensagens`);
        if (!response.ok) throw new Error('Erro ao atualizar mensagens');

        const mensagens = await response.json();
    } catch (error) {
        console.error('Erro ao atualizar mensagens da sessão ativa:', error);
    }
}

window.removerTag = async function(tag) {
    try {
        const response = await fetch(`/api/sessoes/${sessaoAtiva}/tags`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag })
        });

        if (!response.ok) throw new Error('Erro ao remover tag');

        const sessao = await response.json();
        atualizarTags(sessao.tags);
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('Erro ao remover tag', 'error');
    }
};

async function encerrarConversa() {
    if (!window.sessaoAtiva) {
        console.error('Nenhuma sessão ativa para encerrar');
        mostrarNotificacao('Nenhuma conversa ativa para encerrar', 'error');
        return;
    }

    fetch(`/api/sessoes/${window.sessaoAtiva}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'FINALIZADO' })
    })
    .then(response => {
        if (!response.ok) throw new Error('Erro ao atualizar status');
        return response.json();
    })
    .then(data => {
        console.log('Status atualizado para:', data.status);
        mostrarNotificacao('Conversa finalizada com sucesso', 'success');
        
        // Atualiza a UI
        document.getElementById('finalizar-chat').style.display = 'none';
        document.getElementById('reabrir-chat').style.display = 'block';
        
        // Atualiza o status global
        window.currentChatStatus = 'FINALIZADO';
        
        // Atualiza a lista de conversas
        if (window.carregarConversas) window.carregarConversas();
    })
    .catch(error => {
        console.error('Erro ao encerrar conversa:', error);
        mostrarNotificacao('Erro ao finalizar conversa', 'error');
    });
}


// Configuração inicial da UI
function configurarUIInicial() {
    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    const chatList = document.querySelector('.chat-list');
    const chatArea = document.querySelector('.chat-area');
    const toggleBtn = document.getElementById('toggle-chat-list');

    if (isMobile) {
        chatList.classList.remove('show');
        chatArea.classList.remove('hide');
        toggleBtn.textContent = 'Mostrar Conversas';
    } else {
        chatList.classList.add('show');
        chatArea.classList.remove('hide');
        toggleBtn.textContent = 'Ocultar Conversas';
    }
}

// Função principal
document.addEventListener("DOMContentLoaded", () => {
    // Elementos da UI
    const elements = {
        form: document.getElementById("chat-form"),
        input: document.getElementById("chat-input"),
        chatBox: document.getElementById("chat-box"),
        conversasContainer: document.getElementById("conversas-container"),
        novaConversaBtn: document.getElementById("nova-conversa-btn"),
        finalizarChatBtn: document.getElementById("finalizar-chat"),
        reabrirChatBtn: document.getElementById("reabrir-chat"),
        novaTagInput: document.getElementById("nova-tag"),
        tagsList: document.getElementById("tags-list")
    };

    // Dados do usuário
    const userData = {
        username: "{{ users.username }}",
        userId: "{{ users.id }}",
        empresa: "{{ empresa }}",
        ehSuporte: "{{ eh_suporte }}" === "True"
    };

    // Configuração inicial
    configurarUIInicial();
    setupEventListeners();
    carregarConversas();

    // Funções principais
    function setupEventListeners() {
        elements.form.addEventListener("submit", handleSubmit);
        elements.novaConversaBtn.addEventListener('click', criarConversa);
        
        if (userData.ehSuporte) {
            elements.finalizarChatBtn.addEventListener('click', finalizarChat);
            elements.reabrirChatBtn.addEventListener('click', reabrirChat);
            elements.novaTagInput.addEventListener('keypress', handleTagInput);
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        const mensagem = elements.input.value.trim();
        if (!mensagem) return;

        await enviarMensagem(mensagem);
        elements.input.value = "";
    }

    async function carregarConversas() {
        try {
            const response = await fetch('/api/sessoes');
            if (!response.ok) throw new Error('Erro ao carregar conversas');
            
            const sessoes = await response.json();
            renderConversas(sessoes);
            
            if (!window.sessaoAtiva && sessoes.length > 0) {
                await carregarMensagens(sessoes[0].id);
            } else if (sessoes.length === 0 && !userData.ehSuporte) {
                await criarConversa();
            }
        } catch (error) {
            console.error('Erro ao carregar conversas:', error);
        }
    }

    function renderConversas(sessoes) {
        elements.conversasContainer.innerHTML = '';
        
        sessoes.forEach(sessao => {
            const conversaEl = document.createElement('div');
            conversaEl.className = sessao.id === window.sessaoAtiva ? 'conversa-item ativa' : 'conversa-item';
            
            const titulo = userData.ehSuporte && sessao.usuario_nome ? 
                `${sessao.titulo} (${sessao.usuario_nome})` : sessao.titulo;
            
            conversaEl.innerHTML = `
                <div class="conversa-titulo">${titulo}</div>
                <div class="conversa-status ${sessao.status?.toLowerCase()}">${sessao.status || 'ABERTO'}</div>
                <div class="conversa-data">${formatarData(sessao.atualizado_em)}</div>
            `;
            
            conversaEl.addEventListener('click', () => carregarMensagens(sessao.id));
            elements.conversasContainer.appendChild(conversaEl);
        });
    }

    async function carregarMensagens(sessaoId) {
        try {
            const [mensagensResponse, sessaoResponse] = await Promise.all([
                fetch(`/api/sessoes/${sessaoId}/mensagens`),
                fetch(`/api/sessoes`)
            ]);
            
            if (!mensagensResponse.ok) {
                mostrarNotificacao('Erro ao carregar mensagens do chat', 'error');
                throw new Error('Erro ao carregar mensagens do chat');
            }
            if (!sessaoResponse.ok) {
                mostrarNotificacao('Erro ao carregar dados da sessão do chat', 'error');
                throw new Error('Erro ao carregar dados da sessão do chat');
            }
            
            const [mensagens, sessao] = await Promise.all([
                mensagensResponse.json(),
                sessaoResponse.json()
            ]);
            
            window.sessaoAtiva = sessaoId;
            window.currentChatStatus = sessao.status || 'ABERTO';
            
            renderMensagens(mensagens);
            atualizarUIStatusChat();
            if (userData.ehSuporte) atualizarTags(sessao.tags);
            
            carregarConversas(); // Atualiza a lista de conversas
        } catch (error) {
            console.error('Erro ao carregar mensagens:', error);
        }
    }

    function renderMensagens(mensagens) {
        elements.chatBox.innerHTML = "";
        mensagens.forEach(msg => {
            const msgClass = msg.autor === userData.username ? 'me' : 
                           msg.eh_suporte ? 'suporte' : 'other';
            
            const msgEl = document.createElement("div");
            msgEl.className = `chat-message ${msgClass}`;
            msgEl.innerHTML = `
                <div class="msg-autor">${msg.autor}</div>
                <div class="msg-texto">${msg.mensagem}</div>
                <div class="msg-data">${formatarData(msg.enviada_em)}</div>
            `;
            elements.chatBox.appendChild(msgEl);
        });
        elements.chatBox.scrollTop = elements.chatBox.scrollHeight;
    }

    function atualizarUIStatusChat() {
        if (!userData.ehSuporte) return;
        
        elements.finalizarChatBtn.style.display = window.currentChatStatus === 'ABERTO' ? 'block' : 'none';
        elements.reabrirChatBtn.style.display = window.currentChatStatus === 'FINALIZADO' ? 'block' : 'none';
    }

    async function finalizarChat() {
        await atualizarStatusChat('FINALIZADO');
        window.currentChatStatus = 'FINALIZADO';
        atualizarUIStatusChat();
        mostrarNotificacao('Chat finalizado', 'success');
    }

    async function reabrirChat() {
        await atualizarStatusChat('REABERTO');
        window.currentChatStatus = 'REABERTO';
        atualizarUIStatusChat();
        mostrarNotificacao('Chat reaberto', 'success');
    }

    async function atualizarStatusChat(status) {
        try {
            const response = await fetch(`/api/sessoes/${window.sessaoAtiva}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            
            if (!response.ok) throw new Error('Erro ao atualizar status');
        } catch (error) {
            console.error('Erro:', error);
            mostrarNotificacao('Erro ao atualizar status do chat', 'error');
        }
    }

    async function criarConversa() {
        try {
            const primeiraMsg = prompt("Digite sua mensagem inicial para o suporte:");
            if (!primeiraMsg) return;
            
            const response = await fetch('/api/sessoes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    titulo: '',
                    primeira_msg: primeiraMsg 
                })
            });
            
            if (!response.ok) throw new Error('Erro ao criar conversa');
            
            const novaSessao = await response.json();
            await carregarMensagens(novaSessao.id);
            mostrarNotificacao('Conversa criada com sucesso', 'success');
        } catch (error) {
            console.error('Erro ao criar conversa:', error);
            mostrarNotificacao('Erro ao criar conversa', 'error');
        }
    }

    async function enviarMensagem(mensagem) {
        if (!window.sessaoAtiva) {
            await criarConversa();
            return;
        }
        
        try {
            const response = await fetch(`/api/sessoes/${window.sessaoAtiva}/mensagens`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem })
            });
            
            if (!response.ok) throw new Error('Erro ao enviar mensagem');
            
            const novaMsg = await response.json();
            carregarMensagens(window.sessaoAtiva);
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            mostrarNotificacao('Erro ao enviar mensagem', 'error');
        }
    }

    // Funções para tags
    function handleTagInput(e) {
        if (e.key === 'Enter' && e.target.value.trim()) {
            adicionarTag(e.target.value.trim());
            e.target.value = '';
        }
    }

    async function adicionarTag(tag) {
        try {
            const response = await fetch(`/api/sessoes/${window.sessaoAtiva}/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag })
            });
            
            if (!response.ok) throw new Error('Erro ao adicionar tag');
            
            const sessao = await response.json();
            atualizarTags(sessao.tags);
        } catch (error) {
            console.error('Erro:', error);
            mostrarNotificacao('Erro ao adicionar tag', 'error');
        }
    }

    function atualizarTags(tags = []) {
        elements.tagsList.innerHTML = tags.map(tag => `
            <span class="tag">
                ${tag}
                <button onclick="removerTag('${tag}')">×</button>
            </span>
        `).join('');
    }

    // Funções utilitárias
    function formatarData(dataString) {
        if (!dataString) return '';
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR') + ' ' + data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    setInterval(atualizarMensagensSessaoAtiva, 1000);
    
});

window.addEventListener('resize', configurarUIInicial);