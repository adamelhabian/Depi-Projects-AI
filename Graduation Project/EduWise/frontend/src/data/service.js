import { DomainError, projectWorkspace, validateWorkspace } from '../domain/workspace.js';
import { examBank } from './mockData.js';
import { commitWorkspaceCommand } from './commands.js';
import { openPersistence, STORAGE_KEY } from './persistence.js';

// Browser-only persistence for the explicitly selected demo.
export function createDemoService({ storage, now = () => new Date().toISOString(), uuid = () => crypto.randomUUID(), contentOperation } = {}) {
  let opened = openPersistence(storage, now()), state = opened.state, failNext = false;
  let queue = Promise.resolve();
  return {
    mode: 'demo',
    async read(role, { signal } = {}) {
      await Promise.resolve(); signal?.throwIfAborted();
      let raw; try { raw = storage.getItem(STORAGE_KEY); } catch { throw new DomainError('STORAGE'); }
      if (raw && !opened.readOnly) { try { state = validateWorkspace(JSON.parse(raw)); } catch { throw new DomainError('CORRUPT'); } }
      signal?.throwIfAborted();
      return { data: structuredClone(projectWorkspace(state, role)), notice: opened.notice, readOnly: opened.readOnly, questionBankCount: examBank.length };
    },
    failNextMutation() { failNext = true; },
    execute(command, input, { role, idempotencyKey, expectedRevision }) {
      const work = async () => {
        if (opened.readOnly) throw new DomainError(opened.notice || 'STORAGE');
        if (failNext) { failNext = false; throw new DomainError('REQUEST_FAILED'); }
        let persisted; try { persisted = validateWorkspace(JSON.parse(storage.getItem(STORAGE_KEY))); } catch { throw new DomainError('STORAGE'); }
        state = persisted;
        const next = commitWorkspaceCommand(state, command, input, { role, idempotencyKey, expectedRevision, now, uuid, contentOperation });
        if (next === state) return this.read(role);
        try { storage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch { throw new DomainError('STORAGE'); }
        state = next;
        return this.read(role);
      };
      const result = queue.then(work); queue = result.catch(() => {}); return result;
    },
  };
}
