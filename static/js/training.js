// Training page functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeTrainingPage();
});

function initializeTrainingPage() {
    updateProgressBar();
    attachScenarioListeners();
}

function updateProgressBar() {
    const progressBar = document.querySelector('.progress');
    if (progressBar) {
        const completed = parseInt(progressBar.getAttribute('data-completed'));
        const total = parseInt(progressBar.getAttribute('data-total'));
        const percentage = (completed / total) * 100;
        progressBar.style.width = `${percentage}%`;
    }
}

function attachScenarioListeners() {
    const scenarioCards = document.querySelectorAll('.scenario-card');
    scenarioCards.forEach(card => {
        const button = card.querySelector('button');
        const scenarioId = card.getAttribute('data-scenario-id');
        
        if (button && !button.disabled) {
            button.addEventListener('click', () => startScenario(scenarioId));
        }
    });
}

async function startScenario(scenarioId) {
    try {
        const response = await fetch(`/training/start/${scenarioId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to start scenario');
        }
        
        const data = await response.json();
        
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            displayScenario(data);
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to start scenario. Please try again.');
    }
}

function displayScenario(scenarioData) {
    const contentArea = document.querySelector('.training-content');
    if (!contentArea) return;
    
    contentArea.innerHTML = `
        <div class="scenario-details">
            <h2>${scenarioData.title}</h2>
            <div class="scenario-description">
                ${scenarioData.description}
            </div>
            <div class="email-preview">
                <div class="email-header">
                    <div>From: ${scenarioData.email.from}</div>
                    <div>Subject: ${scenarioData.email.subject}</div>
                </div>
                <div class="email-body">
                    ${scenarioData.email.body}
                </div>
            </div>
            <div class="action-buttons">
                <button onclick="submitVerdict('phishing')" class="danger-button">
                    Mark as Phishing
                </button>
                <button onclick="submitVerdict('legitimate')" class="safe-button">
                    Mark as Legitimate
                </button>
            </div>
        </div>
    `;
}

async function submitVerdict(verdict) {
    try {
        const response = await fetch('/training/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scenario_id: currentScenarioId,
                verdict: verdict
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit verdict');
        }
        
        const result = await response.json();
        showFeedback(result);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to submit verdict. Please try again.');
    }
}

function showFeedback(result) {
    const contentArea = document.querySelector('.training-content');
    if (!contentArea) return;
    
    const feedbackHtml = `
        <div class="feedback-container ${result.correct ? 'correct' : 'incorrect'}">
            <h2>${result.correct ? 'Correct!' : 'Incorrect'}</h2>
            <div class="feedback-details">
                ${result.explanation}
            </div>
            <div class="indicator-list">
                <h3>Key Indicators:</h3>
                <ul>
                    ${result.indicators.map(indicator => `
                        <li>${indicator}</li>
                    `).join('')}
                </ul>
            </div>
            <button onclick="nextScenario()" class="primary-button">
                Next Scenario
            </button>
        </div>
    `;
    
    contentArea.innerHTML = feedbackHtml;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    // Remove any existing error messages
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add the new error message
    document.querySelector('.training-section').prepend(errorDiv);
    
    // Remove the error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function nextScenario() {
    window.location.reload();
}