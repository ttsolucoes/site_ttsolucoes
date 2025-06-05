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
        
        // Configuração do gráfico MTTR
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
        
        // Configuração do gráfico MTBF
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
    
    function atualizarResumo(mttrData, mtbfData) {
        // Calcula médias
        const avgMTTR = mttrData.reduce((sum, item) => sum + item.mttr_minutos, 0) / mttrData.length;
        const avgMTBF = mtbfData.reduce((sum, item) => sum + item.mtbf_horas, 0) / mtbfData.length;
        const totalIncidentes = mttrData.reduce((sum, item) => sum + item.total_incidentes, 0);
        
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
    
    function calcularClassificacaoEstabilidade(mtbf) {
        if (mtbf > 168) return 'Excelente (mais de 1 semana)';
        if (mtbf > 72) return 'Boa (3-7 dias)';
        if (mtbf > 24) return 'Regular (1-3 dias)';
        return 'Baixa (menos de 1 dia)';
    }
});