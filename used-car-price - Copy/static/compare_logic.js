// --- MOCK CAR DATABASE ---
// Updated with comprehensive data for all comparison fields
const mockCarData = {
    "Swift": {
        "name": "Maruti Swift VXi",
        "img": "https://i.imgur.com/gJ6hG9f.png", // Example image URL
        "price": 7.5,
        "fuel": "Petrol",
        "transmission": "Manual",
        "mileage": 22.38,
        "power": 88.50,
        "torque": 113,
        "engine_cc": 1197,
        "top_speed": 165,
        "touchscreen": "Yes (7-inch)",
        "sunroof": "No",
        "ac_type": "Automatic Climate Control",
        "seat_material": "Fabric",
        "length": 3845,
        "width": 1735,
        "boot_space": 268,
        "ground_clearance": 163,
        "fuel_tank": 37,
        "safety_rating": 2, // (Example GNCAP)
        "airbags": 2,
        "parking_sensors": "Yes"
    },
    "Verna": {
        "name": "Hyundai Verna SX",
        "img": "https://i.imgur.com/8fS9p3H.png", // Example image URL
        "price": 12.8,
        "fuel": "Petrol",
        "transmission": "Automatic (CVT)",
        "mileage": 18.6,
        "power": 113.18,
        "torque": 144,
        "engine_cc": 1497,
        "top_speed": 190,
        "touchscreen": "Yes (8-inch)",
        "sunroof": "Yes (Electric)",
        "ac_type": "Automatic Climate Control",
        "seat_material": "Leatherette",
        "length": 4535,
        "width": 1765,
        "boot_space": 528,
        "ground_clearance": 165,
        "fuel_tank": 45,
        "safety_rating": 5, // (Example GNCAP)
        "airbags": 6,
        "parking_sensors": "Yes + Camera"
    },
    "Nexon": {
        "name": "Tata Nexon XZ+",
        "img": "https://i.imgur.com/bY3A1bE.png", // Example image URL
        "price": 10.5,
        "fuel": "Petrol",
        "transmission": "Manual",
        "mileage": 17.01,
        "power": 118.27,
        "torque": 170,
        "engine_cc": 1199,
        "top_speed": 180,
        "touchscreen": "Yes (7-inch)",
        "sunroof": "Yes (Electric)",
        "ac_type": "Automatic Climate Control",
        "seat_material": "Fabric",
        "length": 3993,
        "width": 1811,
        "boot_space": 350,
        "ground_clearance": 209,
        "fuel_tank": 44,
        "safety_rating": 5, // (Example GNCAP)
        "airbags": 6,
        "parking_sensors": "Yes + Camera"
    }
};

// --- GLOBAL STATE ---
let activeModalSlot = 1;
let selectedCars = { 1: null, 2: null, 3: null };
let myCompChart = null; // Chart instance

// --- DOM Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching logic
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // Deactivate all
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
                content.style.display = 'none';
            });
            
            // Activate clicked
            button.classList.add('active');
            const activeContent = document.getElementById(`tab-${tabId}`);
            activeContent.classList.add('active');
            activeContent.style.display = 'block';
        });
    });

    // Close modal on overlay click
    document.getElementById('selectionModalOverlay').addEventListener('click', (e) => {
        if (e.target.id === 'selectionModalOverlay') {
            closeSelectionModal();
        }
    });
});

// --- MODAL FUNCTIONS ---
function openSelectionModal(slot) {
    activeModalSlot = slot;
    document.getElementById('modal-slot-number').innerText = slot;
    document.getElementById('selectionModalOverlay').style.display = 'flex';
}

function closeSelectionModal() {
    document.getElementById('selectionModalOverlay').style.display = 'none';
}

function addSelectedCar() {
    const selectedCarName = document.getElementById('modal-car-selector').value;
    const car = mockCarData[selectedCarName];
    
    selectedCars[activeModalSlot] = car; // Store car data
    
    // Update the main selection card (top section)
    document.getElementById(`car-title-${activeModalSlot}`).innerText = car.name;
    document.getElementById(`price-${activeModalSlot}`).innerText = `${car.price} L`;
    document.getElementById(`mileage-${activeModalSlot}`).innerText = `${car.mileage} kmpl`;
    document.getElementById(`power-${activeModalSlot}`).innerText = `${car.power} bhp`;
    
    // Update card image
    const imgWrapper = document.getElementById(`car-img-wrapper-${activeModalSlot}`);
    imgWrapper.innerHTML = `<img src="${car.img}" alt="${car.name}">`;
    
    // Update sticky header name
    document.getElementById(`sticky-name-${activeModalSlot}`).innerText = car.name;

    // Update the main comparison table
    updateComparisonTable();
    closeSelectionModal();
    
    // Check if we can show the chart
    if (selectedCars[1] && selectedCars[2]) {
        updateChart();
    }
}

