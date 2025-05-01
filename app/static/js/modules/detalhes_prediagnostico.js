document.addEventListener("DOMContentLoaded", () => {
    const filtroIdInput = document.getElementById("filtro-id");
    const nomeInput = document.getElementById("filtro-nome");
    const empresaInput = document.getElementById("filtro-empresa");

    // Função de filtragem baseada no ID, nome e empresa
    function filtrarTabela() {
        const filtroId = filtroIdInput.value.trim();
        const nomeFiltro = nomeInput.value.toLowerCase();
        const empresaFiltro = empresaInput.value.toLowerCase();
        const tabelas = document.querySelectorAll('.data-table');
        
        tabelas.forEach(tabela => {
            const linhas = tabela.querySelectorAll("tbody tr");
            
            linhas.forEach(linha => {
                const id = linha.children[0]?.textContent.trim();
                const nome = linha.children[1]?.textContent.toLowerCase();
                const empresa = linha.children[2]?.textContent.toLowerCase();

                // Verifica se o ID, nome e empresa correspondem aos filtros
                const idMatch = !filtroId || id.includes(filtroId);
                const nomeMatch = nome.includes(nomeFiltro);
                const empresaMatch = empresa.includes(empresaFiltro);

                if (idMatch && nomeMatch && empresaMatch) {
                    linha.style.display = "";
                } else {
                    linha.style.display = "none";
                }
            });
        });
    }

    // Adiciona os eventos de filtro
    filtroIdInput.addEventListener("input", filtrarTabela);
    nomeInput.addEventListener("input", filtrarTabela);
    empresaInput.addEventListener("input", filtrarTabela);
});