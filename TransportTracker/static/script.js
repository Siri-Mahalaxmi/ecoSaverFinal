// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;
    
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Theme toggle event listener
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        
        // Trigger a custom event for charts to update
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
    });
    
    function updateThemeIcon(theme) {
        if (theme === 'dark') {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
});

// Form Validation and Enhancement
document.addEventListener('DOMContentLoaded', function() {
    const trackingForm = document.getElementById('trackingForm');
    
    if (trackingForm) {
        trackingForm.addEventListener('submit', function(e) {
            let hasValidEntry = false;
            
            // Check if at least one category has valid input
            const transportEntries = document.querySelectorAll('.transport-entry');
            const applianceEntries = document.querySelectorAll('.appliance-entry');
            
            // Check transport entries
            transportEntries.forEach(entry => {
                const vehicle = entry.querySelector('select[name^="transport_vehicle_"]').value;
                const fuel = entry.querySelector('select[name^="transport_fuel_"]').value;
                const distance = entry.querySelector('input[name^="transport_distance_"]').value;
                
                if (vehicle && fuel && distance && parseFloat(distance) > 0) {
                    hasValidEntry = true;
                }
            });
            
            // Check appliance entries
            applianceEntries.forEach(entry => {
                const appliance = entry.querySelector('select[name^="appliance_name_"]').value;
                const hours = entry.querySelector('input[name^="appliance_hours_"]').value;
                
                if (appliance && hours && parseFloat(hours) > 0) {
                    hasValidEntry = true;
                }
            });
            
            // Check other inputs
            const gasUsage = document.querySelector('input[name="gas_usage"]').value;
            const wasteAmount = document.querySelector('input[name="waste_amount"]').value;
            const waterUsage = document.querySelector('input[name="water_usage"]').value;
            const dietFrequency = document.querySelector('input[name="diet_frequency"]').value;
            
            if ((gasUsage && parseFloat(gasUsage) > 0) ||
                (wasteAmount && parseFloat(wasteAmount) > 0) ||
                (waterUsage && parseFloat(waterUsage) > 0) ||
                (dietFrequency && parseFloat(dietFrequency) > 0)) {
                hasValidEntry = true;
            }
            
            if (!hasValidEntry) {
                e.preventDefault();
                alert('Please fill in at least one category with valid data to calculate your carbon footprint.');
                return false;
            }
            
            // Show loading state
            const submitBtn = trackingForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calculating...';
            submitBtn.disabled = true;
            
            // Re-enable button after a delay (in case of error)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 10000);
        });
    }
});

// Enhanced Number Input Validation
document.addEventListener('DOMContentLoaded', function() {
    const numberInputs = document.querySelectorAll('input[type="number"]');
    
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Remove negative values
            if (this.value < 0) {
                this.value = 0;
            }
            
            // Limit decimal places based on step
            const step = parseFloat(this.step) || 1;
            if (step < 1) {
                const decimalPlaces = step.toString().split('.')[1]?.length || 0;
                this.value = parseFloat(this.value).toFixed(decimalPlaces);
            }
        });
        
        // Validate on blur
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.value = '0';
            }
        });
    });
});

// Smooth Scroll for Navigation
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Auto-save form data (optional enhancement)
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('trackingForm');
    
    if (form) {
        // Load saved data
        loadFormData();
        
        // Save data on input change
        form.addEventListener('input', function() {
            saveFormData();
        });
        
        // Clear saved data on successful submission
        form.addEventListener('submit', function() {
            setTimeout(() => {
                clearFormData();
            }, 1000);
        });
    }
    
    function saveFormData() {
        const formData = new FormData(document.getElementById('trackingForm'));
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        localStorage.setItem('carbonTrackingForm', JSON.stringify(data));
    }
    
    function loadFormData() {
        const savedData = localStorage.getItem('carbonTrackingForm');
        
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                
                Object.keys(data).forEach(key => {
                    const element = document.querySelector(`[name="${key}"]`);
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = data[key] === element.value;
                        } else {
                            element.value = data[key];
                        }
                    }
                });
            } catch (error) {
                console.log('Error loading saved form data:', error);
            }
        }
    }
    
    function clearFormData() {
        localStorage.removeItem('carbonTrackingForm');
    }
});

// Chart Theme Updates
window.addEventListener('themeChanged', function(e) {
    const isDark = e.detail.theme === 'dark';
    
    // Update Chart.js default colors for dark theme
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isDark ? '#e9ecef' : '#333333';
        Chart.defaults.borderColor = isDark ? '#4a5568' : '#dee2e6';
        Chart.defaults.backgroundColor = isDark ? '#2d3748' : '#ffffff';
        
        // Update scale colors
        Chart.defaults.scale.grid.color = isDark ? '#4a5568' : '#dee2e6';
        Chart.defaults.scale.ticks.color = isDark ? '#e9ecef' : '#333333';
        Chart.defaults.plugins.legend.labels.color = isDark ? '#e9ecef' : '#333333';
        
        // Redraw existing charts if they exist
        Object.values(Chart.instances).forEach(chart => {
            // Update chart options for dark theme
            if (chart.options.scales) {
                Object.keys(chart.options.scales).forEach(scaleKey => {
                    if (chart.options.scales[scaleKey].grid) {
                        chart.options.scales[scaleKey].grid.color = isDark ? '#4a5568' : '#dee2e6';
                    }
                    if (chart.options.scales[scaleKey].ticks) {
                        chart.options.scales[scaleKey].ticks.color = isDark ? '#e9ecef' : '#333333';
                    }
                    if (chart.options.scales[scaleKey].title) {
                        chart.options.scales[scaleKey].title.color = isDark ? '#e9ecef' : '#333333';
                    }
                });
            }
            if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                chart.options.plugins.legend.labels.color = isDark ? '#e9ecef' : '#333333';
            }
            chart.update();
        });
    }
});

// Initialize chart theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    if (currentTheme) {
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: currentTheme } }));
    }
});

// Toast Notifications (for better user feedback)
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Performance optimization for large datasets
document.addEventListener('DOMContentLoaded', function() {
    // Lazy load charts when they come into view
    const chartContainers = document.querySelectorAll('canvas');
    
    if ('IntersectionObserver' in window) {
        const chartObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('chart-visible');
                    chartObserver.unobserve(entry.target);
                }
            });
        });
        
        chartContainers.forEach(canvas => {
            chartObserver.observe(canvas);
        });
    }
});
