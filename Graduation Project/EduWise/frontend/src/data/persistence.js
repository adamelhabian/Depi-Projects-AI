import { createWorkspace, validateWorkspace, SCHEMA } from '../domain/workspace.js';

export const STORAGE_KEY = 'eduflow.workspace.v3';
const legacyKeys = ['students', 'materials', 'flows', 'drafts', 'payments', 'exams'];
export function migrateLegacy(legacy, now) {
  const s = createWorkspace(now); const source = legacy.students;
  if (source) {
    if (!Array.isArray(source) || source.some(x => typeof x.id !== 'string' || !Array.isArray(x.name) || !Number.isInteger(x.group))) throw new Error('legacy-students');
    s.students = source.map((x, i) => ({ id: `student-${i + 1}`, centerId: 'nile', code: x.id, name: x.name, phone: x.phone || '', status: 'active', legacyObservation: { attendance: x.attendance, score: x.score, paymentLabel: x.payment, presentUnscoped: x.present } }));
    s.enrollments = source.map((x, i) => ({ id: `enrollment-${i + 1}`, studentId: `student-${i + 1}`, groupId: `group-${x.group + 1}`, startDate: '2020-01-01', endDate: null, status: 'active' }));
  }
  // A paid/due flag is not a receipt; an unscoped boolean is not session attendance.
  // Preserve both verbatim, but never invent dates, money or attendance events.
  s.charges = []; s.payments = []; s.allocations = [];
  for (const [i, payment] of (legacy.payments || []).entries()) {
    const student = s.students.find(x => x.code === payment.studentId);
    if (!student || !Number.isFinite(Number(payment.amount)) || Number(payment.amount) <= 0) continue;
    const minor = Math.round(Number(payment.amount) * 100), id = `legacy-payment-${i}`;
    // An opening receipt-backed charge reconciles only that receipt, not a subscription.
    s.charges.push({ id: `${id}-charge`, studentId: student.id, centerId: 'nile', description: ['Imported receipt opening balance', 'رصيد افتتاحي مقابل إيصال مستورد'], grossMinor: minor, discountMinor: 0, discountReason: '', currency: 'EGP', dueDate: String(payment.date || now).slice(0, 10), createdAt: now, createdBy: 'user-admin', origin: 'legacy-reconciliation' });
    s.payments.push({ id, studentId: student.id, centerId: 'nile', amountMinor: minor, currency: 'EGP', reference: `IMPORT-${i}-${payment.reference || 'NOREF'}`, originalReference: payment.reference || '', method: payment.method || 'cash', createdAt: payment.date || now, createdBy: 'user-admin', origin: 'legacy-reconciliation' });
    s.allocations.push({ id: `${id}-allocation`, paymentId: id, chargeId: `${id}-charge`, amountMinor: minor });
  }
  if (Array.isArray(legacy.materials)) s.materials = legacy.materials.map(m => ({ ...m, status: m.source === 'sample' ? 'ready' : 'failed', storage: m.source === 'sample' ? 'demo-bank' : 'metadata-only', failure: m.source === 'sample' ? null : 'INDEXING_UNAVAILABLE', subject: 'physics', grade: m.id === 'm3' ? '11' : '12', topic: m.id, citationType: 'demo', createdAt: now }));
  if (Array.isArray(legacy.flows)) for (const f of s.workflows) f.enabled = Boolean(legacy.flows.find(x => x.id === f.id)?.enabled);
  s.legacy = { importedAt: now, data: legacy, note: 'Unscoped attendance, old AI drafts and risk labels are retained here, not promoted to verified operational records.' };
  return validateWorkspace(s);
}
export function openPersistence(storage, now = new Date().toISOString()) {
  let raw;
  try {
    raw = storage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed.schemaVersion > SCHEMA) return { state: createWorkspace(now), notice: 'FUTURE_VERSION', readOnly: true };
      return { state: validateWorkspace(parsed), notice: parsed.legacy ? 'MIGRATED' : null, readOnly: false };
    }
    const legacy = {};
    for (const key of legacyKeys) { const value = storage.getItem(`eduflow.${key}.v1`); if (value !== null) legacy[key] = JSON.parse(value); }
    const migrated = Object.keys(legacy).length > 0;
    const state = migrated ? migrateLegacy(legacy, now) : createWorkspace(now);
    storage.setItem(STORAGE_KEY, JSON.stringify(state));
    return { state, notice: migrated ? 'MIGRATED' : null, readOnly: false };
  } catch {
    // Keep every original key untouched. A timestamped backup is required before recovery.
    try {
      const backup = raw || JSON.stringify(Object.fromEntries(legacyKeys.map(k => [k, storage.getItem(`eduflow.${k}.v1`)])));
      storage.setItem(`eduflow.recovery.${now}`, backup);
      const state = createWorkspace(now); storage.setItem(STORAGE_KEY, JSON.stringify(state));
      return { state, notice: 'RECOVERED', readOnly: false };
    } catch { return { state: createWorkspace(now), notice: 'STORAGE', readOnly: true }; }
  }
}
