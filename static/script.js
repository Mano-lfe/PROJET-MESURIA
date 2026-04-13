// Initialisation des animations
document.addEventListener('DOMContentLoaded', function() {
    // Animation des cartes au défilement
    const animateOnScroll = () => {
        const cards = document.querySelectorAll('.stat-card, .info-card, .feature-card');
        const windowHeight = window.innerHeight;
        
        cards.forEach((card, index) => {
            const cardPosition = card.getBoundingClientRect().top;
            
            if (cardPosition < windowHeight - 100) {
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    };

    // Définir l'opacité initiale des cartes
    const cards = document.querySelectorAll('.stat-card, .info-card, .feature-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    });

    // Lancer l'animation au chargement
    setTimeout(() => {
        animateOnScroll();
    }, 300);

    // Lancer l'animation au défilement
    window.addEventListener('scroll', animateOnScroll);

    // Animation pour les chiffres
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(statNumber => {
        const finalNumber = parseInt(statNumber.textContent);
        let currentNumber = 0;
        const increment = finalNumber / 50;
        const timer = setInterval(() => {
            currentNumber += increment;
            if (currentNumber >= finalNumber) {
                currentNumber = finalNumber;
                clearInterval(timer);
            }
            statNumber.textContent = Math.floor(currentNumber) + (statNumber.textContent.includes('%') ? '%' : '+');
        }, 50);
    });

    // Effet de particules interactives
    const createParticles = () => {
        const container = document.querySelector('.background-animation');
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 5 + 2}px;
                height: ${Math.random() * 5 + 2}px;
                background: rgba(80, 179, 162, ${Math.random() * 0.3 + 0.1});
                border-radius: 50%;
                top: ${Math.random() * 100}%;
                left: ${Math.random() * 100}%;
                pointer-events: none;
            `;
            container.appendChild(particle);
            
            // Animation de déplacement
            animateParticle(particle);
        }
    };

    const animateParticle = (particle) => {
        let x = Math.random() * 100;
        let y = Math.random() * 100;
        let xSpeed = (Math.random() - 0.5) * 0.5;
        let ySpeed = (Math.random() - 0.5) * 0.5;
        
        const move = () => {
            x += xSpeed;
            y += ySpeed;
            
            // Rebond sur les bords
            if (x <= 0 || x >= 100) xSpeed *= -1;
            if (y <= 0 || y >= 100) ySpeed *= -1;
            
            particle.style.left = `${x}%`;
            particle.style.top = `${y}%`;
            
            requestAnimationFrame(move);
        };
        
        move();
    };

    // Créer les particules interactives
    setTimeout(createParticles, 1000);

    // Effet de survol pour les boutons
    const buttons = document.querySelectorAll('button, .btn-primary, .btn-secondary, .contact-btn, .feature-btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function(e) {
            const x = e.pageX - this.offsetLeft;
            const y = e.pageY - this.offsetTop;
            
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            const size = Math.max(this.offsetWidth, this.offsetHeight);
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x - size/2}px`;
            ripple.style.top = `${y - size/2}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Ajouter l'animation ripple au CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// Animation pour le titre
window.addEventListener('load', function() {
    const title = document.querySelector('.hero-title');
    const letters = title.textContent.split('');
    title.textContent = '';
    
    letters.forEach((letter, i) => {
        const span = document.createElement('span');
        span.textContent = letter;
        span.style.opacity = '0';
        span.style.display = 'inline-block';
        span.style.animation = `letterAppear 0.5s ease forwards ${i * 0.05}s`;
        title.appendChild(span);
    });
    
    // Ajouter l'animation des lettres
    const style = document.createElement('style');
    style.textContent = `
        @keyframes letterAppear {
            from {
                opacity: 0;
                transform: translateY(20px) rotate(10deg);
            }
            to {
                opacity: 1;
                transform: translateY(0) rotate(0deg);
            }
        }
    `;
    document.head.appendChild(style);
});