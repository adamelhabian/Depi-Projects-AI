import { examVariant } from '../domain/content.js';
import { outstanding, requireRule } from '../domain/workspace.js';

export const escapeHtml = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export function saveFile(blob, filename) { const url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url; link.download = filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
export const csvCell = value => `"${(/^[\s]*[=+\-@]/u.test(String(value)) ? "'" : '') + String(value).replaceAll('"', '""')}"`;
export function exportStudentCsv(students, state, { pick, money, t }) {
  const rows = [[t('Code', 'الكود'), t('English name', 'الاسم بالإنجليزية'), t('Arabic name', 'الاسم بالعربية'), t('Phone', 'التليفون'), t('Status', 'الحالة'), t('Groups', 'المجموعات')], ...students.map(s => [s.code, s.name[0], s.name[1], s.phone, s.status === 'active' ? t('Active', 'نشط') : t('Archived', 'مؤرشف'), state.enrollments.filter(e => e.studentId === s.id).map(e => pick(state.groups.find(g => g.id === e.groupId)?.name)).join(' / ')])];
  saveFile(new Blob(['\uFEFF' + rows.map(row => row.map(csvCell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' }), 'EduFlow-students.csv');
}
export function examExportModel(draft, { lang = 'en', variant = 'A', audience = 'student' } = {}) {
  requireRule(draft?.kind === 'exam' && draft.status === 'reviewed', 'REVIEW_REQUIRED');
  requireRule(['student', 'key'].includes(audience));
  const ar = lang === 'ar', pick = pair => pair[ar ? 1 : 0];
  const questions = examVariant(draft.questions, variant);
  // Student projection deliberately contains no answer IDs, explanations, or key metadata.
  return {
    lang, variant, audience, title: pick(draft.title),
    subtitle: ar ? `نموذج ${variant} · ${audience === 'student' ? 'نسخة الطالب' : 'نموذج الإجابة · نسخة المدرّس'}` : `Variant ${variant} · ${audience === 'student' ? 'Student copy' : 'Answer key · teacher copy'}`,
    note: ar ? 'محتوى بنك تجريبي تمت مراجعته من المدرّس · ليست أسئلة جديدة لكل نموذج' : 'Teacher-reviewed demo bank · variants shuffle existing questions and choices',
    items: questions.map((q, i) => audience === 'student' ? { number: i + 1, text: pick(q.text), choices: q.choices.map((c, j) => `${String.fromCharCode(65 + j)}) ${pick(c.label)}`) } : { number: i + 1, text: pick(q.text), answer: String.fromCharCode(65 + q.choices.findIndex(c => c.id === q.correctChoiceId)), explanation: pick(q.explanation) }),
  };
}
const itemLines = (item, audience, ar) => audience === 'student' ? [item.text, ...item.choices] : [item.text, `${ar ? 'الإجابة' : 'Answer'}: ${item.answer}`, item.explanation];
export function printExam(draft, options) {
  const model = examExportModel(draft, options), ar = model.lang === 'ar';
  const popup = window.open('', '_blank'); if (!popup) throw new Error('EXPORT');
  popup.document.write(`<!doctype html><html lang="${model.lang}" dir="${ar ? 'rtl' : 'ltr'}"><head><meta charset="UTF-8"><title>${escapeHtml(model.subtitle)}</title><style>body{font:16px Arial,sans-serif;line-height:1.9;color:#14243B;margin:20mm auto;max-width:180mm;padding:0 16px}h1{font-size:24px;color:#315DA8}section{break-inside:avoid;margin-block:18px}p{white-space:pre-wrap;unicode-bidi:plaintext;text-align:${ar ? 'right' : 'left'}}small{font-size:11px}button{padding:10px}@media print{button{display:none}@page{size:A4;margin:15mm}body{margin:0;max-width:none;padding:0}}</style></head><body><button id="print">${ar ? 'طباعة / حفظ PDF من المتصفح' : 'Print / save PDF in browser'}</button><h1>${escapeHtml(model.title)}</h1><h2>${escapeHtml(model.subtitle)}</h2><small>${escapeHtml(model.note)}</small>${model.items.map(item => `<section><h3><bdi dir="ltr">${item.number}.</bdi></h3>${itemLines(item, model.audience, ar).map(line => `<p dir="auto">${escapeHtml(line)}</p>`).join('')}</section>`).join('')}</body></html>`);
  popup.document.close(); popup.document.getElementById('print').onclick = () => popup.print(); return popup;
}
export async function exportExamWord(draft, options) {
  const model = examExportModel(draft, options), ar = model.lang === 'ar';
  const { Document, Packer, Paragraph, TextRun, HeadingLevel } = await import('docx');
  const paragraph = (text, heading) => new Paragraph({ bidirectional: ar, heading, spacing: { after: 150 }, children: text.split(/([A-Za-z0-9][A-Za-z0-9\s=×÷+²Ω/λ.()-]*)/g).filter(Boolean).map(part => new TextRun({ text: part, font: 'Arial', size: 24, rightToLeft: ar && /[\u0600-\u06ff]/.test(part) })) });
  const children = [paragraph(model.title, HeadingLevel.TITLE), paragraph(model.subtitle, HeadingLevel.HEADING_1), paragraph(model.note)];
  model.items.forEach(item => { children.push(paragraph(`${item.number}. ${item.text}`, HeadingLevel.HEADING_2)); itemLines(item, model.audience, ar).slice(1).forEach(line => children.push(paragraph(line))); });
  const blob = await Packer.toBlob(new Document({ creator: 'EduFlow AI · demo', sections: [{ properties: {}, children }] }));
  saveFile(blob, `EduFlow-${model.audience}-${model.variant}-${model.lang}.docx`);
}
export async function exportExamSlides(draft, options) {
  const model = examExportModel(draft, options), ar = model.lang === 'ar';
  const { default: PptxGenJS } = await import('pptxgenjs'); const ppt = new PptxGenJS(); ppt.layout = 'LAYOUT_WIDE'; ppt.author = 'EduFlow AI · demo'; ppt.subject = model.subtitle; ppt.lang = ar ? 'ar-EG' : 'en-GB';
  const content = [{ title: model.title, body: `${model.subtitle}\n${model.note}` }, ...model.items.map(i => ({ title: `${i.number}.`, body: itemLines(i, model.audience, ar).join('\n') }))];
  content.forEach((item, i) => {
    const chunks = item.body.match(/[\s\S]{1,650}/g) || [''];
    chunks.forEach((body, part) => { const slide = ppt.addSlide(); slide.background = { color: i === 0 ? '14243B' : 'F8F9FF' }; const color = i === 0 ? 'FFFFFF' : '14243B'; slide.addText(`${item.title}${part ? ` (${part + 1})` : ''}`, { x: .6, y: .5, w: 12, h: .8, fontFace: 'Arial', fontSize: 25, color, rtlMode: ar, align: ar ? 'right' : 'left', fit: 'shrink' }); slide.addText(body, { x: .6, y: 1.6, w: 12, h: 4.7, fontFace: 'Arial', fontSize: 25, color, rtlMode: ar, align: ar ? 'right' : 'left', breakLine: false, fit: 'shrink' }); slide.addText(model.subtitle, { x: .6, y: 6.7, w: 12, h: .3, fontSize: 11, color, rtlMode: ar }); });
  });
  await ppt.writeFile({ fileName: `EduFlow-${model.audience}-${model.variant}-${model.lang}.pptx` });
}
