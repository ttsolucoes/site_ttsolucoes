document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('toggle-chat-list');
    const chatList = document.querySelector('.chat-list');
    const chatArea = document.querySelector('.chat-area');

    if (toggleBtn && chatList && chatArea) {
        toggleBtn.addEventListener('click', () => {
            // Alterna a visibilidade das áreas
            chatList.classList.toggle('show');
            chatArea.classList.toggle('hide');
        });
    }
});

