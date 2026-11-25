export function resolveApiBaseUrl(configuredUrl, hostname) {
  if (configuredUrl) {
    const apiUrl = new URL(configuredUrl);
    if (['localhost', '127.0.0.1', '[::1]'].includes(apiUrl.hostname)) {
      apiUrl.hostname = hostname;
    }
    return apiUrl.toString().replace(/\/$/, '');
  }

  const host = hostname.includes(':') && !hostname.startsWith('[')
    ? `[${hostname}]`
    : hostname;
  return `http://${host}:8000/api`;
}
