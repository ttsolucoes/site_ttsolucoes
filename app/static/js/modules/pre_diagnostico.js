document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.form-step');
    let currentStep = 0;
    const formData = {};

    // Botões de avanço
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

    // Botões de voltar
    document.querySelectorAll('.btn-prev').forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    // Mostra o passo atual
    function showStep(index) {
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
        });
    }

    // Valida os campos obrigatórios do passo
    function validateStep(index) {
        const form = steps[index].querySelector('form');
        if (!form) return true;

        const isValid = form.checkValidity();
        if (!isValid) form.reportValidity();

        return isValid;
    }

    // Salva dados do passo atual no formData
    function saveStepData(index) {
        const form = steps[index].querySelector('form');
        if (form) {
            const formEntries = new FormData(form);
            formData[`step-${index + 1}`] = Object.fromEntries(formEntries.entries());
        }
    }

    // Botão de finalização no passo 7
    document.querySelector('#step-7 .btn-next')?.addEventListener('click', () => {
        const confirmar = confirm("Você deseja finalizar ou revisar suas respostas?");
        if (confirmar) {
            saveStepData(currentStep); // salva último passo antes de enviar
            enviarDados();
        } else {
            showStep(6);
        }
    });

    // Envia dados para o backend
    function enviarDados() {
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
        });
    }

    // Calcula e exibe os resultados
    function calculateResults(data) {
        if (!data || !data.info_final) {
            console.error("Dados incompletos para exibir resultados:", data);
            alert("Não foi possível calcular os resultados. Tente novamente.");
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
                <h3>Maturidade Tecnológica: ${media_final.toFixed(1)}/10</h3>
                <div class="eixos-grid">
                    ${Object.entries(media_eixos).map(([eixo, nota]) => `
                        <div class="eixo-result">
                            <h4>${nomesEixos[eixo]}</h4>
                            <div class="progress-bar">
                                <div style="width: ${(nota * 5)}%"></div>
                            </div>
                            <span>${(nota / 2).toFixed(1)}</span>
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
