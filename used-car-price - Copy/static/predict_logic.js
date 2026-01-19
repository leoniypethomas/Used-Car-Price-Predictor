// --- CHART FUNCTION (unchanged) ---
function createPriceComparisonChart(showroomPrice, predictedPrice) {
    const ctx = document.getElementById('priceComparisonChart').getContext('2d');
    
    if (window.myPriceChart instanceof Chart) {
        window.myPriceChart.destroy();
    }

    window.myPriceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Showroom Price', 'Predicted Price'],
            datasets: [{
                label: 'Price in Lakhs',
                data: [showroomPrice, predictedPrice],
                // NOTE: Chart colors are inlined here — leave if you want the look
                backgroundColor: ['rgba(30, 144, 255, 0.8)', 'rgba(40, 167, 69, 0.8)'],
                borderColor: ['rgba(30, 144, 255, 1)', 'rgba(40, 167, 69, 1)'],
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { display: false } },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Price (₹ Lakhs)' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// --- Wrap everything in DOMContentLoaded ---
document.addEventListener('DOMContentLoaded', () => {

    // --- Correct element IDs to match index.html ---
    const brandSelector = document.getElementById('Brand');       // was 'brand-selector'
    const modelSelector = document.getElementById('Car_Name');    // was 'model-selector'

    // Check brandModelMap exists (comes from template: const brandModelMap = {{ brand_map | tojson }};)
    if (!window.brandModelMap) {
        console.warn('brandModelMap is not defined. Ensure the template sets `brand_map` with tojson.');
    }

    // Initialize model selector state
    if (modelSelector) {
        // If there are no options yet, set a default placeholder
        if (!modelSelector.querySelector('option')) {
            modelSelector.innerHTML = '<option value="" disabled selected>Select Brand First</option>';
            modelSelector.disabled = true;
        }
    }

    if (brandSelector && modelSelector) {
        // Populate the brand dropdown if it has no options (optional)
        // Note: your template already fills Brand <select> with options server-side, so skip unless needed.

        brandSelector.addEventListener('change', () => {
            const selectedBrand = brandSelector.value;

            // Reset model selector
            modelSelector.innerHTML = ''; 

            if (selectedBrand && window.brandModelMap && Array.isArray(window.brandModelMap[selectedBrand])) {
                const models = window.brandModelMap[selectedBrand];

                // Add a prompt option
                const promptOpt = document.createElement('option');
                promptOpt.value = '';
                promptOpt.disabled = true;
                promptOpt.selected = true;
                promptOpt.textContent = 'Select Model';
                modelSelector.appendChild(promptOpt);

                // Populate with models
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelSelector.appendChild(option);
                });

                modelSelector.disabled = false;
            } else {
                // No models found for this brand
                modelSelector.disabled = true;
                modelSelector.innerHTML = '<option value="" disabled selected>No models available</option>';
            }
        });
    } else {
        if (!brandSelector) console.error('Brand selector element not found (expected id="Brand").');
        if (!modelSelector) console.error('Model selector element not found (expected id="Car_Name").');
    }

    // --- Get all form elements ---
    const form = document.getElementById('predictionForm');
    const resultDisplay = document.getElementById('resultDisplay');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const initialMessage = document.getElementById('initialMessage'); // matches index.html id

    const predictedPriceElem = document.getElementById('predictedPriceElem');
    const resYearElem = document.getElementById('res-year');
    const resKmsElem = document.getElementById('res-kms');
    const resFuelElem = document.getElementById('res-fuel');
    const resBrandElem = document.getElementById('res-brand');
    const resCityElem = document.getElementById('res-city');
    const resTransmissionElem = document.getElementById('res-transmission');

    if (!form) {
        console.error('Prediction form not found!');
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI references (already defined above)
        if (initialMessage) initialMessage.style.display = 'none';
        if (resultDisplay) resultDisplay.style.display = 'none';
        if (loadingSpinner) loadingSpinner.style.display = 'block';

        // Build JSON payload from form
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        // Optionally convert numeric fields here:
        const intFields = ['Year', 'Owner', 'Kms_Driven', 'Accidents', 'Engine_Power(cc)', 'Insurance_Age(yrs)'];
        intFields.forEach(k => {
            if (payload[k] !== undefined && payload[k] !== '') {
                const parsed = Number(payload[k]);
                if (!Number.isNaN(parsed)) payload[k] = parsed;
            }
        });
        // Mileage and Present_Price might be floats:
        if (payload['Mileage(km/l)']) payload['Mileage(km/l)'] = Number(payload['Mileage(km/l)']);
        if (payload['Present_Price(Lakhs)']) payload['Present_Price(Lakhs)'] = Number(payload['Present_Price(Lakhs)']);
        if (payload['Maintenance_Cost(₹/yr)']) payload['Maintenance_Cost(₹/yr)'] = Number(payload['Maintenance_Cost(₹/yr)']);

        let response, data;
        try {
            response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            // If server returned non-JSON (HTML), parsing will throw
            const text = await response.text(); // read raw body first
            // Try parse JSON safely
            try {
                data = JSON.parse(text);
            } catch (parseErr) {
                // Not JSON — log and show helpful error
                console.error('Server returned non-JSON response:', text);
                throw new Error('Server did not return JSON. See console for response body.');
            }

            // Now we have `data` as JSON object
            console.log('Predict API response JSON:', data);

            if (!response.ok) {
                // server returned 4xx/5xx with JSON body
                const msg = data.error || data.message || `Server returned ${response.status}`;
                throw new Error(msg);
            }

            // Expecting { success: true, predicted_price: ..., details: {...}, showroom_price: ... }
            if (data.success) {
                if(predictedPriceElem) predictedPriceElem.innerText = `₹ ${Number(data.predicted_price).toFixed(2)} Lakhs`;
                if(resYearElem) resYearElem.innerText = data.details?.Year || data.details?.year || '--';
                if(resKmsElem) resKmsElem.innerText = (data.details?.['Kms_Driven'] ?? data.details?.kms ?? '--') + (data.details?.['Kms_Driven'] ? ' km' : '');
                if(resFuelElem) resFuelElem.innerText = data.details?.['Fuel_Type'] || data.details?.fuel || '--';
                if(resBrandElem) resBrandElem.innerText = data.details?.['Car_Name'] || data.details?.brand || '--';
                if(resCityElem) resCityElem.innerText = data.details?.City || data.details?.city || '--';
                if(resTransmissionElem) resTransmissionElem.innerText = data.details?.Transmission || data.details?.transmission || '--';

                if(resultDisplay) resultDisplay.style.display = 'block';

                // Make sure showroom_price exists
                const showroom = Number(data.showroom_price) || 0;
                createPriceComparisonChart(showroom, Number(data.predicted_price) || 0);

            } else {
                // API returned success:false
                const errMsg = data.error || 'Prediction failed on server.';
                console.error('API error:', errMsg, data);
                alert(`Prediction error: ${errMsg}`);
                if (initialMessage) initialMessage.style.display = 'block';
            }

        } catch (err) {
            console.error('Error during prediction flow:', err);
            alert(err.message || 'An error occurred while predicting. Check the console for details.');
            if (initialMessage) initialMessage.style.display = 'block';
        } finally {
            // Always hide spinner
            if (loadingSpinner) loadingSpinner.style.display = 'none';
        }
    });

});
