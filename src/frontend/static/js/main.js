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
    
    for (const message of messages) {
        await new Promise(r => setTimeout(r, interval));
        addProgressMessage(phaseElement, message);
    }
    
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
            
            if (data.status === 'success' && Array.isArray(data.results)) {
                console.log(`✨ Processing ${data.results.length} results`);
                // Process each result
                data.results.forEach((result, index) => {
                    console.log(`📊 Processing result ${index + 1}:`, result);
                    updateResult(result);
                });
            } else {
                console.error("❌ Error in response:", data);
                resultsContent.innerHTML = `
                    <div class="bg-red-900/50 text-red-200 p-6 rounded-lg error-animation">
                        <h3 class="text-xl font-bold mb-2">❌ Error</h3>
                        <p>${data.message || 'An unexpected error occurred in the response format'}</p>
                    </div>
                `;
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
        } finally {
            // Clean up
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