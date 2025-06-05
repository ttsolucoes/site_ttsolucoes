class SuporteChat {
    constructor() {
        this.sessaoAtiva = null;
        this.currentChatStatus = 'ABERTO';
        this.userData = {
            username: null,
            userId: null,
            empresa: null,
            ehSuporte: false
        };
        this.elements = {
            form: null,
            input: null,
            chatBox: null,
            conversasContainer: null,
            novaConversaBtn: null,
            finalizarChatBtn: null,
            reabrirChatBtn: null,
            novaTagInput: null,
            tagsList: null,
            toggleChatListBtn: null,
            chatList: null,
            chatArea: null
        };
        this.intervalId = null;
        this.resizeTimeout = null;
    }



    init() {
        this.cacheElements();
        this.getUserData();
        this.setupEventListeners();
        this.loadInitialData();
        this.setupAutoRefresh();
        this.adjustLayout();
    }

    cacheElements() {
        this.elements.form = document.getElementById('chat-form');
        this.elements.input = document.getElementById('chat-input');
        this.elements.chatBox = document.getElementById('chat-box');
        this.elements.conversasContainer = document.getElementById('conversas-container');
        this.elements.novaConversaBtn = document.getElementById('nova-conversa-btn');
        this.elements.finalizarChatBtn = document.getElementById('finalizar-chat');
        this.elements.reabrirChatBtn = document.getElementById('reabrir-chat');
        this.elements.novaTagInput = document.getElementById('nova-tag');
        this.elements.tagsList = document.getElementById('tags-list');
        this.elements.toggleChatListBtn = document.getElementById('toggle-chat-list');
        this.elements.chatList = document.getElementById('chat-list');
        this.elements.chatArea = document.getElementById('chat-area');
    }

    getUserData() {
        this.userData.username = window.userData?.username || '';
        this.userData.userId = window.userData?.userId || '';
        this.userData.empresa = window.userData?.empresa || '';
        this.userData.ehSuporte = window.userData?.ehSuporte || false;
    }

    setupEventListeners() {
        this.elements.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        this.elements.input.addEventListener('input', () => this.toggleSendButton());
        this.elements.novaTagInput?.addEventListener('keydown', (e) => this.handleTagInput(e));
        this.elements.finalizarChatBtn?.addEventListener('click', () => this.finalizarChat());
        this.elements.reabrirChatBtn?.addEventListener('click', () => this.reabrirChat());
        this.elements.novaConversaBtn?.addEventListener('click', () => this.criarConversa());
        this.elements.toggleChatListBtn?.addEventListener('click', () => this.toggleChatList());
        window.addEventListener('resize', () => this.adjustLayout());
    }

    async loadInitialData() {
        await this.carregarConversas();
        if (!this.sessaoAtiva && this.elements.conversasContainer.children.length > 0) {
            const primeiraConversa = this.elements.conversasContainer.children[0];
            const sessaoId = primeiraConversa.dataset.sessaoId;
            await this.carregarMensagens(sessaoId);
        } else if (this.elements.conversasContainer.children.length === 0 && !this.userData.ehSuporte) {
            await this.criarConversa();
        }
    }

    setupAutoRefresh() {
        clearInterval(this.intervalId);
        this.intervalId = setInterval(async () => {
            if (this.sessaoAtiva) {
                await this.atualizarMensagensSessaoAtiva();
            }
        }, 2000); // Alterado para 5 segundos
    }

    adjustLayout() {
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            if (window.innerWidth < 768) {
                this.elements.chatList.style.display = 'none';
                this.elements.chatArea.style.display = 'block';
                this.elements.toggleChatListBtn.setAttribute('aria-expanded', 'false');
            } else {
                this.elements.chatList.style.display = 'block';
                this.elements.chatArea.style.display = 'block';
                this.elements.toggleChatListBtn.setAttribute('aria-expanded', 'true');
            }
        }, 100);
    }

    toggleChatList() {
        const isExpanded = this.elements.toggleChatListBtn.getAttribute('aria-expanded') === 'true';
        if (window.innerWidth < 768) {
            this.elements.chatList.style.display = isExpanded ? 'none' : 'block';
            this.elements.chatArea.style.display = isExpanded ? 'block' : 'none';
            this.elements.toggleChatListBtn.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        const mensagem = this.elements.input.value.trim();
        if (!mensagem) return;
        await this.enviarMensagem(mensagem);
        this.elements.input.value = '';
        this.toggleSendButton();
    }

    toggleSendButton() {
        const enviarBtn = this.elements.form.querySelector('#enviar-btn');
        enviarBtn.disabled = this.elements.input.value.trim() === '' || this.currentChatStatus === 'FINALIZADO';
    }

    async handleTagInput(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tag = this.elements.novaTagInput.value.trim();
            if (tag) {
                await this.adicionarTag(tag);
                this.elements.novaTagInput.value = '';
            }
        }
    }

    async atualizarMensagensSessaoAtiva() {
        if (!this.sessaoAtiva) return;
        
        try {
            const response = await fetch(`/api/sessoes/${this.sessaoAtiva}/mensagens`);
            if (!response.ok) throw new Error('Erro ao atualizar mensagens');
            
            const mensagens = await response.json();
            const currentMsgCount = document.querySelectorAll('.chat-message').length;
            
            // Só renderiza se houver novas mensagens
            if (mensagens.length !== currentMsgCount) {
                this.renderMensagens(mensagens);
            }
        } catch (error) {
            console.error('Erro ao atualizar mensagens:', error);
        }
    }

    renderMensagens(mensagens) {

        // Manter a posição do scroll se o usuário não estiver no final
        const wasScrolledToBottom = this.isScrolledToBottom();
        
        this.elements.chatBox.innerHTML = mensagens.map(msg => {
            const msgClass = (msg.autor === this.userData.username) ? 'me' :
                           (msg.eh_suporte ? 'suporte' : 'other');
            return `
                <div class="chat-message ${msgClass}">
                    <div class="msg-autor">${msg.autor}</div>
                    <div class="msg-texto">${msg.mensagem}</div>
                    <div class="msg-data">${this.formatarData(msg.enviada_em)}</div>
                </div>
            `;
        }).join('');
        
        // Restaurar a posição do scroll
        if (wasScrolledToBottom) {
            this.scrollToBottom();
        }
    }

    formatarData(dataString) {
        if (!dataString) return '';
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR') + ' ' +
               data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    async carregarConversas(manterSessaoAtual = true) {
        try {
            const response = await fetch('/api/sessoes');
            if (!response.ok) throw new Error('Erro ao carregar conversas');
            const sessoes = await response.json();
            this.renderConversas(sessoes);

            // Garante que a sessão ativa só é definida se for necessário
            if (!manterSessaoAtual || !this.sessaoAtiva) {
                const primeiraSessao = sessoes[0];
                if (primeiraSessao) {
                    this.sessaoAtiva = primeiraSessao.id;
                    await this.carregarMensagens(this.sessaoAtiva);
                }
            }
        } catch (error) {
            console.error('Erro ao carregar conversas:', error);
            this.mostrarNotificacao('Erro ao carregar conversas', 'error');
        }
    }


    renderConversas(sessoes) {
        this.elements.conversasContainer.innerHTML = sessoes.map(sessao => {
            const titulo = (this.userData.ehSuporte && sessao.usuario_nome) ?
                         `${sessao.titulo} (${sessao.usuario_nome})` : sessao.titulo;
            return `
                <div class="conversa-item ${sessao.id === this.sessaoAtiva ? 'ativa' : ''}" 
                     data-sessao-id="${sessao.id}">
                    <div class="conversa-titulo">${titulo}</div>
                    <div class="conversa-status ${sessao.status?.toLowerCase() || 'aberto'}">
                        ${sessao.status || 'ABERTO'}
                    </div>
                    <div class="conversa-data">${this.formatarData(sessao.atualizado_em)}</div>
                </div>
            `;
        }).join('');

        // Adiciona event listeners para cada conversa
        document.querySelectorAll('.conversa-item').forEach(item => {
            item.addEventListener('click', async () => {
                const sessaoId = item.dataset.sessaoId;
                await this.carregarMensagens(sessaoId);
                if (window.innerWidth < 768) {
                    this.elements.chatList.style.display = 'none';
                    this.elements.chatArea.style.display = 'block';
                    this.elements.toggleChatListBtn.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }

    async carregarMensagens(sessaoId) {
        if (this.sessaoAtiva === sessaoId) return;
        try {
            const [mensagensResponse, sessaoResponse] = await Promise.all([
                fetch(`/api/sessoes/${sessaoId}/mensagens`),
                fetch(`/api/sessoes/${sessaoId}`)
            ]);

            if (!mensagensResponse.ok || !sessaoResponse.ok) {
                throw new Error('Erro ao carregar chat');
            }

            const mensagens = await mensagensResponse.json();
            const sessao = await sessaoResponse.json();

            this.sessaoAtiva = sessaoId;
            this.currentChatStatus = sessao.status || 'ABERTO';

            this.renderMensagens(mensagens);
            this.scrollToBottom(); // Adicionar esta linha
            this.atualizarUIStatusChat();

            if (this.userData.ehSuporte) {
                this.atualizarTags(sessao.tags || []);
            }

            // Atualiza a classe ativa nas conversas
            document.querySelectorAll('.conversa-item').forEach(item => {
                item.classList.toggle('ativa', item.dataset.sessaoId === sessaoId);
            });

        } catch (error) {
            console.error('Erro ao carregar mensagens:', error);
            this.mostrarNotificacao('Erro ao carregar mensagens', 'error');
        }
    }

    atualizarUIStatusChat() {
        if (!this.userData.ehSuporte) return;

        if (this.elements.finalizarChatBtn) {
            this.elements.finalizarChatBtn.style.display = (this.currentChatStatus === 'ABERTO') ? 'inline-block' : 'none';
        }
        if (this.elements.reabrirChatBtn) {
            this.elements.reabrirChatBtn.style.display = (this.currentChatStatus === 'FINALIZADO') ? 'inline-block' : 'none';
        }

        this.elements.input.disabled = (this.currentChatStatus === 'FINALIZADO');
        this.toggleSendButton();
    }

    async enviarMensagem(mensagem) {
        if (!this.sessaoAtiva) {
            await this.criarConversa(mensagem);
            return;
        }

        if (this.currentChatStatus === 'FINALIZADO') {
            this.mostrarNotificacao('Chat finalizado. Não é possível enviar mensagens.', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/sessoes/${this.sessaoAtiva}/mensagens`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem })
            });

            if (!response.ok) throw new Error('Erro ao enviar mensagem');

            await this.carregarMensagens(this.sessaoAtiva);
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.mostrarNotificacao('Erro ao enviar mensagem', 'error');
        }
    }

    async criarConversa(primeiraMsg = null) {
        try {
            if (!primeiraMsg) {
                primeiraMsg = prompt("Digite sua mensagem inicial para o suporte:");
                if (!primeiraMsg) return;
            }

            const response = await fetch('/api/sessoes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    titulo: 'Nova conversa',
                    primeira_msg: primeiraMsg
                })
            });

            if (!response.ok) throw new Error('Erro ao criar conversa');

            const novaSessao = await response.json();
            await this.carregarMensagens(novaSessao.id);
            await this.carregarConversas(false);
            this.mostrarNotificacao('Conversa criada com sucesso', 'success');
        } catch (error) {
            console.error('Erro ao criar conversa:', error);
            this.mostrarNotificacao('Erro ao criar conversa', 'error');
        }
    }

    async finalizarChat() {
        await this.atualizarStatusChat('FINALIZADO');
        this.mostrarNotificacao('Chat finalizado', 'success');
    }

    async reabrirChat() {
        await this.atualizarStatusChat('REABERTO');
        this.mostrarNotificacao('Chat reaberto', 'success');
    }

    async atualizarStatusChat(status) {
        try {
            const response = await fetch(`/api/sessoes/${this.sessaoAtiva}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro ao atualizar status');
            }

            this.currentChatStatus = status;
            this.atualizarUIStatusChat();

        } catch (error) {
            console.error('Erro ao atualizar status:', error);
            this.mostrarNotificacao('Erro ao atualizar status do chat', 'error');
        }
    }

    atualizarTags(tags = []) {
        if (!this.elements.tagsList) return;
        this.elements.tagsList.innerHTML = tags.map(tag => `
            <span class="tag">
                ${tag}
                <button type="button" aria-label="Remover tag ${tag}" 
                        onclick="suporteChat.removerTag('${tag}')">×</button>
            </span>
        `).join('');
    }

    async adicionarTag(tag) {
        if (!tag.trim()) return;

        try {
            const response = await fetch(`/api/sessoes/${this.sessaoAtiva}/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag: tag.trim() })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro ao adicionar tag');
            }

            const sessaoResponse = await fetch(`/api/sessoes/${this.sessaoAtiva}`);
            const sessao = await sessaoResponse.json();
            this.atualizarTags(sessao.tags);

        } catch (error) {
            console.error('Erro ao adicionar tag:', error);
            this.mostrarNotificacao('Erro ao adicionar tag', 'error');
        }
    }

    async removerTag(tag) {
        try {
            const response = await fetch(`/api/sessoes/${this.sessaoAtiva}/tags/${encodeURIComponent(tag)}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Erro ao remover tag');

            const sessaoResponse = await fetch(`/api/sessoes/${this.sessaoAtiva}`);
            const sessao = await sessaoResponse.json();
            this.atualizarTags(sessao.tags);

        } catch (error) {
            console.error('Erro ao remover tag:', error);
            this.mostrarNotificacao('Erro ao remover tag', 'error');
        }
    }

    // Adicionar novos métodos auxiliares:
    isScrolledToBottom() {
        const { chatBox } = this.elements;
        return chatBox.scrollHeight - chatBox.clientHeight <= chatBox.scrollTop + 10;
    }

    scrollToBottom() {
        const { chatBox } = this.elements;
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    mostrarNotificacao(mensagem, tipo = 'info') {
        const notificacao = document.createElement('div');
        notificacao.className = `notificacao notificacao-${tipo}`;
        notificacao.textContent = mensagem;
        notificacao.setAttribute('role', 'alert');

        document.body.appendChild(notificacao);
        setTimeout(() => notificacao.remove(), 3000);
    }

    destroy() {
        clearInterval(this.intervalId);
        // Remove todos os event listeners
        this.elements.form.removeEventListener('submit', this.handleFormSubmit);
        this.elements.input.removeEventListener('input', this.toggleSendButton);
        this.elements.novaTagInput?.removeEventListener('keydown', this.handleTagInput);
        this.elements.finalizarChatBtn?.removeEventListener('click', this.finalizarChat);
        this.elements.reabrirChatBtn?.removeEventListener('click', this.reabrirChat);
        this.elements.novaConversaBtn?.removeEventListener('click', this.criarConversa);
        this.elements.toggleChatListBtn?.removeEventListener('click', this.toggleChatList);
        window.removeEventListener('resize', this.adjustLayout);
    }
}


// Instancia e inicializa o chat
const suporteChat = new SuporteChat();
document.addEventListener('DOMContentLoaded', () => suporteChat.init());



// Expõe métodos necessários para uso global
window.suporteChat = suporteChat;