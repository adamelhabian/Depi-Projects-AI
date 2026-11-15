import { examBank } from '../data/mockData.js';
import { can, requireRule, calendarDate } from './workspace.js';

export function buildQuestions(state, input) {
  requireRule(Array.isArray(input.materialIds) && input.materialIds.length > 0, 'SOURCE_REQUIRED');
  const sources = input.materialIds.map(id => state.materials.find(m => m.id === id));
  requireRule(sources.every(m => m?.status === 'ready' && m.storage === 'demo-bank'), 'NOT_READY');
  requireRule(input.subject === 'physics' && sources.every(m => m.grade === input.grade), 'UNSUPPORTED_SOURCE');
  requireRule(['mixed', 'foundation', 'challenge'].includes(input.difficulty) && input.questionType === 'mcq', 'UNSUPPORTED_REQUEST');
  const pool = examBank.filter(q => input.materialIds.includes(q.topic) && (!input.topic || input.topic === 'all' || q.topic === input.topic) && (input.difficulty === 'mixed' || (input.difficulty === 'challenge' ? /\d/.test(q.q[0]) : !/\d/.test(q.q[0]))));
  requireRule(Number.isInteger(input.count) && input.count > 0 && input.count <= pool.length, 'INSUFFICIENT_QUESTIONS');
  return pool.slice(0, input.count).map((q, i) => ({ id: `question-${i + 1}`, text: [...q.q], choices: q.options.map((label, j) => ({ id: `choice-${j}`, label: [...label] })), correctChoiceId: `choice-${q.answer}`, explanation: [...q.explanation], citation: { materialId: q.topic, page: null, demoPage: q.source, verification: 'demo-only' } }));
}
export function examVariant(questions, variant = 'A') {
  const shift = ['A', 'B', 'C'].indexOf(variant); requireRule(shift >= 0);
  const items = structuredClone(questions);
  if (shift) items.reverse();
  return items.map(q => ({ ...q, choices: [...q.choices.slice(shift), ...q.choices.slice(0, shift)] }));
}
export const essayRubric = [
  { id: 'force', label: ['Names the force concept', 'ذكر مفهوم القوة'], max: 1, words: ['force', 'قوة', 'القوة'] },
  { id: 'mass', label: ['Names mass', 'ذكر الكتلة'], max: 1, words: ['mass', 'كتلة', 'الكتلة'] },
  { id: 'acceleration', label: ['Names acceleration', 'ذكر العجلة'], max: 1, words: ['acceleration', 'عجلة', 'العجلة', 'تسارع'] },
];
export function suggestEssay(answer) {
  return essayRubric.map(c => ({ criterionId: c.id, score: c.words.some(w => answer.toLocaleLowerCase().includes(w)) ? 1 : 0, max: c.max }));
}
export function applyContent(current, command, input, context) {
  const permission = command.startsWith('automation.') ? 'automation.write' : 'content.write';
  requireRule(can(context.role, permission), 'FORBIDDEN');
  const s = structuredClone(current), { id, now, role } = context;
  const actor = s.users.find(u => u.role === role);
  const draft = () => { const d = s.drafts.find(x => x.id === input.draftId); requireRule(d, 'NOT_FOUND'); requireRule(role === 'admin' || d.createdBy === actor.id, 'FORBIDDEN'); return d; };
  if (command === 'content.material') {
    requireRule(input.size > 0 && input.size <= 15 * 1024 * 1024 && /\.pdf$/i.test(input.name), 'PDF_LIMIT');
    requireRule(input.header === '%PDF-', 'PDF_HEADER');
    // No content bytes are saved; no fictitious upload or processing success.
    s.materials.unshift({ id, title: [input.name, input.name], subtitle: ['PDF metadata only', 'بيانات PDF فقط'], pages: null, type: 'PDF', date: calendarDate(new Date(now)), cover: 'sand', source: 'uploaded', bytes: input.size, storage: 'metadata-only', status: 'failed', failure: 'INDEXING_UNAVAILABLE', subject: input.subject, grade: input.grade, topic: '', citationType: 'unavailable', createdAt: now });
  } else if (command === 'content.material.retry') {
    const m = s.materials.find(x => x.id === input.materialId); requireRule(m, 'NOT_FOUND');
    requireRule(m.storage !== 'metadata-only', 'INDEXING_UNAVAILABLE'); requireRule(false, 'UNSUPPORTED_REQUEST');
  } else if (command === 'content.generate') {
    let questions, failure;
    try { questions = buildQuestions(s, input); } catch (error) { failure = error.code || 'VALIDATION'; }
    const job = { id, kind: 'exam', status: failure ? 'failed' : 'succeeded', source: 'demo-bank', request: input, createdAt: now, completedAt: now, createdBy: actor.id, failure: failure || null };
    s.jobs.unshift(job);
    if (!failure) s.drafts.unshift({ id: `${id}-draft`, kind: 'exam', title: input.purpose === 'worksheet' ? ['Physics worksheet', 'ورقة عمل الفيزياء'] : ['Physics assessment', 'اختبار الفيزياء'], status: 'draft', jobId: id, questions, config: input, createdAt: now, updatedAt: now, createdBy: actor.id, provenance: 'demo-bank', reviewedAt: null });
  } else if (command === 'content.exam.edit') {
    const d = draft(); requireRule(d.kind === 'exam');
    requireRule(Array.isArray(input.questions) && input.questions.length === d.questions.length);
    requireRule(new Set(input.questions.map(q => q.id)).size === d.questions.length);
    for (const q of input.questions) requireRule(d.questions.some(x => x.id === q.id) && Array.isArray(q.text) && q.text.length === 2 && q.text.every(t => typeof t === 'string' && t.trim() && t.length <= 3000) && Array.isArray(q.choices) && q.choices.length === 4 && new Set(q.choices.map(c => c.id)).size === 4 && q.choices.every(c => Array.isArray(c.label) && c.label.length === 2 && c.label.every(t => typeof t === 'string' && t.trim() && t.length <= 1000)) && q.choices.some(c => c.id === q.correctChoiceId) && Array.isArray(q.explanation) && q.explanation.length === 2 && q.explanation.every(t => typeof t === 'string' && t.length <= 4000));
    // Citations come from the stored draft, never from an editable client payload.
    d.questions = input.questions.map(q => ({ ...q, citation: d.questions.find(x => x.id === q.id).citation }));
    d.status = 'draft'; d.updatedAt = now; d.reviewedAt = null;
  } else if (command === 'content.exam.review') {
    const d = draft(); requireRule(d.kind === 'exam'); d.status = 'reviewed'; d.reviewedAt = now; d.reviewedBy = actor.id;
  } else if (command === 'content.lesson') {
    requireRule(s.materials.some(m => m.id === input.materialId && m.status === 'ready'), 'NOT_READY');
    requireRule(Number.isInteger(input.minutes) && input.minutes >= 30 && input.minutes <= 180);
    const sections = [
      { title: ['Reconnect', 'مراجعة وربط'], minutes: Math.floor(input.minutes / 6) },
      { title: ['Explain the concept', 'شرح المفهوم'], minutes: Math.floor(input.minutes / 2) },
      { title: ['Guided practice', 'تطبيق ومناقشة'], minutes: Math.floor(input.minutes / 5) },
    ];
    sections.push({ title: ['Exit question', 'سؤال ختامي'], minutes: input.minutes - sections.reduce((n, x) => n + x.minutes, 0) });
    s.drafts.unshift({ id, kind: 'lesson', status: 'draft', materialId: input.materialId, minutes: input.minutes, sections, notes: input.notes || '', provenance: 'demo-template', createdAt: now, createdBy: actor.id });
  } else if (command === 'content.essay') {
    requireRule(typeof input.answer === 'string' && input.answer.trim().length >= 15 && input.answer.length <= 20000, 'ESSAY_LENGTH');
    s.drafts.unshift({ id, kind: 'essay', status: 'draft', answer: input.answer, rubric: essayRubric, suggestion: suggestEssay(input.answer), teacherOverride: null, createdAt: now, createdBy: actor.id, provenance: 'keyword-demo' });
  } else if (command === 'content.essay.override') {
    const d = draft(); requireRule(d.kind === 'essay');
    requireRule(Array.isArray(input.scores) && input.scores.length === essayRubric.length && input.scores.every(x => Number.isInteger(x) && x >= 0 && x <= 1) && input.reason?.trim(), 'RUBRIC');
    d.teacherOverride = { scores: input.scores, reason: input.reason.trim(), at: now, by: actor.id }; d.status = 'teacher-reviewed';
  } else if (command === 'automation.configure') {
    const flow = s.workflows.find(f => f.id === input.workflowId); requireRule(flow && typeof input.enabled === 'boolean'); flow.enabled = input.enabled;
  } else if (command === 'automation.run') {
    const flow = s.workflows.find(f => f.id === input.workflowId); requireRule(flow?.enabled, 'FLOW_DISABLED');
    const session = s.sessions.find(x => x.id === input.sessionId); requireRule(session, 'NOT_FOUND');
    requireRule(role !== 'teacher' || actor.groupIds.includes(session.groupId), 'FORBIDDEN');
    const eventKey = `${flow.id}:${session.id}`;
    requireRule(!s.automationRuns.some(r => r.eventKey === eventKey && r.status === 'succeeded'), 'DUPLICATE_EVENT');
    const absent = s.attendance.filter(a => a.sessionId === session.id && a.status === 'absent');
    const records = s.attendance.filter(a => a.sessionId === session.id);
    const failed = flow.id === 'absence' ? !absent.length : !records.length;
    const run = { id, workflowId: flow.id, eventKey, sessionId: session.id, startedAt: now, completedAt: now, status: failed ? 'failed' : 'succeeded', failure: failed ? 'NO_EVIDENCE' : null, createdBy: actor.id, mode: 'demo', draftIds: [] };
    s.automationRuns.unshift(run);
    const targets = flow.id === 'absence' ? absent : failed ? [] : [{ studentId: null }];
    targets.forEach((a, i) => {
      const person = s.students.find(x => x.id === a.studentId), draftId = `${id}-draft-${i}`;
      run.draftIds.push(draftId);
      s.drafts.unshift({ id: draftId, kind: 'automation', runId: id, studentId: a.studentId, createdBy: actor.id, createdAt: now, updatedAt: now, status: 'draft', delivery: 'unavailable', content: person ? [`Hello, ${person.name[0]} was recorded absent for the session on ${session.date}. Please contact the center to follow up.`, `مرحباً، تم تسجيل غياب ${person.name[1]} عن حصة ${session.date}. يرجى التواصل مع السنتر للمتابعة.`] : [`Session ${session.date}: ${records.length} attendance records. This is a session summary, not a scheduled weekly report.`, `حصة ${session.date}: عدد سجلات الحضور ${records.length}. هذا ملخص حصة وليس تقريراً أسبوعياً مجدولاً.`] });
    });
  } else if (command === 'automation.edit') {
    const d = draft(); requireRule(d.kind === 'automation' && d.status !== 'approved', 'APPROVED_LOCKED');
    requireRule(Array.isArray(input.content) && input.content.length === 2 && input.content.every(x => typeof x === 'string' && x.trim() && x.length <= 10000)); d.content = input.content; d.status = 'draft'; d.updatedAt = now;
  } else if (command === 'automation.review') {
    const d = draft(); requireRule(d.kind === 'automation' && d.status === 'draft'); d.status = 'reviewed'; d.reviewedAt = now; d.reviewedBy = actor.id;
  } else if (command === 'automation.approve') {
    const d = draft(); requireRule(d.kind === 'automation' && d.status === 'reviewed', 'REVIEW_REQUIRED'); d.status = 'approved'; d.approvedAt = now; d.approvedBy = actor.id;
  } else requireRule(false, 'UNSUPPORTED_REQUEST');
  s.audit.push({ id: `${id}-audit`, command, at: now, actorId: actor.id, targetId: input.draftId || input.materialId || id, reason: input.reason || '' });
  return s;
}
