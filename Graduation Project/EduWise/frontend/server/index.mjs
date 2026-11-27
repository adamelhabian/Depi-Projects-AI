import { randomBytes } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { accountFile } from './accounts.mjs';
import { openWorkspace } from './workspace.mjs';
import { createHandler } from './http.mjs';

const accounts = await readFile(accountFile, 'utf8').then(JSON.parse).catch(error => {
  if (error.code === 'ENOENT') throw new Error('Run npm run accounts:setup before starting the API.');
  throw error;
});
const workspace = await openWorkspace();
const port = Number(process.env.EDUFLOW_API_PORT || 8787);
const sessions = new Map();
const handler = createHandler({
  accounts, workspace, secure: process.env.EDUFLOW_SECURE_COOKIE === '1',
  sessions: {
    get: token => sessions.get(token),
    delete: token => sessions.delete(token),
    create(session) {
      for (const [key, saved] of sessions) if (saved.expiresAt <= Date.now()) sessions.delete(key);
      const token = randomBytes(32).toString('hex');
      sessions.set(token, session);
      return token;
    },
  },
});
const server = createServer(handler);
server.listen(port, '127.0.0.1', () => {
  console.log(`EduFlow API listening at http://127.0.0.1:${server.address().port}/api`);
});
