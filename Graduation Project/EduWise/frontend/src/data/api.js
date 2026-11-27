import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
  timeout: 10_000,
  headers: { Accept: 'application/json' },
  responseType: 'json',
  transitional: { silentJSONParsing: false },
});

async function request(config) {
  try {
    return (await client.request(config)).data;
  } catch (error) {
    if (axios.isCancel(error)) throw error;
    const code = error.response?.data?.error?.code
      || (error.response?.status === 401 ? 'AUTH_REQUIRED' : 'API_UNAVAILABLE');
    throw Object.assign(new Error(code), { code });
  }
}

const accountHeader = id => ({ 'X-Workspace-Account': id });
export const api = {
  session: signal => request({ method: 'get', url: '/session', signal }),
  login: (email, password) => request({ method: 'post', url: '/session', data: { email, password } }),
  logout: () => request({ method: 'delete', url: '/session' }),
  read: (role, { signal, actorId }) => request({
    method: 'get', url: '/workspace', signal, headers: accountHeader(actorId),
  }),
  execute: (command, input, { actorId, idempotencyKey, expectedRevision }) => request({
    method: 'post', url: '/workspace/commands',
    headers: { ...accountHeader(actorId), 'Idempotency-Key': idempotencyKey },
    data: { command, input, expectedRevision },
  }),
};
