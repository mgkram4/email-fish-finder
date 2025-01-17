// Main JavaScript functionality for email analysis
async function analyzeEmail() {
    const emailContent = document.getElementById('email-content').value;
    const resultsDiv = document.getElementById('analysis-results');
    
    if (!emailContent.trim()) {
        showError('Please enter email content to analyze');
        return;
    }
    
    try {
        resultsDiv.innerHTML = '<div class="loading">Analyzing email...</div>';
        
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: emailContent })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const result = await response.json();
        
        // Display results
        const resultHtml = `
            <div class="result-card ${result.is_phishing ? 'danger' : 'safe'}">
                <h3>${result.is_phishing ? '⚠️ Potential Phishing' : '✅ Likely Safe'}</h3>
                <p>Confidence: ${(result.confidence * 100).toFixed(0)}%</p>
                
                <div class="details">
                    <h4>Details:</h4>
                    <ul>
                        <li>URLs found: ${result.details.urls_found}</li>
                        <li>Suspicious TLD: ${result.details.suspicious_tld ? 'Yes' : 'No'}</li>
                        <li>URL Shortener: ${result.details.url_shortener ? 'Yes' : 'No'}</li>
                    </ul>
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = resultHtml;
        
    } catch (error) {
        showError('Error analyzing email: ' + error.message);
    }
}

function showError(message) {
    const resultsDiv = document.getElementById('analysis-results');
    resultsDiv.innerHTML = `<div class="error">${message}</div>`;
}

// Event listeners for training page
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize training functions if we're on the training page
    const trainingContainer = document.querySelector('.training-section');
    if (trainingContainer) {
        initializeTraining();
    }
});

function initializeTraining() {
    // Add training-specific initialization here
    const scenarioButtons = document.querySelectorAll('[data-scenario-id]');
    scenarioButtons.forEach(button => {
        button.addEventListener('click', () => {
            const scenarioId = button.dataset.scenarioId;
            startScenario(scenarioId);
        });
    });
}

async function startScenario(scenarioId) {
    try {
        const response = await fetch(`/training/scenario/${scenarioId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to start scenario');
        }
        
        const result = await response.json();
        // Handle scenario start
        window.location.href = result.redirect_url;
        
    } catch (error) {
        console.error('Error starting scenario:', error);
        alert('Failed to start training scenario. Please try again.');
    }
}