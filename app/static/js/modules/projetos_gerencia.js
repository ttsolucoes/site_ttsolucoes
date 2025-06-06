document.addEventListener('DOMContentLoaded', function() {
    let mttrChart, mtbfChart;
    
    // Carrega os dados iniciais
    carregarMetricas();
    
    // Configura os filtros
    document.getElementById('filtro-periodo').addEventListener('change', carregarMetricas);
    document.getElementById('filtro-equipe').addEventListener('change', carregarMetricas);
    
    async function carregarMetricas() {
        const periodo = document.getElementById('filtro-periodo').value;
        const agente = document.getElementById('filtro-equipe').value;
        
        try {
            const [mttrData, mtbfData] = await Promise.all([
                fetch(`/api/metricas/mttr?periodo=${periodo}&agente=${agente}`).then(res => res.json()),
                fetch(`/api/metricas/mtbf?periodo=${periodo}&agente=${agente}`).then(res => res.json())
            ]);
            
            atualizarGraficos(mttrData, mtbfData);
            atualizarResumo(mttrData, mtbfData);
        } catch (error) {
            console.error('Erro ao carregar métricas:', error);
        }
    }
    
    function atualizarGraficos(mttrData, mtbfData) {
        // Destrói gráficos existentes
        if (mttrChart) mttrChart.destroy();
        if (mtbfChart) mtbfChart.destroy();

        const mttrContainer = document.getElementById('mttrInfo');
        const mtbfContainer = document.getElementById('mtbfInfo');

        // Verifica se há dados para MTTR
        if (mttrData.length === 0) {
            document.getElementById('mttrChart').style.display = 'none';
            mttrContainer.innerHTML = `
                <p><strong>Dados indisponíveis.</strong> As métricas de MTTR estarão disponíveis após 30 dias de projeto.</p>
            `;
        } else {
            document.getElementById('mttrChart').style.display = 'block';
            const mttrCtx = document.getElementById('mttrChart').getContext('2d');
            mttrChart = new Chart(mttrCtx, {
                type: 'line',
                data: {
                    labels: mttrData.map(item => item.dia),
                    datasets: [{
                        label: 'MTTR (minutos)',
                        data: mttrData.map(item => item.mttr_minutos),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                afterLabel: function(context) {
                                    const data = mttrData[context.dataIndex];
                                    return `Incidentes: ${data.total_incidentes}`;
                                }
                            }
                        }
                    }
                }
            });
        }

        // Verifica se há dados para MTBF
        if (mtbfData.length === 0) {
            document.getElementById('mtbfChart').style.display = 'none';
            mtbfContainer.innerHTML = `
                <p><strong>Dados indisponíveis.</strong> As métricas de MTBF estarão disponíveis após 30 dias de projeto.</p>
            `;
        } else {
            document.getElementById('mtbfChart').style.display = 'block';
            const mtbfCtx = document.getElementById('mtbfChart').getContext('2d');
            mtbfChart = new Chart(mtbfCtx, {
                type: 'bar',
                data: {
                    labels: mtbfData.map(item => item.semana),
                    datasets: [{
                        label: 'MTBF (horas)',
                        data: mtbfData.map(item => item.mtbf_horas),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
    }

    
    function atualizarResumo(mttrData, mtbfData) {
        // Calcula médias
        const avgMTTR = mttrData.reduce((sum, item) => sum + item.mttr_minutos, 0) / mttrData.length;
        const avgMTBF = mtbfData.reduce((sum, item) => sum + item.mtbf_horas, 0) / mtbfData.length;
        const totalIncidentes = mttrData.reduce((sum, item) => sum + item.total_incidentes, 0);

        // Verifica se as médias são válidas
        if (isNaN(avgMTTR) || isNaN(avgMTBF)) {
            document.getElementById('mttrInfo').innerHTML = '<p><strong>Dados indisponíveis.</strong> As métricas de MTTR estarão disponíveis após 30 dias de projeto. </p>';
            document.getElementById('mtbfInfo').innerHTML = '<p><strong>Dados indisponíveis.</strong> As métricas de MTBF estarão disponíveis após 30 dias de projeto. </p>';
            return;
        }

        // Atualiza HTML
        document.getElementById('mttrInfo').innerHTML = `
            <p><strong>Média:</strong> ${avgMTTR.toFixed(1)} minutos</p>
            <p><strong>Total incidentes:</strong> ${totalIncidentes}</p>
        `;
        
        document.getElementById('mtbfInfo').innerHTML = `
            <p><strong>Média:</strong> ${avgMTBF.toFixed(1)} horas</p>
            <p><strong>Estabilidade:</strong> ${calcularClassificacaoEstabilidade(avgMTBF)}</p>
        `;
    }

    carregarEquipes();

    async function carregarEquipes() {
        try {
            const resposta = await fetch('/api/equipes');
            const equipes = await resposta.json();
            const selectEquipe = document.getElementById('filtro-equipe');

            // Limpa opções anteriores
            selectEquipe.innerHTML = '';

            // Preenche novas opções
            equipes.forEach(equipe => {
                const option = document.createElement('option');
                option.value = equipe;
                option.textContent = equipe;
                selectEquipe.appendChild(option);
            });

            // Dispara a carga de métricas com a primeira equipe como padrão
            carregarMetricas();

        } catch (error) {
            console.error('Erro ao carregar equipes:', error);
        }
    }


    function calcularClassificacaoEstabilidade(mtbf) {
        if (mtbf > 168) return 'Excelente (mais de 1 semana)';
        if (mtbf > 72) return 'Boa (3-7 dias)';
        if (mtbf > 24) return 'Regular (1-3 dias)';
        return 'Baixa (menos de 1 dia)';
    }
});