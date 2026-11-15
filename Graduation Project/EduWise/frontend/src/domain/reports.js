import { calendarDate, eligible } from './workspace.js';

export function attendanceSummary(records) {
  const present = records.filter(r => ['present', 'late'].includes(r.status)).length;
  const absent = records.filter(r => r.status === 'absent').length;
  const excused = records.filter(r => r.status === 'excused').length;
  const denominator = present + absent;
  return { recorded: records.length, present, absent, excused, denominator, rate: denominator ? Math.round(present / denominator * 1000) / 10 : null };
}

export function operationalReport(data, { from = '0000-01-01', to = '9999-12-31', groupId = '' } = {}) {
  const sessions = data.sessions.filter(s => s.date >= from && s.date <= to && (!groupId || s.groupId === groupId));
  const sessionIds = new Set(sessions.map(s => s.id));
  const records = data.attendance.filter(r => sessionIds.has(r.sessionId));
  const students = data.students.filter(p => sessions.some(s => eligible(data, p.id, s)));
  const studentIds = new Set(students.map(s => s.id));
  const inPeriod = event => { const day = calendarDate(new Date(event.createdAt)); return day >= from && day <= to; };
  const receipts = data.payments.filter(p => inPeriod(p) && (!groupId || studentIds.has(p.studentId)));
  const adjustments = data.adjustments.filter(a => inPeriod(a) && (!groupId || studentIds.has(data.payments.find(p => p.id === a.paymentId)?.studentId)));
  const expected = sessions.reduce((n, s) => n + data.students.filter(p => eligible(data, p.id, s)).length, 0);
  return { sessions, records, students, expected, missing: Math.max(0, expected - records.length), ...attendanceSummary(records), receipts, adjustments, netMinor: receipts.reduce((n, p) => n + p.amountMinor, 0) - adjustments.reduce((n, a) => n + a.amountMinor, 0) };
}
