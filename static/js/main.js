/**
 * Main JavaScript File
 * Entry point that loads all required scripts in the correct order
 */

// Function to load scripts in sequence
function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Script load error: ${src}`));
        document.head.appendChild(script);
    });
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initializing portfolio application...');
    
    try {
        // Load base scripts first
        await loadScript('/static/js/base.js');
        console.log('Base script loaded');
        
        // Load components 
        await loadScript('/static/js/components/header.js');
        console.log('Header component loaded');
        
        // Initialize page-specific features
        initHomePage();
        
        // Animate the floating theme button after page load
        setTimeout(() => {
            const floatBtn = document.getElementById('theme-float-toggle');
            if (floatBtn) {
                floatBtn.classList.add('animate-fadeIn');
            }
        }, 1000);
    } catch (error) {
        console.error('Error initializing application:', error);
    }
});

/**
 * Initialize home page specific features
 */
function initHomePage() {
    // Replace typewriter with modern text animation
    futuristicTextEffect();
    
    // Initialize animations that are independent of themes
    initAnimations();
}

/**
 * Modern futuristic text animation for hero section
 */
function futuristicTextEffect() {
    const phrases = [
        "Full Stack Developer",
        "Web App Developer",
        "Mobile App Developer",
        "Tech Innovator",
        "Tech Entrepreneur",
        "Django Backend Architect"
    ];
    
    const textElement = document.querySelector('.typewriter-text');
    if (!textElement) return;
    
    // Simple fade transition between phrases
    textElement.innerHTML = '<div class="simple-animation-text"></div>';
    const container = textElement.querySelector('.simple-animation-text');
    container.textContent = phrases[0];
    
    let currentIndex = 0;
    
    function animateText() {
        currentIndex = (currentIndex + 1) % phrases.length;
        
        // Fade out
        gsap.to(container, {
            opacity: 0,
            duration: 0.7,
            onComplete: () => {
                // Change text and fade in
                container.textContent = phrases[currentIndex];
                gsap.to(container, {
                    opacity: 1,
                    duration: 0.7
                });
            }
        });
    }
    
    // Start animation cycle
    setInterval(animateText, 3000);
}

/**
 * Initialize general animations
 */
function initAnimations() {
    // Fade-in on scroll
    const fadeEls = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.2 });
    
    fadeEls.forEach(el => observer.observe(el));
    
    // Animate skill bars if present on page
    animateSkillBars();
}

/**
 * Animate skill bars on scroll
 */
function animateSkillBars() {
    const skillBars = document.querySelectorAll('.skill-progress');
    if (skillBars.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const percentage = progressBar.getAttribute('data-percentage');
                progressBar.style.width = percentage + '%';
                progressBar.classList.add('animate');
            }
        });
    }, { threshold: 0.2 });
    
    skillBars.forEach(bar => observer.observe(bar));
}