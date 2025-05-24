// DOM Elements
const availableACUsElement = document.querySelector('#available-acus .value');
const lastUpdatedElement = document.getElementById('last-updated-time');
const historyTableBody = document.querySelector('#history-table tbody');
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
    if (isNaN(num)) return "Unknown";
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Extract number from string
function extractNumber(str) {
    if (!str) return NaN;
    const match = str.toString().match(/\d+/);
    return match ? parseInt(match[0], 10) : NaN;
}

// Update the current usage display
function updateCurrentUsage(data) {
    if (!data || Object.keys(data).length === 0) {
        availableACUsElement.textContent = 'No data';
        lastUpdatedElement.textContent = 'Never';
        return;
    }
    
    // Extract available ACUs value
    const availableACUs = extractNumber(data.available_acus);
    
    // Update the display
    availableACUsElement.textContent = formatNumber(availableACUs);
    lastUpdatedElement.textContent = formatDate(data.timestamp);
}

// Update the history table
function updateHistoryTable(historyData) {
    historyTableBody.innerHTML = '';
    
    if (!historyData || historyData.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="3" class="loading-message">No history data available</td>';
        historyTableBody.appendChild(row);
        return;
    }
    
    historyData.forEach(item => {
        const row = document.createElement('tr');
        
        const sessionCell = document.createElement('td');
        sessionCell.textContent = item.session_name || 'Unknown';
        
        const createdAtCell = document.createElement('td');
        createdAtCell.textContent = item.created_at || 'Unknown';
        
        const acusUsedCell = document.createElement('td');
        acusUsedCell.textContent = item.acus_used || 'Unknown';
        
        row.appendChild(sessionCell);
        row.appendChild(createdAtCell);
        row.appendChild(acusUsedCell);
        
        historyTableBody.appendChild(row);
    });
}

// Create or update the usage history chart
function updateUsageChart(historyData) {
    if (!historyData || historyData.length === 0) {
        return;
    }
    
    historyData.sort((a, b) => {
        return new Date(a.created_at) - new Date(b.created_at);
    });
    
    // Prepare data for the chart
    const labels = historyData.map(item => {
        try {
            const date = new Date(item.created_at);
            return date.toLocaleDateString();
        } catch (e) {
            return item.created_at || 'Unknown';
        }
    });
    
    const acusUsedValues = historyData.map(item => {
        return extractNumber(item.acus_used) || 0;
    });
    
    // Create or update the chart
    if (usageChart) {
        usageChart.data.labels = labels;
        usageChart.data.datasets[0].data = acusUsedValues;
        usageChart.update();
    } else {
        usageChart = new Chart(usageChartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'ACUs Used',
                        data: acusUsedValues,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
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
                            text: 'ACUs Used'
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
        availableACUsElement.textContent = 'Error';
    }
}

async function fetchUsageHistory() {
    try {
        const response = await fetch('/api/usage-history');
        const data = await response.json();
        updateHistoryTable(data);
        updateUsageChart(data);
    } catch (error) {
        console.error('Error fetching usage history:', error);
    }
}

// Initialize the application
function init() {
    fetchLatestCreditData();
    fetchUsageHistory();
    
    // Refresh data every 5 minutes
    setInterval(() => {
        fetchLatestCreditData();
        fetchUsageHistory();
    }, 5 * 60 * 1000);
}

// Start the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
