import { randomUUID } from 'node:crypto';
import { readFile, rename, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { commitWorkspaceCommand } from '../src/data/commands.js';
import { examBank } from '../src/data/mockData.js';
import { applyContent } from '../src/domain/content.js';
import { can, createWorkspace, projectWorkspace, resolveActor, validateWorkspace } from '../src/domain/workspace.js';
import { dataDir } from './accounts.mjs';

const now = () => new Date().toISOString();
const workspaceFile = join(dataDir, 'workspace.json');

export function freshWorkspace() {
  const state = createWorkspace(now(), { sample: false });
  const names = {
    admin: ['Center Administrator', 'مدير السنتر'],
    teacher: ['Center Teacher', 'مدرّس السنتر'],
    secretary: ['Center Secretary', 'سكرتارية السنتر'],
  };
  for (const user of state.users) user.name = names[user.role];
  return validateWorkspace(state);
}

export function workspaceUser(state, id) {
  const user = state.users.find(entry => entry.id === id);
  return user && resolveActor(state, user.role, id);
}

export function workspaceResponse(state, user) {
  const { idempotency, legacy, ...data } = projectWorkspace(state, user.role, user.id);
  if (user.role === 'secretary') data.audit = data.audit.filter(entry => entry.actorId === user.id);
  return { data, questionBankCount: can(user.role, 'studio') ? examBank.length : 0, notice: null, readOnly: false };
}

export function applyWorkspaceCommand(state, user, command, input, { idempotencyKey, expectedRevision }) {
  return commitWorkspaceCommand(state, command, input, {
    actorId: user.id, role: user.role, idempotencyKey, expectedRevision,
    now, uuid: randomUUID, contentOperation: applyContent,
  });
}

async function writeWorkspace(state) {
  const temporary = join(dataDir, `workspace-${randomUUID()}.tmp`);
  try {
    await writeFile(temporary, JSON.stringify(state), { flag: 'wx', mode: 0o600 });
    await rename(temporary, workspaceFile);
  } finally {
    await rm(temporary, { force: true });
  }
}

export async function openWorkspace() {
  let state;
  try {
    state = validateWorkspace(JSON.parse(await readFile(workspaceFile, 'utf8')));
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    state = freshWorkspace();
    await writeWorkspace(state);
  }
  let queue = Promise.resolve();
  return {
    getUser: id => workspaceUser(state, id),
    read: user => workspaceResponse(state, user),
    execute(user, command, input, options) {
      const work = queue.then(async () => {
        const next = applyWorkspaceCommand(state, user, command, input, options);
        if (next !== state) {
          await writeWorkspace(next);
          state = next;
        }
        return workspaceResponse(state, user);
      });
      queue = work.catch(() => {});
      return work;
    },
  };
}
