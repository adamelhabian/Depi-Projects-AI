import { applyOperation, requireRule, validateWorkspace } from '../domain/workspace.js';

export function commitWorkspaceCommand(state, command, input, { role, actorId, idempotencyKey, expectedRevision, now, uuid, contentOperation }) {
  const key = actorId ? `${actorId}:${idempotencyKey}` : idempotencyKey;
  const fingerprint = JSON.stringify({ command, input, role });
  const previous = Object.hasOwn(state.idempotency, key) && state.idempotency[key];
  if (previous) {
    requireRule(previous.fingerprint === fingerprint, 'IDEMPOTENCY_CONFLICT');
    return state;
  }
  requireRule(idempotencyKey && expectedRevision === state.revision, 'CONFLICT');
  const context = { role, actorId, id: uuid(), now: now() };
  const operation = command.startsWith('content.') || command.startsWith('automation.') ? contentOperation : applyOperation;
  const next = operation(state, command, input, context);
  next.revision++;
  next.updatedAt = context.now;
  next.idempotency[key] = { fingerprint, at: context.now };
  return validateWorkspace(next);
}
