import { verifyAccount } from './accounts.mjs';
import { DomainError, requireRule } from '../src/domain/workspace.js';

const sessionDuration = 8 * 60 * 60 * 1000;

function send(response, status, body, headers = {}) {
  response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', ...headers });
  response.end(JSON.stringify(body));
}

async function readBody(request) {
  requireRule(request.headers['content-type']?.split(';')[0].trim().toLowerCase() === 'application/json', 'JSON_REQUIRED');
  const maxBytes = 512 * 1024;
  requireRule(Number(request.headers['content-length'] ?? 0) <= maxBytes, 'PAYLOAD_TOO_LARGE');
  let size = 0;
  const chunks = [];
  for await (const chunk of request.iterator({ destroyOnReturn: false })) {
    size += chunk.length;
    if (size > maxBytes) {
      request.resume();
      throw new DomainError('PAYLOAD_TOO_LARGE');
    }
    chunks.push(chunk);
  }
  let body;
  try { body = JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { throw new DomainError('VALIDATION'); }
  requireRule(body && typeof body === 'object' && !Array.isArray(body));
  return body;
}

const statusCodes = {
  AUTH_REQUIRED: 401, INVALID_CREDENTIALS: 401, FORBIDDEN: 403, NOT_FOUND: 404,
  CONFLICT: 409, IDEMPOTENCY_CONFLICT: 409, PAYLOAD_TOO_LARGE: 413, JSON_REQUIRED: 415,
  TOO_MANY_ATTEMPTS: 429, CORRUPT: 500,
};

export function createHandler({ workspace, accounts, sessions, secure = false, origin = process.env.EDUFLOW_ORIGIN }) {
  let attempts = 0;
  let attemptsResetAt = 0;
  const cookie = (token, seconds) => `eduflow_session=${token}; Max-Age=${seconds}; Path=/api; HttpOnly; SameSite=Strict${secure ? '; Secure' : ''}`;

  async function handle(request, response) {
    const route = `${request.method} ${new URL(request.url, 'http://localhost').pathname}`;
    const { origin: requestOrigin, host, 'sec-fetch-site': fetchSite } = request.headers;
    const externalOrigin = origin || `${secure ? 'https' : 'http'}://${host}`;
    requireRule(fetchSite !== 'cross-site' && (!requestOrigin || requestOrigin === externalOrigin), 'FORBIDDEN');
    const token = request.headers.cookie?.match(/(?:^|;\s*)eduflow_session=([a-f0-9]{64}(?:[a-f0-9]{64})?)(?=;|$)/)?.[1];
    const now = Date.now();

    if (route === 'POST /api/session') {
      if (now >= attemptsResetAt) {
        attemptsResetAt = now + 60_000;
        attempts = 0;
      }
      requireRule(attempts < 15, 'TOO_MANY_ATTEMPTS');
      attempts++;
      const { email, password } = await readBody(request);
      requireRule(typeof email === 'string' && email.length <= 254 && typeof password === 'string' && password.length <= 256, 'INVALID_CREDENTIALS');
      const account = await verifyAccount(accounts, email, password);
      const identity = account && await workspace.getUser(account.id);
      requireRule(identity, 'INVALID_CREDENTIALS');
      if (token) await sessions.delete(token);
      const newToken = await sessions.create({ userId: identity.id, expiresAt: now + sessionDuration });
      return send(response, 200, { user: identity }, { 'Set-Cookie': cookie(newToken, sessionDuration / 1000) });
    }
    if (route === 'DELETE /api/session') {
      if (token) await sessions.delete(token);
      return send(response, 200, {}, { 'Set-Cookie': cookie('', 0) });
    }
    const session = token && await sessions.get(token);
    const user = session?.expiresAt > now ? await workspace.getUser(session.userId) : undefined;
    if (route === 'GET /api/session') {
      requireRule(user, 'AUTH_REQUIRED');
      return send(response, 200, { user });
    }
    if (route === 'GET /api/workspace') {
      requireRule(user, 'AUTH_REQUIRED');
      requireAccountMatch(request, user);
      return send(response, 200, await workspace.read(user));
    }
    if (route === 'POST /api/workspace/commands') {
      requireRule(user, 'AUTH_REQUIRED');
      requireAccountMatch(request, user);
      const { command, input, expectedRevision } = await readBody(request);
      const idempotencyKey = request.headers['idempotency-key'];
      requireRule(typeof command === 'string' && input && typeof input === 'object' && !Array.isArray(input));
      requireRule(Number.isSafeInteger(expectedRevision) && expectedRevision >= 0);
      requireRule(typeof idempotencyKey === 'string' && /^[\w-]{1,100}$/.test(idempotencyKey));
      const result = await workspace.execute(user, command, input, { expectedRevision, idempotencyKey });
      return send(response, 200, result);
    }
    send(response, 404, { error: { code: 'NOT_FOUND' } });
  }

  return async (request, response) => {
    try { await handle(request, response); }
    catch (error) {
      const code = error instanceof DomainError ? error.code : 'API_UNAVAILABLE';
      const status = statusCodes[code] ?? (error instanceof DomainError ? 422 : 500);
      if (status >= 500) console.error(error);
      send(response, status, { error: { code } });
    }
  };
}

function requireAccountMatch(request, user) {
  const expected = request.headers['x-workspace-account'];
  requireRule(!expected || expected === user.id, 'AUTH_REQUIRED');
}
