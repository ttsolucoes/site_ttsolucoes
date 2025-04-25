document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.form-step');
    let currentStep = 0;
    const formData = {};

    document.querySelectorAll('.btn-next').forEach(btn => {
        btn.addEventListener('click', (e) => {
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
        btn.addEventListener('click', (e) => {
            if (currentStep > 0) {
                currentStep--;  
                showStep(currentStep);
            }
        });
    });

    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
        });
    }
    function validateStep(stepIndex) {
        const stepForm = steps[stepIndex].querySelector('form');
        return stepForm ? stepForm.checkValidity() : true;
    }

    function saveStepData(stepIndex) {
        const form = steps[stepIndex].querySelector('form');
        if (form) {
            const formDataObj = new FormData(form);
            formData[`step-${stepIndex + 1}`] = Object.fromEntries(formDataObj.entries());
        }
    }

    document.querySelector('#step-7 .btn-next')?.addEventListener('click', (e) => {
        const userConfirmation = confirm("Você deseja finalizar ou revisar suas respostas?");
        if (userConfirmation) {
            calculateResults();
        } else {
            e.preventDefault();
        }
    });

    function calculateResults() {
        const resultados = {
            final: 7.2,
            eixos: {
                'Infraestrutura & Hardware': 6.5,
                'Sistemas & Automação': 8.0,
                'Processos & Padronização': 7.0,
                'Pessoas & Capacitação': 6.0,
                'Governança & Dados': 7.5,
                'Cultura & Inovação': 7.0
            },
            proposta: 'Início Ágil (R$ 800)'
        };

        document.getElementById('result-container').innerHTML = `
            <div class="result-card">
                <h3>Maturidade Tecnológica: ${resultados.final}/10</h3>
                <div class="eixos-grid">
                    ${Object.entries(resultados.eixos).map(([eixo, nota]) => `
                        <div class="eixo-result">
                            <h4>${eixo.charAt(0).toUpperCase() + eixo.slice(1)}</h4>
                            <div class="progress-bar">
                                <div style="width: ${nota * 10}%"></div>
                            </div>
                            <span>${nota.toFixed(1)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="proposta">
                    <h4>Recomendação:</h4>
                    <p>${resultados.proposta}</p>
                </div>
            </div>
        `;
    }
});
