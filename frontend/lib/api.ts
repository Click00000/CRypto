const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}/api/v1${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Include cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// Auth
export async function requestMagicLink(email: string, marketingOptIn: boolean = false) {
  return apiRequest('/auth/request-link', {
    method: 'POST',
    body: JSON.stringify({ email, marketing_opt_in: marketingOptIn }),
  });
}

export async function consumeMagicLink(token: string) {
  return apiRequest('/auth/consume-link', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
}

export async function logout() {
  return apiRequest('/auth/logout', {
    method: 'POST',
  });
}

export async function getCurrentUser() {
  return apiRequest('/me');
}

// Exchanges
export async function getExchanges() {
  return apiRequest('/exchanges');
}

export async function getExchangeFlows(exchangeId: string, params?: {
  asset?: string;
  window?: string;
  from?: string;
  to?: string;
}) {
  const query = new URLSearchParams();
  if (params?.asset) query.append('asset', params.asset);
  if (params?.window) query.append('window', params.window);
  if (params?.from) query.append('from', params.from);
  if (params?.to) query.append('to', params.to);
  
  return apiRequest(`/exchanges/${exchangeId}/flows?${query.toString()}`);
}

// Alerts
export async function getLiveAlerts() {
  return apiRequest('/alerts/live');
}

// Admin
export async function adminGetExchanges() {
  return apiRequest('/admin/exchanges');
}

export async function adminCreateExchange(data: { name: string; slug: string }) {
  return apiRequest('/admin/exchanges', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function adminUpdateExchange(exchangeId: string, data: { name?: string; slug?: string }) {
  return apiRequest(`/admin/exchanges/${exchangeId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function adminGetAddresses(params?: {
  exchange_id?: string;
  chain?: string;
  is_active?: boolean;
}) {
  const query = new URLSearchParams();
  if (params?.exchange_id) query.append('exchange_id', params.exchange_id);
  if (params?.chain) query.append('chain', params.chain);
  if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
  
  return apiRequest(`/admin/addresses?${query.toString()}`);
}

export async function adminCreateAddress(data: {
  exchange_id: string;
  chain: string;
  address: string;
  label: string;
  cluster_id?: string;
  is_active?: boolean;
  notes?: string;
}) {
  return apiRequest('/admin/addresses', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function adminUpdateAddress(addressId: string, data: {
  label?: string;
  cluster_id?: string;
  is_active?: boolean;
  notes?: string;
}) {
  return apiRequest(`/admin/addresses/${addressId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function adminGetSyncState() {
  return apiRequest('/admin/sync-state');
}

export async function adminTriggerResync() {
  return apiRequest('/admin/jobs/resync', {
    method: 'POST',
  });
}
