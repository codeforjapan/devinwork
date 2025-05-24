// DOM Elements
const creditUsedElement = document.querySelector('#credit-used .value');
const creditLimitElement = document.querySelector('#credit-limit .value');
const creditRemainingElement = document.querySelector('#credit-remaining .value');
const lastUpdatedElement = document.getElementById('last-updated-time');
const usageChartCanvas = document.getElementById('usage-chart');

// Chart instance
let usageChart;

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Calculate remaining credits
function calculateRemaining(used, limit) {
    return Math.max(0, limit - used);
}

// Update the current usage display
function updateCurrentUsage(data) {
    if (!data || Object.keys(data).length === 0) {
        creditUsedElement.textContent = 'No data';
        creditLimitElement.textContent = 'No data';
        creditRemainingElement.textContent = 'No data';
        lastUpdatedElement.textContent = 'Never';
        return;
    }
    
    // Extract values (assuming they're numeric strings)
    const creditUsed = parseInt(data.credit_used.replace(/[^0-9]/g, ''), 10);
    const creditLimit = parseInt(data.credit_limit.replace(/[^0-9]/g, ''), 10);
    const remaining = calculateRemaining(creditUsed, creditLimit);
    
    // Update the display
    creditUsedElement.textContent = formatNumber(creditUsed);
    creditLimitElement.textContent = formatNumber(creditLimit);
    creditRemainingElement.textContent = formatNumber(remaining);
    lastUpdatedElement.textContent = formatDate(data.timestamp);
}

// Create or update the usage history chart
function updateUsageChart(data) {
    if (!data || data.length === 0) {
        return;
    }
    
    // Prepare data for the chart
    const labels = data.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleDateString();
    });
    
    const usedValues = data.map(item => {
        return parseInt(item.credit_used.replace(/[^0-9]/g, ''), 10);
    });
    
    const limitValues = data.map(item => {
        return parseInt(item.credit_limit.replace(/[^0-9]/g, ''), 10);
    });
    
    // Create or update the chart
    if (usageChart) {
        usageChart.data.labels = labels;
        usageChart.data.datasets[0].data = usedValues;
        usageChart.data.datasets[1].data = limitValues;
        usageChart.update();
    } else {
        usageChart = new Chart(usageChartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Credits Used',
                        data: usedValues,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Credit Limit',
                        data: limitValues,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Credits'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }
}

// Fetch the latest credit data
async function fetchLatestCreditData() {
    try {
        const response = await fetch('/api/latest-credit-data');
        const data = await response.json();
        updateCurrentUsage(data);
    } catch (error) {
        console.error('Error fetching latest credit data:', error);
        creditUsedElement.textContent = 'Error';
        creditLimitElement.textContent = 'Error';
        creditRemainingElement.textContent = 'Error';
    }
}

// Fetch all credit data for the chart
async function fetchAllCreditData() {
    try {
        const response = await fetch('/api/credit-data');
        const data = await response.json();
        updateUsageChart(data);
    } catch (error) {
        console.error('Error fetching credit data history:', error);
    }
}

// Initialize the application
function init() {
    fetchLatestCreditData();
    fetchAllCreditData();
    
    // Refresh data every 5 minutes
    setInterval(() => {
        fetchLatestCreditData();
        fetchAllCreditData();
    }, 5 * 60 * 1000);
}

// Start the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
