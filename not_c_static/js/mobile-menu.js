/**
 * Mobile Menu Functionality
 * This script handles the mobile menu toggle and behavior
 */

// Wait for DOM to fully load before initializing
console.log('Mobile menu script starting...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing mobile menu');
    
    // Elements
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    // Debug output of elements
    console.log('Mobile menu button:', mobileMenuButton);
    console.log('Mobile menu:', mobileMenu);
    
    if (!mobileMenuButton || !mobileMenu) {
        console.error('Mobile menu elements not found');
        // List all buttons in the document to help debug
        const allButtons = document.querySelectorAll('button');
        console.log('All buttons in document:', allButtons.length);
        allButtons.forEach((btn, i) => console.log(`Button ${i}:`, btn.id, btn));
        return;
    }
    
    console.log('Mobile menu elements found and initialized');
    
    // Mobile menu toggle
    mobileMenuButton.addEventListener('click', function(event) {
        console.log('Mobile menu button clicked');
        event.stopPropagation(); // Prevent event from bubbling up
        
        // Toggle the show class
        mobileMenu.classList.toggle('show');
        
        // Debug after toggle
        console.log('Mobile menu classes after toggle:', mobileMenu.className);
        console.log('Mobile menu is visible:', mobileMenu.classList.contains('show'));
        
        // Toggle aria-expanded attribute for accessibility
        const isExpanded = mobileMenu.classList.contains('show');
        mobileMenuButton.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
        mobileMenu.setAttribute('aria-hidden', isExpanded ? 'false' : 'true');
        
        console.log('Mobile menu state updated:', isExpanded ? 'open' : 'closed');
    });
    
    // Close mobile menu when clicking a link
    document.querySelectorAll('.mobile-link').forEach(link => {
        link.addEventListener('click', function() {
            console.log('Mobile menu link clicked');
            mobileMenu.classList.remove('show');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            mobileMenu.setAttribute('aria-hidden', 'true');
        });
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu.classList.contains('show') && 
            !mobileMenu.contains(event.target) && 
            !mobileMenuButton.contains(event.target)) {
            
            console.log('Clicked outside mobile menu');
            mobileMenu.classList.remove('show');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            mobileMenu.setAttribute('aria-hidden', 'true');
        }
    });
    
    // Initialize state
    mobileMenuButton.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
    console.log('Mobile menu fully initialized');
}); 