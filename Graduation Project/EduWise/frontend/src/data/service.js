import { applyOperation, DomainError, projectWorkspace, validateWorkspace } from '../domain/workspace.js';
import { openPersistence, STORAGE_KEY } from './persistence.js';

// Same asynchronous Interface for reads and atomic commands; no unconfirmed HTTP implementation.
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
      return { data: structuredClone(projectWorkspace(state, role)), notice: opened.notice, readOnly: opened.readOnly };
    },
    failNextMutation() { failNext = true; },
    execute(command, input, { role, idempotencyKey, expectedRevision }) {
      const work = async () => {
        if (opened.readOnly) throw new DomainError(opened.notice || 'STORAGE');
        if (failNext) { failNext = false; throw new DomainError('REQUEST_FAILED'); }
        let persisted; try { persisted = validateWorkspace(JSON.parse(storage.getItem(STORAGE_KEY))); } catch { throw new DomainError('STORAGE'); }
        state = persisted;
        const fingerprint = JSON.stringify({ command, input, role });
        const previous = Object.hasOwn(state.idempotency, idempotencyKey) && state.idempotency[idempotencyKey];
        if (previous) { if (previous.fingerprint !== fingerprint) throw new DomainError('IDEMPOTENCY_CONFLICT'); return this.read(role); }
        if (!idempotencyKey || expectedRevision !== state.revision) throw new DomainError('CONFLICT');
        const context = { role, id: uuid(), now: now() };
        const next = command.startsWith('content.') || command.startsWith('automation.') ? contentOperation(state, command, input, context) : applyOperation(state, command, input, context);
        next.revision++; next.updatedAt = context.now;
        next.idempotency[idempotencyKey] = { fingerprint, at: context.now };
        validateWorkspace(next);
        try { storage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch { throw new DomainError('STORAGE'); }
        state = next;
        return this.read(role);
      };
      const result = queue.then(work); queue = result.catch(() => {}); return result;
    },
  };
}
