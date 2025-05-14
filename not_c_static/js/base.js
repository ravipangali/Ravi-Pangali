/**
 * Base JavaScript
 * Common functionality used across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Base script loaded');
    
    // Initialize fade-in animation observer
    initFadeInObserver();
});

/**
 * Initialize IntersectionObserver for fade-in animations
 */
function initFadeInObserver() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    if (fadeElements.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.2 });
    
    fadeElements.forEach(el => observer.observe(el));
}

/**
 * Smooth scroll to element
 * @param {string} elementId - Target element ID
 * @param {number} offset - Scroll offset in pixels
 */
function smoothScrollTo(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    
    if (element) {
        const targetPosition = element.getBoundingClientRect().top + window.scrollY - offset;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Open external link in new tab
 * @param {string} url - URL to open
 * @param {boolean} noFollow - Whether to add nofollow attribute
 */
function openExternalLink(url, noFollow = true) {
    if (!url) return;
    
    const newWindow = window.open(url, '_blank');
    
    if (noFollow) {
        newWindow.rel = 'noopener noreferrer';
    }
    
    newWindow.focus();
}

/**
 * Detect mobile device
 * @returns {boolean} True if mobile device
 */
function isMobileDevice() {
    return (window.innerWidth <= 768) || 
           (navigator.userAgent.match(/Android/i) ||
            navigator.userAgent.match(/webOS/i) ||
            navigator.userAgent.match(/iPhone/i) ||
            navigator.userAgent.match(/iPad/i) ||
            navigator.userAgent.match(/iPod/i) ||
            navigator.userAgent.match(/BlackBerry/i) ||
            navigator.userAgent.match(/Windows Phone/i));
} 