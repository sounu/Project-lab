// Add smooth scrolling to recommendations
function scrollToRecommendations(elementId) {
    const element = document.getElementById(elementId);
    element.scrollIntoView({ behavior: 'smooth' });
}

// Add loading animation
function showLoading(button) {
    button.disabled = true;
    button.innerHTML = 'Loading...';
}

function hideLoading(button) {
    button.disabled = false;
    button.innerHTML = 'Get Recommendations 👉';
} 