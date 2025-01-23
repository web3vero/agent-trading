// Moon Dev's RBI Agent Frontend 🌙

// Realistic timings (in milliseconds) based on actual processing times
const PHASE_TIMINGS = {
    research: 14000,  // Research agent takes ~10 seconds
    backtest: 17000,  // Backtest agent takes ~15 seconds
    debug: 12000      // Debug agent takes ~8 seconds
};

// Message display intervals
const MESSAGE_INTERVAL = {
    research: PHASE_TIMINGS.research / 5,  // Show 5 messages during research phase
    backtest: PHASE_TIMINGS.backtest / 5,  // Show 5 messages during backtest phase
    debug: PHASE_TIMINGS.debug / 5         // Show 5 messages during debug phase
};

const funMessages = [
    "🤖 AI Agents are cooking up some alpha...",
    "🌙 Moon Dev's agents are working their magic...",
    "🚀 Preparing for launch to the moon...",
    "💫 Discovering hidden patterns in the market...",
    "🎯 Optimizing strategy parameters...",
    "🔮 Predicting the future (just kidding)...",
    "🎨 Adding some artistic flair to the code...",
    "🎮 Playing 4D chess with the market...",
    "🌈 Finding the end of the rainbow...",
    "🎲 Rolling the perfect strategy..."
];

const researchMessages = [
    "📚 Reading through strategy documentation...",
    "🧮 Analyzing mathematical patterns...",
    "🔍 Identifying key trading signals...",
    "📊 Processing historical data...",
    "🎯 Defining entry and exit rules..."
];

const backtestMessages = [
    "⚙️ Setting up backtesting environment...",
    "📈 Implementing trading logic...",
    "💡 Adding risk management rules...",
    "🔧 Configuring position sizing...",
    "🎚️ Fine-tuning parameters..."
];

const debugMessages = [
    "🐛 Hunting for bugs...",
    "✨ Optimizing code performance...",
    "🔍 Reviewing edge cases...",
    "🧪 Running test scenarios...",
    "🎯 Finalizing implementation..."
];

function cycleMessages(element, messages) {
    let index = 0;
    return setInterval(() => {
        element.textContent = messages[index];
        element.classList.remove('fun-message');
        void element.offsetWidth; // Trigger reflow
        element.classList.add('fun-message');
        index = (index + 1) % messages.length;
    }, 4000);
}

function addProgressMessage(phaseElement, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'progress-message text-sm text-gray-400 mt-1 message-animation';
    messageDiv.textContent = message;
    phaseElement.querySelector('.progress-messages').appendChild(messageDiv);
}

function updatePhase(phaseElement, status = 'active') {
    const phases = document.querySelectorAll('.processing-phase');
    phases.forEach(p => p.classList.remove('active'));
    
    phaseElement.classList.add('active');
    if (status === 'complete') {
        phaseElement.classList.add('phase-complete');
    } else if (status === 'error') {
        phaseElement.classList.add('phase-error');
    }
}

async function processPhase(phaseElement, messages, timing) {
    updatePhase(phaseElement);
    const interval = timing / messages.length;
    
    // Clear previous messages
    const messagesContainer = phaseElement.querySelector('.progress-messages');
    messagesContainer.innerHTML = '';
    
    // Add each message with animation
    for (const message of messages) {
        await new Promise(r => setTimeout(r, interval));
        const messageDiv = document.createElement('div');
        messageDiv.className = 'progress-message text-sm text-purple-300 message-animation';
        messageDiv.innerHTML = `
            <span class="inline-block mr-2">→</span>
            ${message}
        `;
        messagesContainer.appendChild(messageDiv);
    }
    
    // Mark phase as complete
    updatePhase(phaseElement, 'complete');
}

