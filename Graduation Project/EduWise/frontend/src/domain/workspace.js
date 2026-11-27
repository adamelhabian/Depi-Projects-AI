import { studentsSeed, materialsSeed } from '../data/mockData.js';

export const SCHEMA = 3;
export const ROLES = ['admin', 'teacher', 'secretary'];
export const PERMISSIONS = {
  admin: ['overview', 'students', 'attendance', 'payments', 'materials', 'studio', 'automations', 'analytics', 'roster.write', 'attendance.write', 'finance.write', 'content.write', 'automation.write'],
  teacher: ['overview', 'students', 'attendance', 'materials', 'studio', 'automations', 'analytics', 'attendance.write', 'content.write', 'automation.write'],
  secretary: ['overview', 'students', 'attendance', 'payments', 'roster.write', 'attendance.write', 'finance.write'],
};
export const can = (role, permission) => PERMISSIONS[role]?.includes(permission) ?? false;
export class DomainError extends Error {
  constructor(code) { super(code); this.code = code; }
}
export const requireRule = (condition, code = 'VALIDATION') => { if (!condition) throw new DomainError(code); };
export const calendarDate = (instant = new Date()) => new Intl.DateTimeFormat('en-CA', { timeZone: 'Africa/Cairo', year: 'numeric', month: '2-digit', day: '2-digit' }).format(instant);
export function minorUnits(value) {
  const text = String(value).trim();
  requireRule(/^\d+(\.\d{1,2})?$/.test(text), 'MONEY');
  const [whole, fraction = ''] = text.split('.');
  const result = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
  requireRule(Number.isSafeInteger(result) && result <= 1_000_000_000, 'MONEY');
  return result;
}
export const normalized = value => String(value ?? '').normalize('NFKC').trim().toLocaleUpperCase('en');
const text = (value, max = 200) => { requireRule(typeof value === 'string' && value.trim().length > 0 && value.length <= max); return value.trim(); };
const validDate = value => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value)) && new Date(`${value}T12:00:00Z`).toISOString().startsWith(value);
export function createWorkspace(now = new Date().toISOString(), { sample = true } = {}) {
  const date = calendarDate(new Date(now));
  const students = sample ? studentsSeed.map((s, i) => ({ id: `student-${i + 1}`, centerId: 'nile', code: s.id, name: s.name, phone: '', status: 'active' })) : [];
  const groups = ['A', 'B', 'C'].map((letter, i) => ({ id: `group-${i + 1}`, centerId: 'nile', name: [`Physics · Group ${letter}`, `الفيزياء · مجموعة ${['أ', 'ب', 'ج'][i]}`], subject: 'physics', grade: '12', status: 'active', teacherId: i < 2 ? 'user-teacher' : null }));
  // These are explicit demonstration transactions, not historical observations.
  const charges = students.map(s => ({ id: `charge-${s.id}`, studentId: s.id, centerId: 'nile', description: ['Demo subscription', 'اشتراك توضيحي'], grossMinor: 90000, discountMinor: 0, discountReason: '', currency: 'EGP', dueDate: date, createdAt: now, createdBy: 'user-admin', origin: 'demo-seed' }));
  const payments = students.filter((_, i) => i % 4 !== 0).map(s => ({ id: `payment-${s.id}`, studentId: s.id, centerId: 'nile', amountMinor: 90000, currency: 'EGP', reference: `DEMO-${s.code}`, method: 'cash', createdAt: now, createdBy: 'user-admin', origin: 'demo-seed' }));
  return {
    schemaVersion: SCHEMA, revision: 0, updatedAt: now,
    center: { id: 'nile', name: ['Nile Learning Center', 'سنتر النيل التعليمي'], timezone: 'Africa/Cairo', currency: 'EGP' },
    users: ROLES.map(role => ({ id: `user-${role}`, centerId: 'nile', role, name: ['Youssef Mohamed', 'يوسف محمد'], groupIds: role === 'teacher' ? ['group-1', 'group-2'] : groups.map(g => g.id) })),
    students, groups,
    enrollments: students.map((s, i) => ({ id: `enrollment-${i + 1}`, studentId: s.id, groupId: `group-${i % 3 + 1}`, startDate: '2020-01-01', endDate: null, status: 'active' })),
    sessions: sample ? groups.map((g, i) => ({ id: `session-${i + 1}`, groupId: g.id, date, startTime: `${14 + i}:00`, title: ['Practice & discussion', 'تطبيق ومناقشة'], status: 'scheduled' })) : [],
    attendance: [], charges, payments,
    allocations: payments.map(p => ({ id: `allocation-${p.id}`, paymentId: p.id, chargeId: `charge-${p.studentId}`, amountMinor: p.amountMinor })), adjustments: [],
    materials: materialsSeed.map(m => ({ ...m, status: 'ready', storage: 'demo-bank', subject: 'physics', grade: m.id === 'm3' ? '11' : '12', topic: m.id, citationType: 'demo', createdAt: now })),
    jobs: [], drafts: [], automationRuns: [],
    workflows: ['absence', 'report'].map(id => ({ id, enabled: false, delivery: 'unavailable', scheduling: 'unavailable' })),
    audit: [], idempotency: {}, legacy: null,
  };
}
export function eligible(state, studentId, session) {
  return state.enrollments.some(e => e.studentId === studentId && e.groupId === session.groupId && e.startDate <= session.date && (!e.endDate || e.endDate >= session.date));
}
export function chargeBalance(state, charge) {
  const allocated = state.allocations.filter(a => a.chargeId === charge.id).reduce((sum, a) => {
    const payment = state.payments.find(p => p.id === a.paymentId);
    const reversed = state.adjustments.filter(x => x.paymentId === payment.id).reduce((n, x) => n + x.amountMinor, 0);
    // Payments currently allocate to exactly one charge; the proposed API allows many.
    return sum + Math.max(0, a.amountMinor - reversed);
  }, 0);
  return charge.grossMinor - charge.discountMinor - allocated;
}
export const outstanding = (state, studentId) => state.charges.filter(c => !studentId || c.studentId === studentId).reduce((n, c) => n + chargeBalance(state, c), 0);
export function projectWorkspace(state, role, actorId) {
  requireRule(can(role, 'overview'), 'FORBIDDEN');
  if (role === 'secretary') return { ...state, materials: [], jobs: [], drafts: [], automationRuns: [], workflows: [], idempotency: {} };
  if (role !== 'teacher') return state;
  const user = resolveActor(state, role, actorId);
  const groups = state.groups.filter(g => user.groupIds.includes(g.id));
  const enrollments = state.enrollments.filter(e => groups.some(g => g.id === e.groupId));
  const studentIds = new Set(enrollments.map(e => e.studentId));
  const sessions = state.sessions.filter(s => groups.some(g => g.id === s.groupId));
  return { ...state, groups, enrollments, students: state.students.filter(s => studentIds.has(s.id)), sessions,
    attendance: state.attendance.filter(a => sessions.some(s => s.id === a.sessionId)), charges: [], payments: [], allocations: [], adjustments: [],
    drafts: state.drafts.filter(d => d.createdBy === user.id), jobs: state.jobs.filter(j => j.createdBy === user.id),
    automationRuns: state.automationRuns.filter(r => r.createdBy === user.id), audit: state.audit.filter(a => a.actorId === user.id), legacy: null, idempotency: {},
  };
}
export function resolveActor(state, role, actorId) {
  const actor = state.users.find(u => u.role === role && (actorId === undefined || u.id === actorId));
  requireRule(actor?.centerId === state.center.id, 'FORBIDDEN');
  return actor;
}
const commands = {
  'student.save': 'roster.write', 'student.archive': 'roster.write', 'group.save': 'roster.write', 'group.archive': 'roster.write', 'enrollment.save': 'roster.write',
  'session.save': 'attendance.write', 'attendance.record': 'attendance.write', 'charge.create': 'finance.write', 'payment.record': 'finance.write', 'payment.adjust': 'finance.write',
};
export function applyOperation(current, command, input, context) {
  requireRule(can(context.role, commands[command]), 'FORBIDDEN');
  const state = structuredClone(current);
  const actor = resolveActor(state, context.role, context.actorId);
  const id = context.id, now = context.now;
  const student = () => { const s = state.students.find(s => s.id === input.studentId); requireRule(s, 'NOT_FOUND'); return s; };
  const groupAccess = groupId => { const g = state.groups.find(g => g.id === groupId); requireRule(g, 'NOT_FOUND'); requireRule(context.role !== 'teacher' || actor.groupIds.includes(groupId), 'FORBIDDEN'); return g; };
  if (command === 'student.save') {
    const code = normalized(text(input.code, 40));
    requireRule(!state.students.some(s => normalized(s.code) === code && s.id !== input.studentId), 'DUPLICATE_CODE');
    const name = [text(input.nameEn, 100), text(input.nameAr, 100)];
    const phone = String(input.phone ?? '').trim(); requireRule(!phone || /^\+?[\d ()-]{7,24}$/.test(phone), 'PHONE');
    const guardianPhone = String(input.guardianPhone ?? '').trim(); requireRule(!guardianPhone || /^\+?[\d ()-]{7,24}$/.test(guardianPhone), 'PHONE');
    const extra = { guardianName: String(input.guardianName ?? '').trim(), guardianPhone, grade: String(input.grade ?? '').trim(), notes: String(input.notes ?? '').trim() };
    requireRule(extra.guardianName.length <= 100 && extra.grade.length <= 100 && extra.notes.length <= 2000);
    if (input.studentId) Object.assign(student(), { code, name, phone, ...extra });
    else state.students.push({ id, centerId: state.center.id, code, name, phone, ...extra, status: 'active' });
  } else if (command === 'student.archive') {
    requireRule(text(input.reason, 400)); student().status = 'archived';
    for (const e of state.enrollments.filter(e => e.studentId === input.studentId && !e.endDate)) { e.endDate = calendarDate(new Date(now)); e.status = 'ended'; }
  } else if (command === 'group.save') {
    state.groups.push({ id, centerId: state.center.id, name: [text(input.nameEn), text(input.nameAr)], subject: text(input.subject), grade: text(input.grade), teacherId: null, status: 'active' });
  } else if (command === 'group.archive') {
    text(input.reason, 400); groupAccess(input.groupId).status = 'archived';
    for (const e of state.enrollments.filter(e => e.groupId === input.groupId && !e.endDate)) { e.endDate = calendarDate(new Date(now)); e.status = 'ended'; }
  } else if (command === 'enrollment.save') {
    requireRule(student().status === 'active', 'ARCHIVED');
    requireRule(groupAccess(input.groupId).status === 'active', 'ARCHIVED');
    requireRule(validDate(input.startDate) && (!input.endDate || (validDate(input.endDate) && input.endDate >= input.startDate)), 'DATE');
    requireRule(!state.enrollments.some(e => e.studentId === input.studentId && e.groupId === input.groupId && (!e.endDate || e.endDate >= input.startDate) && (!input.endDate || input.endDate >= e.startDate)), 'DUPLICATE_ENROLLMENT');
    state.enrollments.push({ id, studentId: input.studentId, groupId: input.groupId, startDate: input.startDate, endDate: input.endDate || null, status: input.endDate ? 'ended' : 'active' });
  } else if (command === 'session.save') {
    requireRule(groupAccess(input.groupId).status === 'active', 'ARCHIVED');
    requireRule(validDate(input.date) && /^([01]\d|2[0-3]):[0-5]\d$/.test(input.startTime), 'DATE');
    requireRule(!state.sessions.some(s => s.groupId === input.groupId && s.date === input.date && s.startTime === input.startTime), 'DUPLICATE_SESSION');
    state.sessions.push({ id, groupId: input.groupId, date: input.date, startTime: input.startTime, title: [text(input.title), text(input.title)], status: 'scheduled' });
  } else if (command === 'attendance.record') {
    const session = state.sessions.find(s => s.id === input.sessionId); requireRule(session, 'NOT_FOUND'); groupAccess(session.groupId);
    const person = student(); requireRule(eligible(state, person.id, session), 'NOT_ENROLLED');
    requireRule(['present', 'late', 'absent', 'excused'].includes(input.status));
    const existing = state.attendance.find(a => a.studentId === person.id && a.sessionId === session.id);
    if (existing) {
      requireRule(existing.status !== input.status, 'DUPLICATE_ATTENDANCE');
      requireRule(input.expectedUpdatedAt === existing.updatedAt, 'CONFLICT');
      text(input.reason, 400);
      existing.history.push({ status: existing.status, updatedAt: existing.updatedAt, actorId: existing.actorId, reason: existing.reason });
      Object.assign(existing, { status: input.status, reason: input.reason.trim(), actorId: actor.id, updatedAt: now });
    } else {
      requireRule(person.status === 'active' && groupAccess(session.groupId).status === 'active', 'ARCHIVED');
      state.attendance.push({ id, studentId: person.id, sessionId: session.id, status: input.status, reason: '', actorId: actor.id, updatedAt: now, history: [] });
    }
  } else if (command === 'charge.create') {
    student(); const grossMinor = minorUnits(input.amount), discountMinor = minorUnits(input.discount || '0');
    requireRule(grossMinor > 0 && discountMinor <= grossMinor, 'MONEY'); requireRule(validDate(input.dueDate), 'DATE');
    if (discountMinor) text(input.discountReason, 400);
    state.charges.push({ id, centerId: state.center.id, studentId: input.studentId, description: [text(input.description), text(input.description)], grossMinor, discountMinor, discountReason: input.discountReason || '', currency: 'EGP', dueDate: input.dueDate, createdAt: now, createdBy: actor.id });
  } else if (command === 'payment.record') {
    student(); const amountMinor = minorUnits(input.amount), reference = normalized(text(input.reference, 80));
    requireRule(!state.payments.some(p => normalized(p.reference) === reference), 'DUPLICATE_REFERENCE');
    const charge = state.charges.find(c => c.id === input.chargeId && c.studentId === input.studentId); requireRule(charge, 'NOT_FOUND');
    requireRule(amountMinor > 0 && amountMinor <= chargeBalance(state, charge), 'PAYMENT_LIMIT');
    requireRule(['cash', 'transfer', 'card'].includes(input.method));
    state.payments.push({ id, centerId: state.center.id, studentId: input.studentId, amountMinor, currency: 'EGP', reference, method: input.method, createdAt: now, createdBy: actor.id });
    state.allocations.push({ id: `${id}-allocation`, paymentId: id, chargeId: charge.id, amountMinor });
  } else if (command === 'payment.adjust') {
    const payment = state.payments.find(p => p.id === input.paymentId); requireRule(payment, 'NOT_FOUND');
    const net = payment.amountMinor - state.adjustments.filter(a => a.paymentId === payment.id).reduce((n, a) => n + a.amountMinor, 0);
    const amountMinor = input.type === 'void' ? net : minorUnits(input.amount);
    requireRule(['void', 'refund'].includes(input.type) && amountMinor > 0 && amountMinor <= net, 'PAYMENT_LIMIT');
    state.adjustments.push({ id, paymentId: payment.id, amountMinor, type: input.type, reason: text(input.reason, 400), createdAt: now, createdBy: actor.id });
  }
  state.audit.push({ id: `${id}-audit`, command, actorId: actor.id, at: now, targetId: input.studentId || input.paymentId || input.groupId || id, reason: input.reason || input.discountReason || '' });
  return state;
}

