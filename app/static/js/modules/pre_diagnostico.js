document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.form-step');
    let currentStep = 0;
    const formData = {};
    const pesosMaximos = {
        eixo1: 1.5,
        eixo2: 2,
        eixo3: 2,
        eixo4: 1.5,
        eixo5: 1.5,
        eixo6: 1.5
    };

    const nomesEixos = {
        eixo1: 'Infraestrutura & Hardware',
        eixo2: 'Sistemas & Automação',
        eixo3: 'Processos & Padronização',
        eixo4: 'Pessoas & Capacitação',
        eixo5: 'Governança & Dados',
        eixo6: 'Cultura & Inovação',
    };

    document.querySelectorAll('.btn-next').forEach(btn => {
        btn.addEventListener('click', () => {
            if (validateStep(currentStep)) {
                saveStepData(currentStep);
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    showStep(currentStep);
                }
            }
        });
    });

    document.querySelectorAll('.btn-prev').forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    function showStep(index) {
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
        });
    }

    function validateStep(index) {
        const form = steps[index].querySelector('form');
        if (!form) return true;

        const isValid = form.checkValidity();
        if (!isValid) form.reportValidity();

        return isValid;
    }
    function saveStepData(index) {
        const form = steps[index].querySelector('form');
        if (form) {
            const formEntries = new FormData(form);
            formData[`step-${index + 1}`] = Object.fromEntries(formEntries.entries());
        }
    }

    document.querySelector('#step-7 .btn-next')?.addEventListener('click', () => {
        const confirmar = confirm("Você deseja finalizar ou revisar suas respostas?");
        if (confirmar) {
            saveStepData(currentStep);
            enviarDados();
        } else {
            showStep(6);
        }
    });

    function enviarDados() {
        // Desabilita o botão de reiniciar
        const restartBtn = document.querySelector('.btn-restart');
        restartBtn.disabled = true;
        restartBtn.textContent = 'Processando...';
        restartBtn.style.opacity = '0.7';
        restartBtn.style.cursor = 'not-allowed';
        
        fetch('/pre_diagnostico_salvar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(async response => {
            if (!response.ok) {
                const erroTexto = await response.text();
                throw new Error(`Erro do servidor: ${erroTexto}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                alert('Diagnóstico salvo com sucesso!');
                calculateResults(data.data);
            } else {
                alert('Erro ao salvar diagnóstico: ' + (data.message || 'Desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro ao enviar dados:', error);
            alert('Erro de comunicação com o servidor.');
        })
        .finally(() => {
            // Reabilita o botão de reiniciar independentemente do resultado
            restartBtn.disabled = false;
            restartBtn.textContent = 'Reiniciar';
            restartBtn.style.opacity = '1';
            restartBtn.style.cursor = 'pointer';
        });
    }

    function calculateResults(data) {
        if (!data || !data.info_final) {
            console.error("Dados incompletos:", data);
            alert("Erro ao calcular resultados.");
            return;
        }
    
        const { media_final, media_eixos, proposta } = data.info_final;
    
        const nomesEixos = {
            eixo1: 'Infraestrutura & Hardware',
            eixo2: 'Sistemas & Automação',
            eixo3: 'Processos & Padronização',
            eixo4: 'Pessoas & Capacitação',
            eixo5: 'Governança & Dados',
            eixo6: 'Cultura & Inovação',
        };
    
        document.getElementById('result-container').innerHTML = `
        <div class="result-card">
            <h3>Maturidade Tecnológica: ${media_final.toFixed(2)}/10</h3>
            <div class="eixos-grid">
                ${Object.entries(media_eixos).map(([eixo, nota]) => `
                    <div class="eixo-result">
                        <h4>${nomesEixos[eixo]}</h4>
                        <div class="progress-bar">
                            <div style="width: ${(nota / pesosMaximos[eixo] * 100)}%"></div>
                        </div>
                        <span>${nota.toFixed(2)}/${pesosMaximos[eixo]}</span>
                    </div>
                `).join('')}
            </div>
            <div class="proposta">
                <h4>Recomendação:</h4>
                <p>${proposta}</p>
            </div>
        </div>
        `;
    }
    

});
