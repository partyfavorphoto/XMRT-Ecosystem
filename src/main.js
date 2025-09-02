// XMRT DAO Hub - Vite Static Build JavaScript
// Mobile-first responsive functionality

// Global state
let currentSection = 'overview';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    handleUrlHash();
});

// Initialize application
function initializeApp() {
    console.log('🚀 XMRT DAO Hub - Vite Build Initialized');
    updateConnectionStatus();
    showSection('overview');
}

// Setup event listeners
function setupEventListeners() {
    // Handle window resize for responsive behavior
    window.addEventListener('resize', handleResize);
    
    // Handle orientation change on mobile
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            closeMobileNav();
        }, 100);
    });

    // Handle hash changes for direct navigation
    window.addEventListener('hashchange', handleUrlHash);

    // Add touch event listeners for better mobile experience
    setupTouchSupport();
}

// Mobile Navigation Functions
window.toggleMobileNav = function() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

window.closeMobileNav = function() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.remove('active');
}

// Section Navigation Functions
window.showSection = function(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show the selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionName;
        
        // Update URL hash without triggering scroll
        history.replaceState(null, null, '#' + sectionName);
        
        // Update navigation highlight
        updateNavHighlight(sectionName);
        
        // Close mobile nav if open
        closeMobileNav();
        
        console.log(`📍 Switched to section: ${sectionName}`);
    }
}

function updateNavHighlight(activeSection) {
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.classList.remove('active');
        // Check if link text includes the section name
        if (link.textContent.toLowerCase().includes(activeSection.toLowerCase()) ||
            (activeSection === 'overview' && link.textContent.includes('Overview'))) {
            link.classList.add('active');
        }
    });
}

// Handle URL hash changes for direct navigation
function handleUrlHash() {
    const hash = window.location.hash.substr(1);
    if (hash && ['overview', 'chat', 'agents', 'mcp', 'utilities', 'api'].includes(hash)) {
        showSection(hash);
    } else {
        showSection('overview');
    }
}

// Handle window resize
function handleResize() {
    // Close mobile nav if window becomes larger
    if (window.innerWidth >= 768) {
        closeMobileNav();
    }
}

// Enhanced Touch Support
function setupTouchSupport() {
    // Prevent zoom on double tap for buttons
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function (event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);

    // Add touch feedback for interactive elements
    const interactiveElements = document.querySelectorAll('.action-btn, .feature-card, .status-item');
    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        }, { passive: true });
        
        element.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.opacity = '1';
            }, 150);
        }, { passive: true });
    });
}

// Update connection status
function updateConnectionStatus() {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.textContent = 'Vite Static Build';
        statusElement.style.background = 'var(--success-color)';
    }
}

// Demo functionality for static build
window.demoAlert = function(message) {
    alert(`Demo Mode: ${message}\n\nThis is a static Vite build. For full functionality, visit the Render deployment with Flask backend.`);
}

// Simulate loading states for demo
function simulateLoading(elementId, duration = 2000) {
    const element = document.getElementById(elementId);
    if (element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<div class="loading"></div><p style="text-align: center; margin-top: 10px;">Loading...</p>';
        
        setTimeout(() => {
            element.innerHTML = originalContent;
        }, duration);
    }
}

// Feature demonstrations
window.showFeatureDemo = function(featureName) {
    const messages = {
        'mobile': 'This design is mobile-first and responsive! Try resizing your browser or viewing on different devices.',
        'navigation': 'All navigation tabs are functional and provide smooth section switching with URL support.',
        'design': 'The UI uses modern CSS with gradients, animations, and touch-friendly interactions.',
        'architecture': 'Dual deployment: Static Vite build (Vercel) + Dynamic Flask app (Render) for best of both worlds.'
    };
    
    demoAlert(messages[featureName] || 'Feature demonstration available in full Flask deployment.');
}

// Console logging for debugging
console.log('📱 Mobile-first responsive design loaded');
console.log('⚡ Vite build environment detected');
console.log('🎯 All navigation features initialized');

// Export functions for global access
export { showSection, toggleMobileNav, closeMobileNav, demoAlert, showFeatureDemo };