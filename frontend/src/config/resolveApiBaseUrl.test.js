import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { resolveApiBaseUrl } from './resolveApiBaseUrl.js';

describe('resolveApiBaseUrl', () => {
  it('uses the configured API URL when provided', () => {
    assert.equal(
      resolveApiBaseUrl('https://api.example.test/api', '192.168.1.25'),
      'https://api.example.test/api',
    );
  });

  it('replaces a configured loopback host with the current page hostname', () => {
    assert.equal(
      resolveApiBaseUrl('http://127.0.0.1:8000/api', '192.168.1.25'),
      'http://192.168.1.25:8000/api',
    );
  });

  it('uses the current page hostname for LAN access by default', () => {
    assert.equal(
      resolveApiBaseUrl('', '192.168.1.25'),
      'http://192.168.1.25:8000/api',
    );
  });

  it('brackets an IPv6 hostname in the fallback URL', () => {
    assert.equal(
      resolveApiBaseUrl(undefined, '2001:db8::1'),
      'http://[2001:db8::1]:8000/api',
    );
  });
});
