document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-chat-list');
    const chatList = document.querySelector('.chat-list');
    
    if (toggleBtn && chatList) {
        // Estado inicial - oculto em mobile, visível em desktop
        const isMobile = window.matchMedia('(max-width: 768px)').matches;
        
        if (isMobile) {
            chatList.classList.remove('show');
            toggleBtn.textContent = 'Mostrar Conversas';
        } else {
            chatList.classList.add('show');
            toggleBtn.textContent = 'Ocultar Conversas';
        }
        
        toggleBtn.addEventListener('click', function() {
            // Alterna a classe 'show' na lista de chats
            chatList.classList.toggle('show');
            
            // Atualiza o texto do botão
            if (chatList.classList.contains('show')) {
                toggleBtn.textContent = 'Ocultar Conversas';
            } else {
                toggleBtn.textContent = 'Mostrar Conversas';
            }
        });
    }
});