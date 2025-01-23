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
    const analyzeForm = document.getElementById('analyzeForm');
    const resultsContent = document.getElementById('resultsContent');
    const spinner = document.getElementById('spinner');
    let pollInterval;

    analyzeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous results and show spinner
        resultsContent.innerHTML = '';
        spinner.classList.remove('hidden');
        
        console.log("🌙 Starting form submission...");
        
        try {
            const formData = new FormData(analyzeForm);
            console.log("📤 Sending request to /analyze endpoint...");
            
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log("📡 Received response:", data);
            
            if (data.status === 'success') {
                console.log("✨ Starting polling for results...");
                startPolling();
            } else {
                console.error("❌ Error in response:", data);
                showError(data.message || "An unexpected error occurred");
            }
        } catch (error) {
            console.error("❌ Error:", error);
            showError(`An unexpected error occurred: ${error.message}`);
        }
    });

    function startPolling() {
        console.log("🔄 Starting polling interval...");
        if (pollInterval) clearInterval(pollInterval);
        
        pollInterval = setInterval(async () => {
            try {
                console.log("📡 Polling for results...");
                const response = await fetch('/results');
                const data = await response.json();
                console.log("📥 Received polling data:", data);
                
                if (data.status === 'success' && Array.isArray(data.results)) {
                    console.log(`✨ Processing ${data.results.length} results`);
                    updateResults(data.results);
                    
                    if (data.is_complete) {
                        console.log("✅ Processing complete, stopping polling");
                        clearInterval(pollInterval);
                        spinner.classList.add('hidden');
                    }
                } else {
                    console.error("❌ Invalid results data:", data);
                }
            } catch (error) {
                console.error("❌ Polling error:", error);
                clearInterval(pollInterval);
                spinner.classList.add('hidden');
                showError(`Error fetching results: ${error.message}`);
            }
        }, 5000);
    }

    function updateResults(results) {
        resultsContent.innerHTML = '';
        
        results.forEach(result => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'mb-8 p-6 bg-white rounded-lg shadow-md';
            
            if (result.status === 'success') {
                resultDiv.innerHTML = `
                    <h3 class="text-xl font-bold mb-4">Strategy ${result.strategy_number} Analysis 🎯</h3>
                    <div class="mb-6">
                        <h4 class="text-lg font-semibold mb-2">Strategy Analysis 📊</h4>
                        <pre class="bg-gray-100 p-4 rounded overflow-x-auto">${result.strategy}</pre>
                        <a href="/download/strategy/${result.strategy_file}" class="text-blue-500 hover:text-blue-700">Download Strategy</a>
                    </div>
                    <div>
                        <h4 class="text-lg font-semibold mb-2">Backtest Implementation 🚀</h4>
                        <pre class="bg-gray-100 p-4 rounded overflow-x-auto">${result.backtest}</pre>
                        <a href="/download/backtest/${result.backtest_file}" class="text-blue-500 hover:text-blue-700">Download Backtest</a>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <h3 class="text-xl font-bold mb-4">Strategy ${result.strategy_number} Error ❌</h3>
                    <p class="text-red-500">${result.message}</p>
                `;
            }
            
            resultsContent.appendChild(resultDiv);
        });
    }

    function showError(message) {
        spinner.classList.add('hidden');
        resultsContent.innerHTML = `
            <div class="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                ❌ ${message}
            </div>
        `;
    }
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