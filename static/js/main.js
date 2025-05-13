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
        
        // Load theme system
        await loadScript('/static/js/themes/theme-manager.js');
        await loadScript('/static/js/themes/galaxy.js');
        console.log('Theme system loaded');
        
        // Initialize theme manager
        if (window.themeManager) {
            window.themeManager.init();
        }
        
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
    // Typewriter effect
    typeWriterEffect();
    
    // Initialize animations that are independent of themes
    initAnimations();
}

/**
 * Typewriter effect for hero section
 */
function typeWriterEffect() {
    const phrases = [
        "Full Stack Developer",
        "UI/UX Designer",
        "Blockchain Explorer",
        "Creative Technologist"
    ];
    
    let currentPhraseIndex = 0;
    let currentCharIndex = 0;
    let isDeleting = false;
    let typingSpeed = 100;
    
    const textElement = document.querySelector('.typewriter-text');
    if (!textElement) return;
    
    function type() {
        const currentPhrase = phrases[currentPhraseIndex];
        
        if (isDeleting) {
            // Deleting text
            textElement.textContent = currentPhrase.substring(0, currentCharIndex - 1);
            currentCharIndex--;
            typingSpeed = 50;
        } else {
            // Typing text
            textElement.textContent = currentPhrase.substring(0, currentCharIndex + 1);
            currentCharIndex++;
            typingSpeed = 150;
        }
        
        // Switch between typing and deleting
        if (!isDeleting && currentCharIndex === currentPhrase.length) {
            // Wait at the end of typing
            isDeleting = true;
            typingSpeed = 1500;
        } else if (isDeleting && currentCharIndex === 0) {
            // Move to next phrase after deleting
            isDeleting = false;
            currentPhraseIndex = (currentPhraseIndex + 1) % phrases.length;
            typingSpeed = 500;
        }
        
        setTimeout(type, typingSpeed);
    }
    
    // Start the typing effect
    type();
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