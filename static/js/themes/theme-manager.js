/**
 * Theme Manager
 * Handles theme loading, switching, and persistence
 */

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('portfolio-theme') || 'galaxy';
        this.themes = {
            'galaxy': this.getGalaxyTheme(),
            'none': this.getNoThemeOption()
        };
        this.isInitialized = false;
    }
    
    /**
     * Initialize the theme manager
     */
    init() {
        if (this.isInitialized) return;
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeTheme());
        } else {
            this.initializeTheme();
        }
        
        this.isInitialized = true;
    }
    
    /**
     * Initialize theme functionality
     */
    initializeTheme() {
        this.initFloatingThemeSwitcher();
        this.setTheme(this.currentTheme);
        console.log(`ThemeManager initialized with theme: ${this.currentTheme}`);
    }
    
    /**
     * Initialize floating theme switcher
     */
    initFloatingThemeSwitcher() {
        const toggleBtn = document.getElementById('theme-float-toggle');
        const dropdown = document.getElementById('theme-float-dropdown');
        const options = document.querySelectorAll('.theme-float-option');
        
        if (!toggleBtn || !dropdown) {
            console.error('Theme switcher elements not found');
            return;
        }
        
        // Set initial active state
        options.forEach(option => {
            if (option.dataset.theme === this.currentTheme) {
                option.classList.add('active');
            }
        });
        
        // Toggle dropdown visibility
        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropdown.classList.toggle('show');
            
            // Add animation pulse to button when clicked
            toggleBtn.classList.add('animate-pulse');
            setTimeout(() => toggleBtn.classList.remove('animate-pulse'), 500);
        });
        
        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && !toggleBtn.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
        
        // Theme option selection
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const theme = option.dataset.theme;
                this.setTheme(theme);
                localStorage.setItem('portfolio-theme', theme);
                console.log(`Theme switched to: ${theme} (from floating menu)`);
                
                // Update active state and close dropdown
                options.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                dropdown.classList.remove('show');
            });
        });
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

// For backwards compatibility with existing code
window.getGalaxyTheme = () => window.themeManager.getGalaxyTheme(); 