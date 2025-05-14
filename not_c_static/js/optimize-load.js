// Optimize resource loading
document.addEventListener('DOMContentLoaded', () => {
    // Lazy load images
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    if (src) {
                        img.setAttribute('src', src);
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Defer non-critical JavaScript
    setTimeout(() => {
        // Load non-critical scripts after initial page load
        const nonCriticalScripts = [
            // Add paths to non-critical scripts
            '/static/js/themes/ocean.js',
            // Add more scripts as needed
        ];

        nonCriticalScripts.forEach(scriptPath => {
            const script = document.createElement('script');
            script.src = scriptPath;
            script.defer = true;
            document.body.appendChild(script);
        });
    }, 2000); // 2-second delay
    
    // Initialize galaxy background if in viewport
    const initializeGalaxy = () => {
        // Check if galaxy element exists in DOM
        const galaxyElement = document.getElementById('galaxy-canvas');
        if (galaxyElement && typeof initGalaxyBackground === 'function') {
            initGalaxyBackground();
        }
    };
    
    // Initialize after a small delay to ensure faster initial load
    setTimeout(initializeGalaxy, 500);
}); 