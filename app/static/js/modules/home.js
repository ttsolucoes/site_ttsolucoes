document.addEventListener('DOMContentLoaded', function() {
    const accessCards = document.querySelectorAll('.access-card');
    
    accessCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;

        card.addEventListener('mouseenter', () => {
            card.style.boxShadow = '0 10px 15px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });

    const learnMoreLinks = document.querySelectorAll('a[href="#features"]');
    learnMoreLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector('#features').scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});