// Function to add or update a result in the results section
function updateResult(result) {
    const resultId = `strategy-${result.strategy_number}`;
    let resultElement = document.getElementById(resultId);
    
    if (!resultElement) {
        resultElement = document.createElement('div');
        resultElement.id = resultId;
        resultElement.className = 'bg-gray-800 rounded-lg p-6 success-animation';
        resultsContent.appendChild(resultElement);
    }
    
    if (result.status === 'success') {
        resultElement.innerHTML = `
            <div class="mb-4">
                <h3 class="text-xl font-bold mb-2">📊 Strategy ${result.strategy_number}</h3>
                <p class="text-gray-400 mb-2">Source: ${result.link}</p>
            </div>
            
            <!-- Strategy Section -->
            <div class="mb-6">
                <h4 class="text-lg font-semibold mb-2">🎯 Strategy Analysis</h4>
                <div class="code-block">
                    <pre><code>${result.strategy}</code></pre>
                    <button class="copy-button" onclick="copyToClipboard(this)">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
            
            <!-- Backtest Section -->
            <div class="mb-6">
                <h4 class="text-lg font-semibold mb-2">📈 Backtest Implementation</h4>
                <div class="code-block">
                    <pre><code>${result.backtest}</code></pre>
                    <button class="copy-button" onclick="copyToClipboard(this)">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
            
            <!-- Download Links -->
            <div class="mt-4 flex space-x-4">
                <a href="/download/strategy/${result.strategy_file}" 
                   class="inline-flex items-center space-x-2 text-purple-400 hover:text-purple-300">
                    <i class="fas fa-download"></i>
                    <span>Download Strategy</span>
                </a>
                <a href="/download/backtest/${result.backtest_file}" 
                   class="inline-flex items-center space-x-2 text-purple-400 hover:text-purple-300">
                    <i class="fas fa-download"></i>
                    <span>Download Backtest</span>
                </a>
            </div>
        `;
    } else {
        resultElement.innerHTML = `
            <div class="text-red-500">
                <h3 class="text-xl font-bold mb-2">❌ Error Processing Strategy ${result.strategy_number}</h3>
                <p>${result.error}</p>
            </div>
        `;
        resultElement.classList.add('error-animation');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const submitButton = document.getElementById('submitButton');
    const resultsContent = document.getElementById('resultsContent');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const processingAnimation = document.getElementById('processingAnimation');
    let pollingInterval;

    async function pollForResults() {
        try {
            const response = await fetch('/results');
            const data = await response.json();
            
            console.log("🔍 Polling results:", data);
            
            if (data.status === 'success') {
                if (data.results && data.results.length > 0) {
                    resultsContent.innerHTML = ''; // Clear previous results
                    
                    data.results.forEach(result => {
                        const resultHtml = `
                            <div class="mb-8 p-4 bg-white rounded-lg shadow-md">
                                <h3 class="text-lg font-semibold mb-2">Strategy ${result.strategy_number} ${result.status === 'success' ? '✅' : '❌'}</h3>
                                ${result.status === 'success' ? `
                                    <div class="mb-4">
                                        <h4 class="font-medium mb-2">Strategy Analysis 📊</h4>
                                        <pre class="bg-gray-100 p-4 rounded overflow-x-auto">${result.strategy}</pre>
                                        <a href="/download/strategy/${result.strategy_file}" class="text-blue-500 hover:text-blue-700">Download Strategy</a>
                                    </div>
                                    <div>
                                        <h4 class="font-medium mb-2">Backtest Implementation 🔬</h4>
                                        <pre class="bg-gray-100 p-4 rounded overflow-x-auto">${result.backtest}</pre>
                                        <a href="/download/backtest/${result.backtest_file}" class="text-blue-500 hover:text-blue-700">Download Backtest</a>
                                    </div>
                                ` : `
                                    <div class="text-red-500">
                                        Error: ${result.message}
                                    </div>
                                `}
                            </div>
                        `;
                        resultsContent.innerHTML += resultHtml;
                    });
                }
                
                if (data.is_complete) {
                    console.log("✅ Processing complete!");
                    clearInterval(pollingInterval);
                    loadingSpinner.classList.add('hidden');
                    processingAnimation.classList.add('hidden');
                }
            } else {
                console.error("❌ Error in results:", data);
                resultsContent.innerHTML = `<div class="text-red-500">Error: ${data.message || 'An unexpected error occurred'}</div>`;
                clearInterval(pollingInterval);
                loadingSpinner.classList.add('hidden');
                processingAnimation.classList.add('hidden');
            }
        } catch (error) {
            console.error("❌ Error polling results:", error);
            resultsContent.innerHTML = `<div class="text-red-500">Error: ${error.message}</div>`;
            clearInterval(pollingInterval);
            loadingSpinner.classList.add('hidden');
            processingAnimation.classList.add('hidden');
        }
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous results and show loading state
        resultsContent.innerHTML = '';
        loadingSpinner.classList.remove('hidden');
        processingAnimation.classList.remove('hidden');
        submitButton.disabled = true;
        
        try {
            console.log("🌙 Submitting form...");
            const formData = new FormData(form);
            
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log("📡 Response:", data);
            
            if (data.status === 'success') {
                console.log("✨ Starting polling for results...");
                // Start polling for results every 5 seconds
                pollingInterval = setInterval(pollForResults, 5000);
                // Also poll immediately
                await pollForResults();
            } else {
                console.error("❌ Error:", data);
                resultsContent.innerHTML = `<div class="text-red-500">Error: ${data.message || 'An unexpected error occurred'}</div>`;
                loadingSpinner.classList.add('hidden');
                processingAnimation.classList.add('hidden');
            }
        } catch (error) {
            console.error("❌ Error:", error);
            resultsContent.innerHTML = `<div class="text-red-500">Error: ${error.message}</div>`;
            loadingSpinner.classList.add('hidden');
            processingAnimation.classList.add('hidden');
        } finally {
            submitButton.disabled = false;
        }
    });
});

// Copy to clipboard function
function copyToClipboard(button) {
    const codeBlock = button.parentElement.querySelector('code');
    const text = codeBlock.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('text-green-500');
        
        setTimeout(() => {
            button.innerHTML = originalIcon;
            button.classList.remove('text-green-500');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        button.innerHTML = '<i class="fas fa-times"></i>';
        button.classList.add('text-red-500');
        
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-copy"></i>';
            button.classList.remove('text-red-500');
        }, 2000);
    });
}

// Add some fun console messages
console.log("🌙 Moon Dev's RBI Agent Frontend loaded!");
console.log("✨ Ready to discover some alpha!");

// Add CSS for message animations
const style = document.createElement('style');
style.textContent = `
    .message-animation {
        opacity: 0;
        animation: fadeInSlide 0.5s ease-out forwards;
    }
    
    @keyframes fadeInSlide {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .processing-phase {
        opacity: 0.4;
        transition: opacity 0.3s ease;
    }
    
    .processing-phase.active {
        opacity: 1;
    }
    
    .phase-complete .phase-icon {
        color: #34d399;
        animation: completePulse 0.5s ease-out;
    }
    
    @keyframes completePulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .fun-message {
        animation: fadeInOut 4s ease-in-out infinite;
    }
    
    @keyframes fadeInOut {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }
`;
document.head.appendChild(style); 