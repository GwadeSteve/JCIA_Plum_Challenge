const API_BASE_URL = 'http://localhost:8000';

export const predictImage = async(imageFile) => {
    try {
        //console.log('Original image file being sent:', imageFile);
        //console.log('File type:', imageFile.type);
        //console.log('File size (bytes):', imageFile.size);

        const formData = new FormData();
        formData.append('file', imageFile);

        const response = await fetch(`${API_BASE_URL}/api/predict`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to predict image');
        }

        const result = await response.json();
        //console.log('Prediction result:', result);
        return result;
    } catch (error) {
        console.error('Prediction error:', error);
        throw error;
    }
};

export const getPredictions = async(sessionId = null, limit = 100) => {
    try {
        let url = `${API_BASE_URL}/api/predictions?limit=${limit}`;
        if (sessionId) {
            url += `&session_id=${sessionId}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch predictions');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching predictions:', error);
        throw error;
    }
};

export const connectToStreamSession = () => {
    try {
        const websocket = new WebSocket(`ws://${API_BASE_URL.replace('http://', '')}/ws/stream`);
        return websocket;
    } catch (error) {
        console.error('Error connecting to stream session:', error);
        throw error;
    }
};