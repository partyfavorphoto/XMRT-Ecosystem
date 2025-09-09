/**
 * XMRT-Ecosystem Enhanced Frontend Integration
 * Fixed JavaScript for button functionality and WebSocket connections
 */

class XMRTSystemManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.autonomousState = {
            learning_active: false,
            coordination_active: false,
            memory_active: false,
            agents_active: false
        };
        this.connectionAttempts = 0;
        this.maxRetries = 5;
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.setupEventHandlers();
        this.updateUI();
        
        // Auto-reconnect on page visibility change
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isConnected) {
                this.connectWebSocket();
            }
        });
    }
    
    connectWebSocket() {
        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['polling', 'websocket'],
                upgrade: true,
                rememberUpgrade: true,
                timeout: 20000,
                forceNew: true
            });
            
            this.setupSocketHandlers();
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.handleConnectionError();
        }
    }
    
    setupSocketHandlers() {
        // Connection handlers
        this.socket.on('connect', () => {
            console.log('✅ Connected to XMRT-Ecosystem');
            this.isConnected = true;
            this.connectionAttempts = 0;
            this.updateConnectionStatus(true);
            this.requestSystemStatus();
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from XMRT-Ecosystem');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.handleConnectionError();
        });
        
        // System event handlers
        this.socket.on('connection_response', (data) => {
            console.log('Connection response:', data);
            if (data.autonomous_state) {
                this.autonomousState = data.autonomous_state;
                this.updateUI();
            }
        });
        
        this.socket.on('agents_activated', (data) => {
            console.log('Agents activated:', data);
            this.autonomousState.agents_active = true;
            this.updateUI();
            this.showNotification('Autonomous agents activated successfully!', 'success');
        });
        
        this.socket.on('learning_started', (data) => {
            console.log('Learning started:', data);
            this.autonomousState.learning_active = true;
            this.updateUI();
            this.showNotification('Learning system activated!', 'success');
        });
        
        this.socket.on('coordination_activated', (data) => {
            console.log('Coordination activated:', data);
            this.autonomousState.coordination_active = true;
            this.updateUI();
            this.showNotification('Coordination system activated!', 'success');
        });
        
        this.socket.on('memory_activated', (data) => {
            console.log('Memory activated:', data);
            this.autonomousState.memory_active = true;
            this.updateUI();
            this.showNotification('Long-term memory system activated!', 'success');
        });
        
        this.socket.on('system_update', (data) => {
            if (data.autonomous_state) {
                this.autonomousState = data.autonomous_state;
                this.updateUI();
            }
        });
        
        this.socket.on('learning_update', (data) => {
            this.updateLearningDisplay(data);
        });
        
        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.showNotification('System error: ' + error.message, 'error');
        });
    }
    
    setupEventHandlers() {
        // Button event handlers with improved error handling
        const buttons = {
            'activate-agents-btn': () => this.activateAgents(),
            'start-learning-btn': () => this.startLearning(),
            'activate-coordination-btn': () => this.activateCoordination(),
            'activate-memory-btn': () => this.activateMemory(),
            'system-status-btn': () => this.requestSystemStatus(),
            'activate-all-btn': () => this.activateAllSystems()
        };
        
        Object.entries(buttons).forEach(([buttonId, handler]) => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.handleButtonClick(button, handler);
                });
            }
        });
        
        // Auto-refresh status every 30 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.requestSystemStatus();
            }
        }, 30000);
    }
    
    handleButtonClick(button, handler) {
        if (!this.isConnected) {
            this.showNotification('Not connected to system. Attempting to reconnect...', 'warning');
            this.connectWebSocket();
            return;
        }
        
        // Disable button during operation
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = 'Processing...';
        
        try {
            handler();
        } catch (error) {
            console.error('Button handler error:', error);
            this.showNotification('Operation failed: ' + error.message, 'error');
        } finally {
            // Re-enable button after 2 seconds
            setTimeout(() => {
                button.disabled = false;
                button.textContent = originalText;
            }, 2000);
        }
    }
    
    // API Methods with proper error handling
    async activateAgents() {
        try {
            const response = await fetch('/api/agents/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ timestamp: new Date().toISOString() })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.autonomousState.agents_active = true;
                this.updateUI();
                this.showNotification('Autonomous agents activated!', 'success');
            } else {
                throw new Error(data.error || 'Failed to activate agents');
            }
            
        } catch (error) {
            console.error('Agent activation error:', error);
            this.showNotification('Failed to activate agents: ' + error.message, 'error');
        }
    }
    
    async startLearning() {
        try {
            const response = await fetch('/api/learning/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ timestamp: new Date().toISOString() })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.autonomousState.learning_active = true;
                this.updateUI();
                this.showNotification('Learning system started!', 'success');
            } else {
                throw new Error(data.error || 'Failed to start learning');
            }
            
        } catch (error) {
            console.error('Learning activation error:', error);
            this.showNotification('Failed to start learning: ' + error.message, 'error');
        }
    }
    
    async activateCoordination() {
        try {
            const response = await fetch('/api/coordination/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ timestamp: new Date().toISOString() })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.autonomousState.coordination_active = true;
                this.updateUI();
                this.showNotification('Coordination system activated!', 'success');
            } else {
                throw new Error(data.error || 'Failed to activate coordination');
            }
            
        } catch (error) {
            console.error('Coordination activation error:', error);
            this.showNotification('Failed to activate coordination: ' + error.message, 'error');
        }
    }
    
    async activateMemory() {
        try {
            const response = await fetch('/api/memory/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ timestamp: new Date().toISOString() })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.autonomousState.memory_active = true;
                this.updateUI();
                this.showNotification('Long-term memory activated!', 'success');
            } else {
                throw new Error(data.error || 'Failed to activate memory');
            }
            
        } catch (error) {
            console.error('Memory activation error:', error);
            this.showNotification('Failed to activate memory: ' + error.message, 'error');
        }
    }
    
    async activateAllSystems() {
        this.showNotification('Activating all systems...', 'info');
        
        try {
            await this.activateAgents();
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            await this.startLearning();
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            await this.activateCoordination();
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            await this.activateMemory();
            
            this.showNotification('All systems activated successfully!', 'success');
            
        } catch (error) {
            console.error('System activation error:', error);
            this.showNotification('Failed to activate all systems: ' + error.message, 'error');
        }
    }
    
    requestSystemStatus() {
        if (this.socket && this.isConnected) {
            this.socket.emit('request_status');
        }
    }
    
    // UI Update Methods
    updateUI() {
        this.updateSystemStatus();
        this.updateButtonStates();
        this.updateProgressIndicators();
    }
    
    updateSystemStatus() {
        const statusElements = {
            'agents-status': this.autonomousState.agents_active,
            'learning-status': this.autonomousState.learning_active,
            'coordination-status': this.autonomousState.coordination_active,
            'memory-status': this.autonomousState.memory_active
        };
        
        Object.entries(statusElements).forEach(([elementId, isActive]) => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = isActive ? '✅ Active' : '⏸️ Inactive';
                element.className = isActive ? 'status-active' : 'status-inactive';
            }
        });
        
        // Update overall system status
        const overallStatus = document.getElementById('overall-status');
        if (overallStatus) {
            const activeCount = Object.values(this.autonomousState).filter(Boolean).length;
            const totalCount = Object.keys(this.autonomousState).length;
            
            if (activeCount === totalCount) {
                overallStatus.textContent = '🟢 All Systems Operational';
                overallStatus.className = 'status-optimal';
            } else if (activeCount > 0) {
                overallStatus.textContent = `🟡 ${activeCount}/${totalCount} Systems Active`;
                overallStatus.className = 'status-partial';
            } else {
                overallStatus.textContent = '🔴 Systems Inactive';
                overallStatus.className = 'status-inactive';
            }
        }
    }
    
    updateButtonStates() {
        const buttonStates = {
            'activate-agents-btn': !this.autonomousState.agents_active,
            'start-learning-btn': !this.autonomousState.learning_active,
            'activate-coordination-btn': !this.autonomousState.coordination_active,
            'activate-memory-btn': !this.autonomousState.memory_active
        };
        
        Object.entries(buttonStates).forEach(([buttonId, shouldEnable]) => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.disabled = !shouldEnable || !this.isConnected;
                if (!shouldEnable) {
                    button.textContent = button.textContent.replace('Activate', 'Activated');
                }
            }
        });
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? '🟢 Connected' : '🔴 Disconnected';
            statusElement.className = connected ? 'connection-active' : 'connection-inactive';
        }
    }
    
    updateProgressIndicators() {
        // Update any progress bars or indicators
        const progressElements = document.querySelectorAll('.progress-indicator');
        progressElements.forEach(element => {
            const systemType = element.dataset.system;
            if (systemType && this.autonomousState[systemType + '_active']) {
                element.style.width = '100%';
                element.classList.add('progress-complete');
            }
        });
    }
    
    updateLearningDisplay(data) {
        const learningDisplay = document.getElementById('learning-display');
        if (learningDisplay && data.learning_point) {
            const learningInfo = document.createElement('div');
            learningInfo.className = 'learning-update';
            learningInfo.innerHTML = `
                <span class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</span>
                <span class="data-point">Learning point collected</span>
                <span class="total">Total: ${data.total_points}</span>
            `;
            
            learningDisplay.appendChild(learningInfo);
            
            // Keep only last 10 updates
            while (learningDisplay.children.length > 10) {
                learningDisplay.removeChild(learningDisplay.firstChild);
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // Add to page
        const container = document.getElementById('notifications') || document.body;
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
        
        // Close button handler
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            });
        }
        
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    handleConnectionError() {
        this.connectionAttempts++;
        
        if (this.connectionAttempts < this.maxRetries) {
            const retryDelay = Math.min(1000 * Math.pow(2, this.connectionAttempts), 30000);
            console.log(`Retrying connection in ${retryDelay}ms (attempt ${this.connectionAttempts}/${this.maxRetries})`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, retryDelay);
        } else {
            console.error('Max connection attempts reached');
            this.showNotification('Connection failed. Please refresh the page.', 'error');
        }
    }
}

// Initialize the system manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing XMRT-Ecosystem Frontend');
    window.xmrtSystem = new XMRTSystemManager();
});

// Export for global access
window.XMRTSystemManager = XMRTSystemManager;

