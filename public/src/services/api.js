// API service - handles all backend communication
// Follows the master blueprint by including Firebase ID token in every request

const BACKEND_URL = process.env.NODE_ENV === 'production' 
  ? 'https://us-central1-raphael-great-sage.cloudfunctions.net/main'
  : 'http://localhost:5001/raphael-great-sage/us-central1/main';

/**
 * Send a message to the Raphael AI backend
 * @param {string} message - The user's message
 * @param {string} idToken - Firebase ID token for authentication
 * @returns {Promise<Object>} - The response from the backend
 */
export const sendMessageToRaphael = async (message, idToken) => {
  try {
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        idToken: idToken  // Required by auth middleware
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

/**
 * Get user data from the backend
 * @param {string} idToken - Firebase ID token for authentication
 * @returns {Promise<Object>} - The user's personal data summary
 */
export const getUserDataSummary = async (idToken) => {
  try {
    const response = await fetch(`${BACKEND_URL}/user-data`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};
