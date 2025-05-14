if(window.themeManager){
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
            this.isLoading = true;
            
            // Ensure body has loading class when page starts loading
            document.body.classList.add('loading');
            
            if(document.readyState === 'loading') {
                console.log('DOM still loading, adding event listener');
                document.addEventListener('DOMContentLoaded', () => this.initialize());
            } else {
                console.log('DOM already loaded, initializing immediately');
                this.initialize();
            }
        }
        
        initialize() {
            console.log('Initializing theme manager');
            // Keep the loader visible during theme initialization
            this.showLoader();
            this.initFloatingThemeSwitcher();
            
            // Set theme and hide loader after theme is loaded
            this.setTheme(this.currentTheme)
                .then(() => {
                    console.log(`ThemeManager initialized with theme: ${this.currentTheme}`);
                    // Hide loader only after theme is fully loaded
                    setTimeout(() => {
                        this.hideLoader();
                        const container = document.getElementById('theme-float-container');
                        if (container) {
                            container.classList.add('show');
                        }
                    }, 1800); // Give additional time for theme to render properly
                });
        }

        // Method to show the loader
        showLoader() {
            const loader = document.getElementById('loader-container');
            if (loader) {
                loader.style.display = 'flex';
                loader.style.opacity = '1';
                loader.style.visibility = 'visible';
            }
            // Add loading class to body to hide content
            document.body.classList.add('loading');
            this.isLoading = true;
        }

        // Method to hide the loader
        hideLoader() {
            const loader = document.getElementById('loader-container');
            if (loader) {
                loader.style.opacity = '0';
                
                setTimeout(() => {
                    loader.style.visibility = 'hidden';
                    // Remove loading class to show content
                    document.body.classList.remove('loading');
                }, 800);
            }
            this.isLoading = false;
        }

        initFloatingThemeSwitcher() {
            console.log('initFloatingThemeSwitcher');
            const toggleBtn = document.getElementById('theme-float-toggle');
            const dropdown = document.getElementById('theme-float-dropdown');
            const options = document.querySelectorAll('.theme-float-option');
            
            console.log('Theme elements:', {toggleBtn, dropdown, options});
            
            if(toggleBtn && dropdown) {
                options.forEach(option => {
                    if(option.dataset.theme === this.currentTheme) {
                        option.classList.add('active');
                    }
                });
                
                toggleBtn.addEventListener('click', (e) => {
                    console.log('Theme toggle clicked');
                    e.preventDefault();
                    e.stopPropagation();
                    
                    if(dropdown.classList.contains('show')) {
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
                    
                    toggleBtn.classList.add('animate-pulse');
                    setTimeout(() => toggleBtn.classList.remove('animate-pulse'), 500);
                    console.log('Theme toggle clicked, dropdown visibility:', dropdown.classList.contains('show'));
                });
                
                document.addEventListener('click', (e) => {
                    if(!dropdown.contains(e.target) && !toggleBtn.contains(e.target)) {
                        dropdown.classList.remove('show');
                        dropdown.style.opacity = '0';
                        dropdown.style.visibility = 'hidden';
                        dropdown.style.pointerEvents = 'none';
                    }
                });
                
                options.forEach(option => {
                    option.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        const theme = option.dataset.theme;
                        console.log('Theme option clicked:', theme);
                        options.forEach(opt => opt.classList.remove('active'));
                        option.classList.add('active');
                        
                        // Show loader before changing theme
                        this.showLoader();
                        
                        // Set the theme and reload after it's fully loaded
                        this.setTheme(theme)
                            .then(() => {
                                localStorage.setItem('portfolio-theme', theme);
                                dropdown.classList.remove('show');
                                console.log(`Theme switched to: ${theme}`);
                                window.location.reload();
                            });
                    });
                });
            } else {
                console.warn('Theme toggle button or dropdown not found:', {toggleBtn, dropdown});
            }
        }

        // Make setTheme async to handle loading state properly
        async setTheme(theme) {
            document.body.classList.remove('theme-galaxy', 'theme-ocean', 'theme-none');
            
            // Disable all themes first
            for (const [themeName, themeObj] of Object.entries(this.themes)) {
                if (themeObj && typeof themeObj.disable === 'function') {
                    themeObj.disable();
                }
            }
            
            // Enable the selected theme
            if (this.themes[theme]) {
                document.body.classList.add(`theme-${theme}`);
                if (typeof this.themes[theme].enable === 'function') {
                    // Wait for theme to be enabled if it returns a promise
                    try {
                        const result = this.themes[theme].enable();
                        if (result instanceof Promise) {
                            await result;
                        }
                    } catch (error) {
                        console.error('Error enabling theme:', error);
                    }
                }
            }
            
            this.currentTheme = theme;
            return Promise.resolve(); // Resolve the promise when theme is set
        }

        getGalaxyTheme() {
            return {
                enable: () => {
                    return new Promise((resolve) => {
                        const galaxyBackground = document.getElementById('galaxy-background');
                        if (galaxyBackground) {
                            galaxyBackground.style.display = 'block';
                        }
                        if (window.initGalaxyScene && typeof window.initGalaxyScene === 'function') {
                            window.initGalaxyScene();
                            // Give time for the scene to initialize
                            setTimeout(resolve, 500);
                        } else {
                            console.warn('Galaxy scene initialization function not found');
                            resolve();
                        }
                    });
                },
                disable: () => {
                    const galaxyBackground = document.getElementById('galaxy-background');
                    if (galaxyBackground) {
                        galaxyBackground.style.display = 'none';
                    }
                    if (window.stopGalaxyAnimation && typeof window.stopGalaxyAnimation === 'function') {
                        window.stopGalaxyAnimation();
                    }
                }
            };
        }

        getOceanTheme() {
            return {
                enable: () => {
                    // Return a promise for the ocean theme loading
                    return new Promise((resolve) => {
                        if (!document.getElementById('ocean-css')) {
                            const link = document.createElement('link');
                            link.id = 'ocean-css';
                            link.rel = 'stylesheet';
                            link.href = '/static/css/themes/ocean.css';
                            document.head.appendChild(link);
                        }
                        
                        if (!window.initOceanScene) {
                            const script = document.createElement('script');
                            script.src = '/static/js/themes/ocean.js';
                            script.onload = () => {
                                if (window.initOceanScene) {
                                    window.initOceanScene();
                                    // Give time for the scene to initialize
                                    setTimeout(resolve, 500);
                                } else {
                                    resolve();
                                }
                            };
                            document.body.appendChild(script);
                        } else {
                            window.initOceanScene();
                            // Give time for the scene to initialize
                            setTimeout(resolve, 500);
                        }
                    });
                },
                disable: () => {
                    if (window.stopOceanScene) window.stopOceanScene();
                    const link = document.getElementById('ocean-css');
                    if (link) link.remove();
                }
            };
        }

        getNoThemeOption() {
            return {
                enable: () => {
                    return new Promise((resolve) => {
                        const galaxyBackground = document.getElementById('galaxy-background');
                        if (galaxyBackground) {
                            galaxyBackground.style.display = 'none';
                        }
                        setTimeout(resolve, 300);
                    });
                },
                disable: () => {}
            };
        }
    }

    window.themeManager = new ThemeManager();
    console.log('ThemeManager initialized:', window.themeManager.currentTheme);
}

window.getGalaxyTheme = () => window.themeManager.getGalaxyTheme();