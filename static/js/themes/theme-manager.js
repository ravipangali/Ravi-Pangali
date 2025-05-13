/**
 * Theme Manager
 * Handles theme loading, switching, and persistence
 */

// Prevent duplicate initialization
if (window.themeManager) {
    console.log('ThemeManager already initialized');
} else {
    class ThemeManager {
        constructor() {
            console.log('ThemeManager constructor');
            this.currentTheme = localStorage.getItem('portfolio-theme') || 'galaxy';
            this.themes = {
                'galaxy': this.getGalaxyTheme(),
                'ocean': this.getOceanTheme(),
                'none': this.getNoThemeOption()
            };
            
            // Initialize immediately if DOM is already loaded
            if (document.readyState === 'loading') {
                console.log('DOM still loading, adding event listener');
                document.addEventListener('DOMContentLoaded', () => this.initialize());
            } else {
                console.log('DOM already loaded, initializing immediately');
                this.initialize();
            }
        }
        
        /**
         * Initialize the theme manager
         */
        initialize() {
            console.log('Initializing theme manager');
            this.initFloatingThemeSwitcher();
            this.setTheme(this.currentTheme);
            console.log(`ThemeManager initialized with theme: ${this.currentTheme}`);
            
            // Show theme button after a delay
            setTimeout(() => {
                const container = document.getElementById('theme-float-container');
                if (container) {
                    container.classList.add('show');
                }
            }, 2000); // Show after 2 seconds
        }
        
        /**
         * Initialize floating theme switcher
         */
        initFloatingThemeSwitcher() {
            console.log('initFloatingThemeSwitcher');
            
            const toggleBtn = document.getElementById('theme-float-toggle');
            const dropdown = document.getElementById('theme-float-dropdown');
            const options = document.querySelectorAll('.theme-float-option');
            
            console.log('Theme elements:', { toggleBtn, dropdown, options });
            
            if (toggleBtn && dropdown) {
                // Set initial active state
                options.forEach(option => {
                    if (option.dataset.theme === this.currentTheme) {
                        option.classList.add('active');
                    }
                });
                
                // Toggle dropdown visibility
                toggleBtn.addEventListener('click', (e) => {
                    console.log('Theme toggle clicked');
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Toggle dropdown
                    if (dropdown.classList.contains('show')) {
                        dropdown.classList.remove('show');
                        dropdown.style.opacity = '0';
                        dropdown.style.visibility = 'hidden';
                        dropdown.style.pointerEvents = 'none';
                    } else {
                        dropdown.classList.add('show');
                        dropdown.style.opacity = '1';
                        dropdown.style.visibility = 'visible';
                        dropdown.style.pointerEvents = 'auto';
                    }
                    
                    // Add animation pulse to button when clicked
                    toggleBtn.classList.add('animate-pulse');
                    setTimeout(() => toggleBtn.classList.remove('animate-pulse'), 500);
                    
                    console.log('Theme toggle clicked, dropdown visibility:', dropdown.classList.contains('show'));
                });
                
                // Close when clicking outside
                document.addEventListener('click', (e) => {
                    if (!dropdown.contains(e.target) && !toggleBtn.contains(e.target)) {
                        dropdown.classList.remove('show');
                        dropdown.style.opacity = '0';
                        dropdown.style.visibility = 'hidden';
                        dropdown.style.pointerEvents = 'none';
                    }
                });
                
                // Theme option selection
                options.forEach(option => {
                    option.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const theme = option.dataset.theme;
                        console.log('Theme option clicked:', theme);
                        
                        // Update active state
                        options.forEach(opt => opt.classList.remove('active'));
                        option.classList.add('active');
                        
                        // Set theme
                        this.setTheme(theme);
                        localStorage.setItem('portfolio-theme', theme);
                        
                        // Close dropdown
                        dropdown.classList.remove('show');
                        
                        console.log(`Theme switched to: ${theme}`);
                        
                        // Refresh the page after a short delay to apply the new theme
                        setTimeout(() => {
                            window.location.reload();
                        }, 300);
                    });
                });
            } else {
                console.warn('Theme toggle button or dropdown not found:', { toggleBtn, dropdown });
            }
        }
        
        /**
         * Set active theme
         * @param {string} theme - Theme identifier
         */
        setTheme(theme) {
            // Remove all theme classes
            document.body.classList.remove('theme-galaxy', 'theme-ocean', 'theme-none');
            
            // Disable all themes first
            Object.values(this.themes).forEach(theme => {
                if (theme && typeof theme.disable === 'function') {
                    theme.disable();
                }
            });
            
            // Add selected theme class and enable it
            if (this.themes[theme]) {
                document.body.classList.add(`theme-${theme}`);
                if (typeof this.themes[theme].enable === 'function') {
                    this.themes[theme].enable();
                }
            }
            
            this.currentTheme = theme;
        }
        
        /**
         * Get Galaxy theme object
         * @returns {Object} Galaxy theme controller
         */
        getGalaxyTheme() {
            return {
                enable: () => {
                    // Show galaxy container
                    const galaxyBackground = document.getElementById('galaxy-background');
                    if (galaxyBackground) {
                        galaxyBackground.style.display = 'block';
                    }
                    
                    // Initialize Three.js scene
                    if (window.initGalaxyScene && typeof window.initGalaxyScene === 'function') {
                        window.initGalaxyScene();
                    } else {
                        console.warn('Galaxy scene initialization function not found');
                    }
                },
                
                disable: () => {
                    // Hide galaxy container
                    const galaxyBackground = document.getElementById('galaxy-background');
                    if (galaxyBackground) {
                        galaxyBackground.style.display = 'none';
                    }
                    
                    // Stop Three.js animations
                    if (window.stopGalaxyAnimation && typeof window.stopGalaxyAnimation === 'function') {
                        window.stopGalaxyAnimation();
                    }
                }
            };
        }
        
        /**
         * Get Ocean theme object
         * @returns {Object} Ocean theme controller
         */
        getOceanTheme() {
            return {
                enable: () => {
                    // Load ocean.css if not already loaded
                    if (!document.getElementById('ocean-css')) {
                        const link = document.createElement('link');
                        link.id = 'ocean-css';
                        link.rel = 'stylesheet';
                        link.href = '/static/css/themes/ocean.css';
                        document.head.appendChild(link);
                    }
                    // Load ocean.js if not already loaded
                    if (!window.initOceanScene) {
                        const script = document.createElement('script');
                        script.src = '/static/js/themes/ocean.js';
                        script.onload = () => {
                            if (window.initOceanScene) window.initOceanScene();
                        };
                        document.body.appendChild(script);
                    } else {
                        window.initOceanScene();
                    }
                },
                disable: () => {
                    if (window.stopOceanScene) window.stopOceanScene();
                    // Optionally remove ocean.css
                    const link = document.getElementById('ocean-css');
                    if (link) link.remove();
                }
            };
        }
        
        /**
         * Get "No Theme" option
         * @returns {Object} No theme controller
         */
        getNoThemeOption() {
            return {
                enable: () => {
                    // Hide all theme-specific elements
                    const galaxyBackground = document.getElementById('galaxy-background');
                    if (galaxyBackground) {
                        galaxyBackground.style.display = 'none';
                    }
                },
                
                disable: () => {
                    // Nothing to do when disabling the "no theme" option
                }
            };
        }
    }

    // Initialize the ThemeManager and make it globally available
    window.themeManager = new ThemeManager();
    console.log('ThemeManager initialized:', window.themeManager.currentTheme);
}

// For backwards compatibility with existing code
window.getGalaxyTheme = () => window.themeManager.getGalaxyTheme(); 