// Persisted snapshots are untrusted input. Reject a broken graph instead of partly importing it.
export function validateWorkspace(s) {
  requireRule(s?.schemaVersion === SCHEMA && Number.isSafeInteger(s.revision) && s.revision >= 0 && s.center?.id === 'nile' && s.center.timezone === 'Africa/Cairo', 'CORRUPT');
  const lists = ['users', 'students', 'groups', 'enrollments', 'sessions', 'attendance', 'charges', 'payments', 'allocations', 'adjustments', 'materials', 'jobs', 'drafts', 'automationRuns', 'workflows', 'audit'];
  for (const key of lists) { requireRule(Array.isArray(s[key]), 'CORRUPT'); const ids = s[key].map(x => x?.id); requireRule(ids.every(x => typeof x === 'string') && new Set(ids).size === ids.length, 'CORRUPT'); }
  requireRule(s.users.length === 3 && ROLES.every(r => s.users.some(u => u.role === r && Array.isArray(u.groupIds))), 'CORRUPT');
  requireRule(s.idempotency && typeof s.idempotency === 'object' && !Array.isArray(s.idempotency), 'CORRUPT');
  for (const student of s.students) requireRule(Array.isArray(student.name) && student.name.length === 2 && student.name.every(n => typeof n === 'string') && typeof student.code === 'string' && ['active', 'archived'].includes(student.status), 'CORRUPT');
  requireRule(new Set(s.students.map(x => normalized(x.code))).size === s.students.length, 'CORRUPT');
  const has = (list, id) => s[list].some(x => x.id === id);
  for (const g of s.groups) requireRule(Array.isArray(g.name) && g.name.every(n => typeof n === 'string') && ['active', 'archived'].includes(g.status), 'CORRUPT');
  for (const e of s.enrollments) requireRule(has('students', e.studentId) && has('groups', e.groupId) && validDate(e.startDate) && (!e.endDate || validDate(e.endDate)), 'CORRUPT');
  for (const session of s.sessions) requireRule(has('groups', session.groupId) && validDate(session.date) && typeof session.startTime === 'string', 'CORRUPT');
  const attendanceKeys = s.attendance.map(a => `${a.sessionId}/${a.studentId}`); requireRule(new Set(attendanceKeys).size === attendanceKeys.length, 'CORRUPT');
  for (const a of s.attendance) requireRule(has('students', a.studentId) && has('sessions', a.sessionId) && ['present', 'late', 'absent', 'excused'].includes(a.status) && Array.isArray(a.history) && typeof a.updatedAt === 'string', 'CORRUPT');
  for (const c of s.charges) requireRule(has('students', c.studentId) && Number.isSafeInteger(c.grossMinor) && Number.isSafeInteger(c.discountMinor) && c.grossMinor >= c.discountMinor && c.discountMinor >= 0 && c.currency === 'EGP', 'CORRUPT');
  for (const p of s.payments) requireRule(has('students', p.studentId) && Number.isSafeInteger(p.amountMinor) && p.amountMinor > 0 && typeof p.reference === 'string' && p.currency === 'EGP', 'CORRUPT');
  requireRule(new Set(s.payments.map(p => normalized(p.reference))).size === s.payments.length, 'CORRUPT');
  for (const a of s.allocations) requireRule(has('payments', a.paymentId) && has('charges', a.chargeId) && Number.isSafeInteger(a.amountMinor) && a.amountMinor > 0 && s.payments.find(p => p.id === a.paymentId).studentId === s.charges.find(c => c.id === a.chargeId).studentId, 'CORRUPT');
  for (const p of s.payments) requireRule(s.allocations.filter(a => a.paymentId === p.id).length === 1 && s.allocations.find(a => a.paymentId === p.id).amountMinor === p.amountMinor, 'CORRUPT');
  for (const a of s.adjustments) requireRule(has('payments', a.paymentId) && Number.isSafeInteger(a.amountMinor) && a.amountMinor > 0 && ['refund', 'void'].includes(a.type) && typeof a.reason === 'string', 'CORRUPT');
  for (const p of s.payments) requireRule(s.adjustments.filter(a => a.paymentId === p.id).reduce((n, a) => n + a.amountMinor, 0) <= p.amountMinor, 'CORRUPT');
  for (const c of s.charges) requireRule(chargeBalance(s, c) >= 0, 'CORRUPT');
  for (const m of s.materials) requireRule(Array.isArray(m.title) && m.title.length === 2 && m.title.every(n => typeof n === 'string') && ['uploading', 'processing', 'ready', 'failed'].includes(m.status) && (m.status !== 'ready' || m.storage === 'demo-bank'), 'CORRUPT');
  const validInstant = value => typeof value === 'string' && !Number.isNaN(Date.parse(value));
  requireRule(validInstant(s.updatedAt), 'CORRUPT');
  for (const p of s.payments) requireRule(validInstant(p.createdAt) && typeof p.createdBy === 'string', 'CORRUPT');
  for (const a of s.adjustments) requireRule(validInstant(a.createdAt) && typeof a.createdBy === 'string', 'CORRUPT');
  for (const c of s.charges) requireRule(Array.isArray(c.description) && c.description.length === 2 && c.description.every(x => typeof x === 'string') && validDate(c.dueDate), 'CORRUPT');
  for (const j of s.jobs) requireRule(['queued', 'running', 'succeeded', 'failed', 'cancelled'].includes(j.status) && validInstant(j.createdAt) && (j.status !== 'failed' || typeof j.failure === 'string'), 'CORRUPT');
  for (const d of s.drafts) {
    requireRule(['exam', 'essay', 'automation', 'lesson'].includes(d.kind) && ['draft', 'reviewed', 'approved', 'teacher-reviewed'].includes(d.status) && validInstant(d.createdAt) && typeof d.createdBy === 'string', 'CORRUPT');
    if (d.kind === 'exam') {
      requireRule(Array.isArray(d.title) && d.title.length === 2 && Array.isArray(d.questions) && d.questions.length > 0, 'CORRUPT');
      for (const q of d.questions) requireRule(typeof q.id === 'string' && Array.isArray(q.text) && q.text.length === 2 && q.text.every(x => typeof x === 'string') && Array.isArray(q.choices) && q.choices.length === 4 && q.choices.every(c => typeof c.id === 'string' && Array.isArray(c.label) && c.label.length === 2 && c.label.every(x => typeof x === 'string')) && new Set(q.choices.map(c => c.id)).size === 4 && q.choices.some(c => c.id === q.correctChoiceId) && Array.isArray(q.explanation) && q.explanation.length === 2 && q.explanation.every(x => typeof x === 'string') && has('materials', q.citation?.materialId), 'CORRUPT');
      requireRule(new Set(d.questions.map(q => q.id)).size === d.questions.length, 'CORRUPT');
    } else if (d.kind === 'automation') requireRule(Array.isArray(d.content) && d.content.length === 2 && d.content.every(x => typeof x === 'string') && has('automationRuns', d.runId) && d.delivery === 'unavailable', 'CORRUPT');
    else if (d.kind === 'essay') requireRule(typeof d.answer === 'string' && Array.isArray(d.suggestion) && d.suggestion.length === 3 && d.suggestion.every(x => Number.isInteger(x.score) && x.score >= 0 && x.score <= 1) && (!d.teacherOverride || (Array.isArray(d.teacherOverride.scores) && d.teacherOverride.scores.length === 3 && d.teacherOverride.scores.every(x => Number.isInteger(x) && x >= 0 && x <= 1))), 'CORRUPT');
    else requireRule(has('materials', d.materialId) && Array.isArray(d.sections) && d.sections.every(x => Array.isArray(x.title) && Number.isInteger(x.minutes)) && typeof d.notes === 'string', 'CORRUPT');
  }
  for (const f of s.workflows) requireRule(['absence', 'report'].includes(f.id) && typeof f.enabled === 'boolean', 'CORRUPT');
  for (const r of s.automationRuns) requireRule(has('sessions', r.sessionId) && has('workflows', r.workflowId) && typeof r.eventKey === 'string' && ['failed', 'succeeded'].includes(r.status) && validInstant(r.startedAt) && validInstant(r.completedAt) && Array.isArray(r.draftIds) && r.draftIds.every(id => has('drafts', id)), 'CORRUPT');
  return s;
}
