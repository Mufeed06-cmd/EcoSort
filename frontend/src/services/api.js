/**
 * API service for communicating with the AI Waste Segregation Advisor backend.
 */

const API_ENDPOINT = import.meta.env.VITE_API_URL || 'http://localhost:5001/analyze';

/**
 * Analyzes waste through POST /analyze endpoint.
 *
 * @param {Object} params
 * @param {string} [params.text] - Waste text description
 * @param {string} [params.image] - Base64 encoded image string (or data URI)
 * @param {boolean} [params.forceMock] - Whether to force backend mock mode
 * @returns {Promise<Object>} Analysis response
 */
export async function analyzeWaste({ text, image, forceMock = false }) {
  if (!text && !image) {
    throw new Error('Please enter a waste description or upload a photo.');
  }

  const payload = {
    text: text?.trim() || '',
    image: image || '',
    mock: Boolean(forceMock),
  };

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); // 20s timeout

    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.message || `Server returned ${response.status}: ${response.statusText}`;
      const error = new Error(errorMsg);
      error.status = response.status;
      error.errorType = data?.error_type || 'ApiError';
      throw error;
    }

    if (!data) {
      throw new Error('Received empty response from waste advisor server.');
    }

    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please check your network connection and try again.');
    }

    // If fetch failed completely (e.g. backend server not started), format descriptive error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const connectionError = new Error(
        `Unable to reach backend at ${API_ENDPOINT}. Ensure local backend server is running (python3 -m backend.local_server).`
      );
      connectionError.isConnectionError = true;
      throw connectionError;
    }

    throw error;
  }
}
