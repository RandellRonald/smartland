// js/ui.js

document.addEventListener('DOMContentLoaded', () => {
    const coordinateInput = document.getElementById('coordinates');
    const analyzeBtn = document.getElementById('analyze-btn');

    const statusCard = document.getElementById('status-card');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');

    const summarySection = document.getElementById('summary-section');
    const detailsSection = document.getElementById('details-section');
    const riskTagsContainer = document.getElementById('risk-tags');
    const explanationsContainer = document.getElementById('explanations-container');
    const sourcesList = document.getElementById('sources-list');
    const wardDisplay = document.getElementById('ward-display');
    const infrastructureSection = document.getElementById('infrastructure-section');
    const infraContainer = document.getElementById('infra-container');
    const warningBannerContainer = document.getElementById('warning-banner-container');
    const constraintReasons = document.getElementById('constraint-reasons');

    analyzeBtn.addEventListener('click', async () => {
        console.log("Analyze button clicked");
        const rawInput = coordinateInput.value.trim();
        console.log("Raw input:", rawInput);

        if (!rawInput.includes(",")) {
            showError("Enter coordinates as: latitude, longitude");
            return;
        }

        const parts = rawInput.split(",");

        if (parts.length !== 2) {
            showError("Invalid coordinate format. Use: lat, lon");
            return;
        }

        const lat = parseFloat(parts[0].trim());
        const lon = parseFloat(parts[1].trim());

        if (isNaN(lat) || isNaN(lon)) {
            showError("Coordinates must be valid numbers");
            return;
        }

        if (lat < -90 || lat > 90) {
            showError("Latitude must be between -90 and 90");
            return;
        }

        if (lon < -180 || lon > 180) {
            showError("Longitude must be between -180 and 180");
            return;
        }

        // Reset UI
        clearResults();
        showLoading(true);
        updateMapMarker(lat, lon); // Update map immediately on click

        // Call API
        const result = await analyzeLocation(lat, lon);

        showLoading(false);

        if (result.success) {
            renderResults(result.data);

            // --- Fetch Infrastructure Context ---
            const infraResult = await fetchInfrastructureContext(lat, lon);
            if (infraResult.success) {
                renderInfrastructure(infraResult.data);
                if (infraResult.data.overall_assessment) {
                    renderWarningBanner(infraResult.data.overall_assessment);
                }
            }
        } else {
            showError(result.error.message);
        }
    });

    function showLoading(isLoading) {
        if (isLoading) {
            statusCard.classList.remove('hidden');
            loadingSpinner.classList.remove('hidden');
            errorMessage.classList.add('hidden');
            summarySection.classList.add('hidden');
            detailsSection.classList.add('hidden');
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = "Analyzing...";
        } else {
            statusCard.classList.add('hidden');
            loadingSpinner.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Analyze Location";
        }
    }

    function showError(message) {
        statusCard.classList.remove('hidden');
        errorMessage.classList.remove('hidden');
        errorMessage.textContent = message;
    }

    function clearResults() {
        summarySection.classList.add('hidden');
        detailsSection.classList.add('hidden');
        riskTagsContainer.innerHTML = '';
        explanationsContainer.innerHTML = '';
        sourcesList.innerHTML = '';
        wardDisplay.textContent = '-';

        infrastructureSection.classList.add('hidden');
        infraContainer.innerHTML = '';
        warningBannerContainer.classList.add('hidden');
        constraintReasons.innerHTML = '';
    }

    function renderResults(data) {
        // 1. Summary
        summarySection.classList.remove('hidden');
        wardDisplay.textContent = data.location.ward || "Unknown Ward";

        // Tags
        data.risk_tags.forEach(tag => {
            const el = document.createElement('div');
            // Determine class based on risk_level
            let pClass = 'low';
            const level = tag.risk_level.toUpperCase();
            if (level === 'HIGH' || level === 'CRITICAL') pClass = 'high';
            if (level === 'MODERATE' || level === 'SEMI-CRITICAL') pClass = 'moderate';

            el.className = `risk-pill ${pClass}`;
            el.textContent = `${tag.category}: ${tag.risk_level}`;
            riskTagsContainer.appendChild(el);
        });

        // 2. Explanations
        detailsSection.classList.remove('hidden');
        data.explanations.forEach(expl => {
            const card = document.createElement('div');
            card.className = 'detail-card';

            const header = document.createElement('div');
            header.className = 'detail-header';
            header.innerHTML = `
                <div class="detail-title">${expl.category}</div>
                <div class="toggle-icon">▼</div>
            `;

            const body = document.createElement('div');
            body.className = 'detail-body';

            // Text list
            let html = '<ul>';
            expl.text.forEach(line => {
                html += `<li style="margin-left: 16px; margin-bottom: 4px;">${line}</li>`;
            });
            html += '</ul>';

            // Source
            html += `<div class="source-line">Source: ${expl.source} (${expl.year})</div>`;

            body.innerHTML = html;

            // Click Event
            header.addEventListener('click', () => {
                card.classList.toggle('open');
            });

            card.appendChild(header);
            card.appendChild(body);
            explanationsContainer.appendChild(card);
        });

        // 3. Data Sources
        if (data.data_sources && data.data_sources.length > 0) {
            data.data_sources.forEach(source => {
                const li = document.createElement('li');
                li.style.marginBottom = '4px';
                li.innerHTML = `• ${source}`;
                sourcesList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = "No specific sources cited.";
            sourcesList.appendChild(li);
        }
    }

    // --- New Functions for Infrastructure ---

    function renderInfrastructure(data) {
        infrastructureSection.classList.remove('hidden');

        // Update Subtitle
        const existingTitle = infrastructureSection.querySelector('.card-title');
        let sub = infrastructureSection.querySelector('.infra-subtitle');
        if (!sub) {
            sub = document.createElement('div');
            sub.className = 'infra-subtitle';
            existingTitle.after(sub);
        }
        sub.textContent = 'What daily services and access look like around this location';

        // Icons (SVG) - Material Design style line icons
        const icons = {
            network: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>',
            water: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>',
            healthcare: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6L12 18M6 12L18 12"></path></svg>', // Medical Cross
            fire_rescue: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.1.2-2.2.6-3a7 7 0 0 1 6.9-6.5"></path></svg>',
            density: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
            sanitation: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>',
            daily_services: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>'
        };

        // Strict Configuration Mapping based on specific user request
        const config = [
            { key: 'network', label: 'NETWORK', icon: icons.network, badgeBg: 'bg-blue-soft' },
            { key: 'water', label: 'WATER', icon: icons.water, badgeBg: 'bg-teal-soft' },
            { key: 'healthcare', label: 'HEALTHCARE', icon: icons.healthcare, badgeBg: 'bg-green-soft' },
            { key: 'fire_rescue', label: 'EMERGENCY', icon: icons.fire_rescue, badgeBg: 'bg-orange-soft' },
            { key: 'density', label: 'DENSITY', icon: icons.density, badgeBg: 'bg-purple-soft' },
            { key: 'sanitation', label: 'SANITATION', icon: icons.sanitation, badgeBg: 'bg-gray-soft' },
            { key: 'daily_services', label: 'DAILY ACCESS', icon: icons.daily_services, badgeBg: 'bg-teal-soft' }
        ];

        // Specific Color Logic override for consistency
        function getValueColor(key, val) {
            val = val.toLowerCase();
            // Network: Amber
            if (key === 'network') return 'text-amber';
            // Water: Neutral
            if (key === 'water') return 'text-neutral';
            // Healthcare: Green
            if (key === 'healthcare') return 'text-green';
            // Emergency: Green
            if (key === 'fire_rescue') return 'text-green';
            // Density: Neutral
            if (key === 'density') return 'text-neutral';
            // Sanitation: Amber
            if (key === 'sanitation') return 'text-amber';
            // Daily Access: Amber
            if (key === 'daily_services') return 'text-amber';

            return 'text-neutral';
        }

        // Clear previous content
        infraContainer.innerHTML = '';
        infraContainer.className = 'infra-grid';

        config.forEach(item => {
            let value = data[item.key] || "Info Unavailable";

            // Map backend value for daily services if it differs:
            if (item.key === 'daily_services' && value.toLowerCase().includes('food')) {
                // If user insists on "Limited Services" text but backend says "Food delivery available", we must honor the "DO NOT CHANGE DATA VALUES" unless it's just presentation.
                // User Prompt: "DO NOT change data values". But also listed "DAILY ACCESS: Limited Services" in "CARD CONTENT".
                // Backend logic says: if key % 2 == 0: "Food delivery available", else "Limited services".
                // The user prompt *might* have been showing an example of what *that specific card* looks like in their mind, OR asserting the content.
                // Given "DO NOT change data values" is a strict rule, I will trust the backend data.
                // If the backend returns "Food delivery available", I will show that.
            }

            const valColor = getValueColor(item.key, value);

            const card = document.createElement('div');
            card.className = 'infra-card';

            // 1. Icon Badge
            const badge = document.createElement('div');
            badge.className = `infra-badge ${item.badgeBg}`;
            badge.innerHTML = item.icon;

            // 2. Content Column
            const content = document.createElement('div');
            content.className = 'infra-content';

            // Label
            const label = document.createElement('div');
            label.className = 'infra-label';
            label.textContent = item.label;

            // Value
            const valEl = document.createElement('div');
            valEl.className = `infra-value ${valColor}`;
            valEl.textContent = value;

            content.appendChild(label);
            content.appendChild(valEl);

            card.appendChild(badge);
            card.appendChild(content);

            infraContainer.appendChild(card);
        });

        // Add Footer
        const footer = document.createElement('div');
        footer.className = 'infra-footer';
        footer.textContent = 'Indicators are based on available spatial and contextual datasets. Availability may vary over time.';
        infraContainer.appendChild(footer);
    }

    function renderWarningBanner(assessment) {
        warningBannerContainer.classList.remove('hidden');
        constraintReasons.innerHTML = ''; // Clear previous reasons

        const bannerDiv = warningBannerContainer.querySelector('.warning-banner');

        if (assessment.status === 'high_constraint') {
            // Restore High Risk HTML (Red)
            bannerDiv.style.backgroundColor = '#ffe6e6';
            bannerDiv.style.border = '1px solid #ff4d4d';
            bannerDiv.innerHTML = `
                <div style="font-size: 24px;">⚠️</div>
                <div>
                    <h3 style="margin: 0 0 4px 0; color: #cc0000; font-size: 16px; font-weight: 700;">High-Risk Location Identified</h3>
                    <p style="margin: 0; color: #990000; font-size: 14px;">This location shows multiple critical environmental or disaster-related constraints.</p>
                    <p style="margin: 8px 0 0 0; font-size: 12px; color: #666;">This assessment is based on available historical and spatial data. It does not predict future events and should be used for awareness only.</p>
                </div>
            `;

            // Add reasons list
            const list = document.createElement('ul');
            list.style.fontSize = "13px";
            list.style.color = "#cc0000";
            list.style.paddingLeft = "20px";
            list.style.marginTop = "8px";

            assessment.reason.forEach(r => {
                const li = document.createElement('li');
                li.textContent = r;
                list.appendChild(li);
            });
            constraintReasons.appendChild(list);

        } else if (assessment.status === 'normal_context') {
            // Set Safe HTML (Green)
            bannerDiv.style.backgroundColor = '#ECFDF5'; // Green 50
            bannerDiv.style.border = '1px solid #6EE7B7'; // Green 300
            bannerDiv.innerHTML = `
                <div style="font-size: 24px;">✅</div>
                <div>
                    <h3 style="margin: 0 0 4px 0; color: #065F46; font-size: 16px; font-weight: 700;">Low Constraint Zone</h3>
                    <p style="margin: 0; color: #064E3B; font-size: 14px;">No significant critical environmental constraints detected in this sector.</p>
                    <p style="margin: 8px 0 0 0; font-size: 12px; color: #666;">Based on available spatial context. Suitable for general development subject to local regulations.</p>
                </div>
            `;
        } else {
            // Fallback if generic status, though we usually only have high vs normal
            warningBannerContainer.classList.add('hidden');
            return;
        }

        // Scroll to top to ensure user sees the banner
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});
