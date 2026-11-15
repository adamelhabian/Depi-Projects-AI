import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorkspace, applyOperation, projectWorkspace } from '../src/domain/workspace.js';
import { attendanceSummary, operationalReport } from '../src/domain/reports.js';

test('7 present of 8 records is 87.5%; missing and excused never become absences', () => {
  const records = [...Array.from({length:7},()=>({status:'present'})),{status:'absent'},{status:'excused'}];
  assert.equal(attendanceSummary(records).rate,87.5);
  assert.equal(attendanceSummary([]).rate,null);
  assert.equal(attendanceSummary([{status:'excused'}]).rate,null);
});
test('register changes and corrections flow into reports without fixture fallbacks', () => {
  let data=createWorkspace('2026-10-23T10:00:00Z');
  const context={role:'admin',id:'a1',now:'2026-10-23T11:00:00Z'};
  data=applyOperation(data,'attendance.record',{studentId:'student-1',sessionId:'session-1',status:'absent'},context);
  assert.equal(operationalReport(data).absent,1);
  const record=data.attendance[0];
  data=applyOperation(data,'attendance.record',{studentId:'student-1',sessionId:'session-1',status:'present',reason:'Corrected register',expectedUpdatedAt:record.updatedAt},{...context,id:'a2',now:'2026-10-23T11:01:00Z'});
  assert.equal(operationalReport(data).absent,0);
  assert.equal(operationalReport(data).rate,100);
  assert.equal(operationalReport(data).recorded,1);
});
test('future periods contain no sessions, records or revenue; group projection is respected', () => {
  const data=createWorkspace('2026-10-23T10:00:00Z');
  const empty=operationalReport(data,{from:'2030-01-01',to:'2030-01-31'});
  assert.equal(empty.sessions.length,0); assert.equal(empty.rate,null); assert.equal(empty.netMinor,0); assert.equal(empty.missing,0);
  const group=operationalReport(data,{groupId:'group-1'});
  assert.equal(group.sessions.length,1); assert.equal(group.students.length,8);
  const teacher=operationalReport(projectWorkspace(data,'teacher'));
  assert.equal(teacher.netMinor,0); assert.equal(teacher.sessions.length,2);
});

test('date range validation handles valid, single-day, open-ended, and invalid ranges with exact localized errors', async () => {
  const { isValidDateRange, dateRangeErrorText } = await import('../src/i18n.js');
  // Valid ranges
  assert.equal(isValidDateRange('2026-10-01', '2026-10-23'), true);
  // Single-day range (start equals end)
  assert.equal(isValidDateRange('2026-10-23', '2026-10-23'), true);
  // Open-ended ranges
  assert.equal(isValidDateRange('', '2026-10-23'), true);
  assert.equal(isValidDateRange('2026-10-01', ''), true);
  assert.equal(isValidDateRange('', ''), true);
  // Invalid range (start after end)
  assert.equal(isValidDateRange('2026-10-25', '2026-10-20'), false);

  // Exact required error strings
  assert.equal(dateRangeErrorText('ar'), 'تاريخ البداية لازم يكون قبل تاريخ النهاية أو مساوي له');
  assert.equal(dateRangeErrorText('en'), 'Start date must be on or before end date.');
});

test('operational report includes records on boundary days and supports single-day period in Cairo time', () => {
  const data = createWorkspace('2026-10-23T10:00:00Z');
  const today = '2026-10-23';
  // Single-day period containing today's sessions and seed payments
  const singleDay = operationalReport(data, { from: today, to: today });
  assert.equal(singleDay.sessions.length, 3);
  assert.equal(singleDay.receipts.length, 18);
  assert.equal(singleDay.netMinor, 1620000);

  // Date range spanning today
  const range = operationalReport(data, { from: '2026-10-20', to: '2026-10-25' });
  assert.equal(range.sessions.length, 3);
  assert.equal(range.receipts.length, 18);
});

test('receipt localization translates payment methods, resolves employee display, and preserves audit identities', async () => {
  const { translatePaymentMethod, resolveEmployeeDisplay, formatGrade } = await import('../src/i18n.js');
  // Payment methods
  assert.equal(translatePaymentMethod('cash', 'ar'), 'نقدي');
  assert.equal(translatePaymentMethod('cash', 'en'), 'Cash');
  assert.equal(translatePaymentMethod('card', 'ar'), 'بطاقة');
  assert.equal(translatePaymentMethod('card', 'en'), 'Card');
  assert.equal(translatePaymentMethod('transfer', 'ar'), 'تحويل بنكي');
  assert.equal(translatePaymentMethod('transfer', 'en'), 'Bank transfer');

  // Employee display resolution
  const users = [
    { id: 'user-admin', name: ['Youssef Mohamed', 'يوسف محمد'], role: 'admin' },
    { id: 'user-teacher-anon', role: 'teacher' },
  ];
  assert.equal(resolveEmployeeDisplay('user-admin', users, 'ar'), 'يوسف محمد');
  assert.equal(resolveEmployeeDisplay('user-admin', users, 'en'), 'Youssef Mohamed');
  assert.equal(resolveEmployeeDisplay('user-teacher-anon', users, 'ar'), 'مدرّس');
  assert.equal(resolveEmployeeDisplay('user-teacher-anon', users, 'en'), 'Teacher');
  assert.equal(resolveEmployeeDisplay('user-missing', users, 'ar'), 'غير متاح');
  assert.equal(resolveEmployeeDisplay('user-missing', users, 'en'), 'Not available');
  assert.equal(resolveEmployeeDisplay(null, users, 'ar'), 'غير متاح');

  // Human-readable educational grades
  assert.equal(formatGrade('11', 'ar'), 'الصف الثاني الثانوي');
  assert.equal(formatGrade('11', 'en'), 'Grade 11');
  assert.equal(formatGrade('12', 'ar'), 'الصف الثالث الثانوي');
  assert.equal(formatGrade('12', 'en'), 'Grade 12');
  assert.equal(formatGrade('10', 'ar'), 'الصف 10');
  assert.equal(formatGrade('10', 'en'), 'Grade 10');
});
