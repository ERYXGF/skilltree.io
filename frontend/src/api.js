/**
 * API Helper Module
 * Provides functions to interact with the backend SkillTree.io API
 */

/**
 * Analyze a GitHub repository
 * @param {string} url - The GitHub repository URL
 * @param {string|null} targetRole - Optional target role for personalized recommendations
 * @returns {Promise<Object>} - The analysis response matching AnalyzeResponse schema
 * @throws {Error} - Network or API errors
 */
export async function analyzeRepo(url, targetRole = null) {
  try {
    // Validate input
    if (!url || typeof url !== 'string') {
      throw new Error('Invalid repository URL provided');
    }

    // Build request body
    const requestBody = { repo_url: url };
    if (targetRole) {
      requestBody.target_role = targetRole;
    }

    // Make POST request to backend
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail ||
        errorData.message ||
        `HTTP ${response.status}: ${response.statusText}`
      );
    }

    // Parse and return JSON response
    const data = await response.json();

    // Validate response structure (basic check)
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid response format from server');
    }

    return data;

  } catch (error) {
    // Network errors (fetch failures)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: Unable to connect to the server. Please check your connection.');
    }

    // Re-throw other errors with context
    if (error.message) {
      throw error;
    }

    // Unknown errors
    throw new Error('An unexpected error occurred while analyzing the repository');
  }
}

/**
 * Health check endpoint
 * @returns {Promise<Object>} - Health status
 */
export async function checkHealth() {
  try {
    const response = await fetch('/health', {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Export default object with all API functions
 */
export default {
  analyzeRepo,
  checkHealth,
};
