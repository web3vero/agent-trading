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

async function pollForResults() {
    try {
        const response = await fetch('/results');
        const data = await response.json();
        
        if (data.status === 'success' && data.results) {
            // Update UI with results
            data.results.forEach(result => {
                if (result.status === 'success') {
                    const resultHtml = `
                        <div class="mb-8 p-4 bg-gray-800 rounded-lg">
                            <h3 class="text-xl font-bold mb-4">Strategy ${result.strategy_number} Results</h3>
                            
                            <div class="mb-6">
                                <h4 class="text-lg font-semibold mb-2">Strategy Analysis</h4>
                                <pre class="bg-gray-900 p-4 rounded overflow-x-auto">${result.strategy}</pre>
                                <a href="/download/strategy/${result.strategy_file}" class="text-blue-400 hover:text-blue-300">
                                    Download Strategy
                                </a>
                            </div>
                            
                            <div>
                                <h4 class="text-lg font-semibold mb-2">Backtest Implementation</h4>
                                <pre class="bg-gray-900 p-4 rounded overflow-x-auto">${result.backtest}</pre>
                                <a href="/download/backtest/${result.backtest_file}" class="text-blue-400 hover:text-blue-300">
                                    Download Backtest
                                </a>
                            </div>
                        </div>
                    `;
                    document.getElementById('results').innerHTML += resultHtml;
                } else {
                    // Handle error for this strategy
                    const errorHtml = `
                        <div class="mb-8 p-4 bg-red-900 rounded-lg">
                            <h3 class="text-xl font-bold mb-4">Strategy ${result.strategy_number} Error</h3>
                            <p class="text-red-300">${result.error}</p>
                        </div>
                    `;
                    document.getElementById('results').innerHTML += errorHtml;
                }
            });
            
            if (data.complete) {
                // Stop polling when processing is complete
                return true;
            }
        }
        return false;
    } catch (error) {
        console.error('Error polling for results:', error);
        return true; // Stop polling on error
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyzeForm');
    const spinner = document.getElementById('spinner');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const processingAnimation = document.getElementById('processingAnimation');
    const funMessageElement = document.getElementById('funMessage');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset all progress messages and states
        document.querySelectorAll('.progress-messages').forEach(el => el.innerHTML = '');
        document.querySelectorAll('.processing-phase').forEach(el => {
            el.classList.remove('active', 'phase-complete', 'phase-error');
        });
        
        // Reset and show processing animation
        spinner.classList.remove('hidden');
        results.classList.add('hidden');
        processingAnimation.classList.remove('hidden');
        
        // Start fun message cycle
        const messageInterval = cycleMessages(funMessageElement, funMessages);
        
        try {
            // Count number of strategies to process
            const formData = new FormData(form);
            const links = formData.get('links');
            const numStrategies = links.split(/[\n,]/).filter(link => link.trim()).length;
            
            // Start the phase animations
            const researchPhase = document.getElementById('researchPhase');
            const backtestPhase = document.getElementById('backtestPhase');
            const debugPhase = document.getElementById('debugPhase');
            
            // Process each phase
            await processPhase(researchPhase, researchMessages, PHASE_TIMINGS.research);
            await processPhase(backtestPhase, backtestMessages, PHASE_TIMINGS.backtest);
            await processPhase(debugPhase, debugMessages, PHASE_TIMINGS.debug);
            
            // Start actual processing
            console.log("🌙 Sending request to /analyze endpoint...");
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            
            console.log("📡 Received response from server");
            const data = await response.json();
            console.log("🔍 Response data:", data);
            
            // Show results section
            results.classList.remove('hidden');
            resultsContent.innerHTML = ''; // Clear previous results
            
            if (data.status === 'success') {
                // Start polling for results
                const pollInterval = setInterval(async () => {
                    const complete = await pollForResults();
                    if (complete) {
                        clearInterval(pollInterval);
                        spinner.classList.add('hidden');
                        processingAnimation.classList.add('hidden');
                        clearInterval(messageInterval);
                    }
                }, 5000); // Poll every 5 seconds
            } else {
                console.error("❌ Error in response:", data);
                resultsContent.innerHTML = `
                    <div class="bg-red-900/50 text-red-200 p-6 rounded-lg error-animation">
                        <h3 class="text-xl font-bold mb-2">❌ Error</h3>
                        <p>${data.message || 'An unexpected error occurred in the response format'}</p>
                    </div>
                `;
                spinner.classList.add('hidden');
                processingAnimation.classList.add('hidden');
                clearInterval(messageInterval);
            }
        } catch (error) {
            console.error('❌ Error:', error);
            results.classList.remove('hidden');
            resultsContent.innerHTML = `
                <div class="bg-red-900/50 text-red-200 p-6 rounded-lg error-animation">
                    <h3 class="text-xl font-bold mb-2">❌ Error</h3>
                    <p>An unexpected error occurred: ${error.message}</p>
                    <p class="mt-2 text-sm">Please check the console for more details.</p>
                </div>
            `;
            spinner.classList.add('hidden');
            processingAnimation.classList.add('hidden');
            clearInterval(messageInterval);
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