// --- COMPARISON TABLE & CHART ---
function updateComparisonTable() {
    // Clear all previous comparison values
    document.querySelectorAll('.comp-table tbody tr').forEach(row => {
        row.querySelectorAll('td[class^="comp-val-"]').forEach(cell => {
            cell.innerText = '--';
            cell.classList.remove('highlight-success', 'highlight-danger');
        });
    });

    // Loop through all selected cars (1, 2, 3)
    for (const slot in selectedCars) {
        const car = selectedCars[slot];
        if (car) {
            // Update table headers
            document.getElementById(`comp-car-${slot}-name`).innerText = car.name;

            // Populate all stats from the car object
            document.querySelectorAll('.comp-table tbody tr').forEach(row => {
                const stat = row.getAttribute('data-stat');
                if (car[stat] !== undefined) {
                    const cell = row.querySelector(`.comp-val-${slot}`);
                    // Add units where appropriate
                    let value = car[stat];
                    if (stat === 'price') value = `₹ ${value} L`;
                    if (stat === 'mileage') value = `${value} kmpl`;
                    if (stat === 'power') value = `${value} bhp`;
                    if (stat === 'torque') value = `${value} Nm`;
                    if (stat === 'engine_cc') value = `${value} cc`;
                    if (stat === 'top_speed') value = `${value} km/h`;
                    if (stat === 'length' || stat === 'width' || stat === 'ground_clearance') value = `${value} mm`;
                    if (stat === 'boot_space' || stat === 'fuel_tank') value = `${value} L`;
                    if (stat === 'safety_rating') value = `${value} ★`;
                    
                    cell.innerText = value;
                }
            });
        }
    }
}

function updateChart() {
    const chartArea = document.getElementById('price-mileage-chart');
    chartArea.style.display = 'block';
    
    const ctx = document.getElementById('compChart').getContext('2d');
    
    const carNames = [];
    const prices = [];
    const mileages = [];

    [selectedCars[1], selectedCars[2], selectedCars[3]].forEach(car => {
        if (car) {
            carNames.push(car.name);
            prices.push(car.price);
            mileages.push(car.mileage);
        }
    });

    if (myCompChart) {
        myCompChart.destroy(); // Destroy old chart instance
    }

    myCompChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: carNames,
            datasets: [
                {
                    label: 'Price (₹ Lakhs)',
                    data: prices,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    yAxisID: 'yPrice',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Mileage (kmpl)',
                    data: mileages,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    yAxisID: 'yMileage',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false }
                },
                yPrice: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Price (₹ Lakhs)' },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)' // Lighter grid for dark mode
                    }
                },
                yMileage: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Mileage (kmpl)' },
                    grid: { display: false } // Hide grid for this axis
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}


// --- DYNAMIC HIGHLIGHTING ---
function highlightDifferences() {
    document.querySelectorAll('.comp-table tbody tr').forEach(row => {
        const stat = row.getAttribute('data-stat');
        if (!stat) return;

        // Rules: true = higher is better, false = lower is better
        const rules = {
            "price": false, "mileage": true, "power": true, "torque": true,
            "engine_cc": true, "top_speed": true, "length": true, "width": true,
            "boot_space": true, "ground_clearance": true, "fuel_tank": true,
            "safety_rating": true, "airbags": true
        };

        if (rules[stat] === undefined) return; // Not a numeric stat to compare
        const higherIsBetter = rules[stat];

        const values = [];
        const cells = [];

        [1, 2, 3].forEach(slot => {
            const car = selectedCars[slot];
            const cell = row.querySelector(`.comp-val-${slot}`);
            cells.push(cell);
            if (car && car[stat] !== undefined && typeof car[stat] === 'number') {
                values.push(car[stat]);
            } else {
                values.push(null); // No value for this car
            }
        });

        // Find min/max
        const validValues = values.filter(v => v !== null);
        if (validValues.length < 2) return; // Can't compare
        
        const minVal = Math.min(...validValues);
        const maxVal = Math.max(...validValues);
        
        if (minVal === maxVal) return; // All values are the same

        // Apply classes
        values.forEach((val, index) => {
            if (val === null) return;
            const cell = cells[index];
            cell.classList.remove('highlight-success', 'highlight-danger');

            if (higherIsBetter) {
                if (val === maxVal) cell.classList.add('highlight-success');
                if (val === minVal) cell.classList.add('highlight-danger');
            } else {
                if (val === minVal) cell.classList.add('highlight-success');
                if (val === maxVal) cell.classList.add('highlight-danger');
            }
        });
    });
}

// --- UTILITY FUNCTIONS ---
function resetComparison() {
    selectedCars = { 1: null, 2: null, 3: null };
    
    // Reset top cards
    [1, 2, 3].forEach(slot => {
        document.getElementById(`car-title-${slot}`).innerText = `Select Car ${slot}`;
        document.getElementById(`price-${slot}`).innerText = '--';
        document.getElementById(`mileage-${slot}`).innerText = '--';
        document.getElementById(`power-${slot}`).innerText = '--';
        document.getElementById(`sticky-name-${slot}`).innerText = `Car ${slot}`;
        
        const imgWrapper = document.getElementById(`car-img-wrapper-${slot}`);
        imgWrapper.innerHTML = `<i class="fas fa-car" style="font-size: 3.5em; color: #CCC;"></i>`;
        
        // Reset table headers
        document.getElementById(`comp-car-${slot}-name`).innerText = `Car ${slot}`;
    });

    // Clear table data
    updateComparisonTable();

    // Hide and destroy chart
    if (myCompChart) {
        myCompChart.destroy();
    }
    document.getElementById('price-mileage-chart').style.display = 'none';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleStickyHeader() {
    // This function should be attached to the body's onscroll event
    // e.g. <body onscroll="toggleStickyHeader()">
    
    const header = document.getElementById('sticky-header');
    // Anchor point is the comparison table area
    const anchor = document.getElementById('comparison-area-anchor'); 
    
    if (anchor) {
        const anchorTop = anchor.getBoundingClientRect().top;
        if (anchorTop <= 0) { // When the table top hits the viewport top
            header.style.transform = 'translateY(0)';
        } else {
            header.style.transform = 'translateY(-100%)';
        }
    }
}