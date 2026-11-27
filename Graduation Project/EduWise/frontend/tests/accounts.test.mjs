import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { setupAccounts } from '../server/accounts.mjs';

test('account sessions protect JSON workspace reads, permissions and persisted commands', { timeout: 15_000 }, async t => {
  const directory = await mkdtemp(join(tmpdir(), 'eduflow-test-'));
  let server;
  let exited;
  t.after(async () => {
    if (server) { server.kill(); await exited; }
    await rm(directory, { recursive: true, force: true });
  });
  const credentials = await setupAccounts(directory);
  await assert.rejects(setupAccounts(directory), { code: 'EEXIST' });
  const accounts = await readFile(join(directory, 'accounts.json'), 'utf8');
  assert.ok(credentials.every(({ password }) => !accounts.includes(password)));

  server = spawn(process.execPath, [fileURLToPath(new URL('../server/index.mjs', import.meta.url))], {
    env: { ...process.env, EDUFLOW_DATA_DIR: directory, EDUFLOW_API_PORT: '0', EDUFLOW_SECURE_COOKIE: '0' },
    stdio: ['ignore', 'pipe', 'inherit'],
  });
  exited = once(server, 'exit');
  const [output] = await Promise.race([
    once(server.stdout, 'data'),
    exited.then(([code]) => { throw new Error(`Server exited during startup with code ${code}`); }),
  ]);
  const base = String(output).match(/http:\/\/127\.0\.0\.1:\d+\/api/)?.[0];
  assert.ok(base, 'server reported its listening address');

  function request(path, { method = 'GET', body, cookie, headers = {} } = {}) {
    return fetch(base + path, {
      method,
      headers: { ...headers, ...(cookie && { Cookie: cookie }), ...(body && { 'Content-Type': 'application/json' }) },
      body: body && JSON.stringify(body),
    });
  }
  async function login(role) {
    const { email, password } = credentials.find(entry => entry.id === `user-${role}`);
    const response = await request('/session', { method: 'POST', body: { email, password } });
    assert.equal(response.status, 200);
    assert.equal((await response.json()).user.role, role);
    const cookie = response.headers.get('set-cookie');
    assert.match(cookie, /HttpOnly; SameSite=Strict/);
    return cookie.split(';')[0];
  }
  assert.equal((await request('/workspace')).status, 401);
  const invalid = await request('/session', { method: 'POST', body: { email: credentials[0].email, password: 'wrong' } });
  assert.equal(invalid.status, 401);
  assert.equal((await invalid.json()).error.code, 'INVALID_CREDENTIALS');

  const admin = await login('admin');
  const before = await request('/workspace', { cookie: admin }).then(response => response.json());
  assert.deepEqual(before.data.students, []);
  assert.equal(before.data.idempotency, undefined);

  const body = { command: 'student.save', input: { code: 'API-1', nameEn: 'Test Student', nameAr: 'طالب اختبار' }, expectedRevision: before.data.revision };
  const submit = (cookie, key = 'create-one') => request('/workspace/commands', { method: 'POST', body, cookie, headers: { 'Idempotency-Key': key } });
  const teacher = await login('teacher');
  assert.equal((await submit(teacher)).status, 403);
  assert.equal((await request('/workspace', { cookie: teacher, headers: { 'X-Workspace-Account': 'user-admin' } })).status, 401);
  const teacherData = await request('/workspace', { cookie: teacher }).then(response => response.json());
  assert.deepEqual(teacherData.data.groups.map(group => group.id), ['group-1', 'group-2']);
  assert.deepEqual(teacherData.data.payments, []);
  const secretary = await login('secretary');
  const secretaryData = await request('/workspace', { cookie: secretary }).then(response => response.json());
  assert.equal(secretaryData.questionBankCount, 0);
  assert.deepEqual(secretaryData.data.materials, []);

  assert.equal((await submit(admin)).status, 200);
  assert.equal((await submit(admin)).status, 200);
  assert.equal((await submit(admin, 'stale-revision')).status, 409);
  const saved = JSON.parse(await readFile(join(directory, 'workspace.json'), 'utf8'));
  assert.equal(saved.students.length, 1);
  assert.equal(saved.students[0].code, 'API-1');
  assert.equal(saved.audit.at(-1).actorId, 'user-admin');
  assert.equal((await request('/session', { method: 'DELETE', cookie: admin })).status, 200);
  assert.equal((await request('/workspace', { cookie: admin })).status, 401);
});
