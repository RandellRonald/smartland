// js/api.js

const API_BASE_URL = "http://127.0.0.1:8000";

async function analyzeLocation(lat, lon) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-location`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ latitude: lat, longitude: lon }),
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle expected errors (400)
            return {
                success: false,
                error: data
            };
        }

        return {
            success: true,
            data: data
        };

    } catch (error) {
        console.error("API Error:", error);
        return {
            success: false,
            error: { message: "Failed to connect to analysis server." }
        };
    }
}

async function fetchInfrastructureContext(lat, lon) {
    try {
        const response = await fetch(`${API_BASE_URL}/infrastructure-context?lat=${lat}&lon=${lon}`);
        const data = await response.json();

        if (!response.ok) {
            return {
                success: false,
                data: null
            };
        }

        return {
            success: true,
            data: data
        };
    } catch (e) {
        console.error("Infra API Error", e);
        return { success: false, data: null };
    }
}
