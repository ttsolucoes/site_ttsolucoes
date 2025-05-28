document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");

    const username = "{{ users.username }}"; // renderizado no HTML
    const empresa = "{{ empresa }}";

    // MOCK: simular mensagens existentes
    const mensagensMock = [
        { autor: "luiz.esquivel", mensagem: "Olá, tudo bem?" },
        { autor: "suporte", mensagem: "Olá Luiz! Como podemos ajudar?" }
    ];

    function renderMensagens(mensagens) {
        chatBox.innerHTML = "";
        mensagens.forEach(msg => {
            const msgEl = document.createElement("div");
            msgEl.classList.add("chat-message");
            msgEl.classList.add(msg.autor === username ? "me" : "other");
            msgEl.innerText = msg.mensagem;
            chatBox.appendChild(msgEl);
        });
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    renderMensagens(mensagensMock); // simulação inicial

    form.addEventListener("submit", e => {
        e.preventDefault();
        const novaMsg = input.value.trim();
        if (!novaMsg) return;

        mensagensMock.push({ autor: username, mensagem: novaMsg });
        renderMensagens(mensagensMock);

        input.value = "";
    });
});
