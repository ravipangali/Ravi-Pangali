# Portfolio Website

A modern, responsive portfolio website with interactive themes and animations.

## Project Structure

The project has been organized with a clean separation of concerns:

```
static/
  ├── css/
  │   ├── style.css           # Main stylesheet with global styles
  │   ├── components/         # Component-specific styles
  │   │   └── header.css      # Header component styles
  │   └── themes/             # Theme-specific styles
  │       └── galaxy.css      # Galaxy theme styles
  ├── js/
  │   ├── main.js             # Main entry point JavaScript
  │   ├── base.js             # Common utilities and functions
  │   ├── components/         # Component-specific JavaScript
  │   │   └── header.js       # Header functionality
  │   └── themes/             # Theme-specific JavaScript
  │       ├── theme-manager.js # Theme management system
  │       └── galaxy.js       # Galaxy theme implementation
templates/
  ├── home.html               # Main page template
  └── base/                   # Base templates
      ├── base.html           # Base template with common structure
      ├── header.html         # Header component
      └── footer.html         # Footer component
```

## Features

- **Modular Code Organization**: Clean separation of CSS and JavaScript files
- **Theme System**: Extensible theme system with theme-manager
- **Galaxy Theme**: Interactive 3D background with Three.js
- **Responsive Design**: Mobile-friendly layouts
- **Interactive Elements**: Animations, typewriter effects, and more

## Theme System

The portfolio includes a theme management system that allows for easy switching between different visual themes.

### How It Works

1. The `ThemeManager` class in `static/js/themes/theme-manager.js` handles theme registration and switching
2. Each theme is implemented as a module in the `static/js/themes/` directory
3. Theme-specific CSS is stored in the `static/css/themes/` directory
4. Themes can be switched using the theme selector in the header

### Adding a New Theme

To add a new theme:

1. Create a new CSS file in `static/css/themes/` (e.g., `my-theme.css`)
2. Create a new JavaScript file in `static/js/themes/` (e.g., `my-theme.js`)
3. Register the theme in `theme-manager.js` by adding it to the `themes` object
4. Add a UI selector for the theme in the header

## Galaxy Theme Implementation

The Galaxy theme includes:

- Interactive 3D background with Three.js
- Animated particles and blockchain nodes
- Floating code snippets
- Star explosions and animations
- Reactive elements that respond to user interactions

## Development

To set up the development environment:

1. Clone the repository
2. Install dependencies (if any)
3. Run a local web server
4. Open the website in your browser

## Credits

This project uses the following libraries:

- [Three.js](https://threejs.org/) - For 3D rendering
- [GSAP](https://greensock.com/gsap/) - For animations
- [Tailwind CSS](https://tailwindcss.com/) - For styling 