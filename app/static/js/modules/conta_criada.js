document.addEventListener('DOMContentLoaded', function() {
    const countdownEl = document.createElement('div');
    countdownEl.className = 'countdown';
    countdownEl.textContent = 'Redirecionando em 10 segundos...';
    document.querySelector('.success-actions').prepend(countdownEl);
    
    let seconds = 10;
    const interval = setInterval(() => {
        seconds--;
        countdownEl.textContent = `Redirecionando em ${seconds} segundos...`;
        
        if (seconds <= 0) {
            clearInterval(interval);
            window.location.href = "/index";
        }
    }, 1000);
});