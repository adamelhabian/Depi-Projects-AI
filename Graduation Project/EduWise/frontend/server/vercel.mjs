import { createHmac, randomBytes, timingSafeEqual } from 'node:crypto';
import { BlobPreconditionFailedError, del, get, head, put } from '@vercel/blob';
import { DomainError, validateWorkspace } from '../src/domain/workspace.js';
import { createHandler } from './http.mjs';
import { applyWorkspaceCommand, freshWorkspace, workspaceResponse, workspaceUser } from './workspace.mjs';

const production = process.env.VERCEL_ENV !== 'preview';
const prefix = production ? 'production' : 'preview';
const workspacePath = `${prefix}/workspace.json`;
const initialUsers = freshWorkspace();
const privateAccess = { access: 'private' };
const jsonOptions = { ...privateAccess, contentType: 'application/json', addRandomSuffix: false };

async function readBlob(path) {
  const blob = await get(path, { ...privateAccess, useCache: false, headers: { 'Accept-Encoding': 'identity' } });
  if (!blob) return null;
  return { etag: blob.blob.etag, data: await new Response(blob.stream).json() };
}

async function loadWorkspace() {
  const saved = await readBlob(workspacePath);
  if (saved) return { ...saved, data: validateWorkspace(saved.data) };
  const data = freshWorkspace();
  try {
    const written = await put(workspacePath, JSON.stringify(data), jsonOptions);
    return { etag: written.etag, data };
  } catch (error) {
    // Another instance may have initialized the workspace in the meantime.
    const created = await readBlob(workspacePath);
    if (!created) throw error;
    return { ...created, data: validateWorkspace(created.data) };
  }
}

const workspace = {
  // Roles and actor IDs are fixed for the three provisioned accounts.
  getUser: id => workspaceUser(initialUsers, id),
  async read(user) {
    const { data } = await loadWorkspace();
    return workspaceResponse(data, user);
  },
  async execute(user, command, input, options) {
    for (let attempt = 0; attempt < 2; attempt++) {
      const { etag, data } = await loadWorkspace();
      const next = applyWorkspaceCommand(data, user, command, input, options);
      if (next === data) return workspaceResponse(next, user);
      const current = await head(workspacePath);
      // CDN responses can quote the tag or mark the representation weak.
      // Only use the storage API's exact tag after matching it to the body we read.
      if (!etag || normalizeEtag(etag) !== normalizeEtag(current.etag)) continue;
      try {
        await put(workspacePath, JSON.stringify(next), { ...jsonOptions, allowOverwrite: true, ifMatch: current.etag });
        return workspaceResponse(next, user);
      } catch (error) {
        if (!(error instanceof BlobPreconditionFailedError)) throw error;
      }
    }
    throw new DomainError('CONFLICT');
  },
};

function normalizeEtag(value) {
  return value?.replace(/^W\//i, '').replace(/^"|"$/g, '');
}

function blobSessions(secret) {
  const sign = id => createHmac('sha256', secret).update(`${prefix}:${id}`).digest('hex');
  const pathFor = id => `${prefix}/sessions/${id}.json`;
  const verify = token => token.length === 128 && timingSafeEqual(
    Buffer.from(token.slice(64), 'hex'), Buffer.from(sign(token.slice(0, 64)), 'hex'),
  );
  return {
    async create(session) {
      const id = randomBytes(32).toString('hex');
      await put(pathFor(id), JSON.stringify(session), { ...jsonOptions, ttlDays: 1 });
      return id + sign(id);
    },
    async get(token) {
      return verify(token) ? (await readBlob(pathFor(token.slice(0, 64))))?.data : undefined;
    },
    async delete(token) {
      if (verify(token)) await del(pathFor(token.slice(0, 64)));
    },
  };
}

let handler;
export default function vercelHandler(request, response) {
  if (!handler) {
    const config = process.env.EDUFLOW_AUTH;
    if (!config || !(process.env.BLOB_STORE_ID || process.env.BLOB_READ_WRITE_TOKEN)) {
      response.writeHead(503, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
      response.end(JSON.stringify({ error: { code: 'API_UNAVAILABLE' } }));
      return;
    }
    const { accounts, sessionSecret } = JSON.parse(config);
    handler = createHandler({ workspace, accounts, sessions: blobSessions(sessionSecret), secure: true });
  }
  return handler(request, response);
}
