// API configuration that works for both local and production environments.
// Local dev: falls back to http://localhost:8000.
// Production (Vercel): set NEXT_PUBLIC_API_URL to your API Gateway URL.
export const getApiUrl = () => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl && envUrl.length > 0) {
    return envUrl.replace(/\/$/, '');
  }

  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }

  return '';
};

export const API_URL = getApiUrl();
