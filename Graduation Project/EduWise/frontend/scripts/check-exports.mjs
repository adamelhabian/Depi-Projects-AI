import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import JSZip from 'jszip'; // Already installed by the locked Office export dependencies.
const root = path.resolve('test-results');
async function contents(file) {
  const zip = await JSZip.loadAsync(await readFile(path.join(root, file)));
  const targets = Object.keys(zip.files).filter(name => name === 'word/document.xml' || /^ppt\/slides\/slide[0-9]+\.xml$/.test(name));
  assert(targets.length > 0, `${file}: document parts`);
  const xml = (await Promise.all(targets.map(name => zip.file(name).async('string')))).join('');
  return { xml, text: xml.replace(/<[^>]*>/g, '').replaceAll('&amp;', '&').replaceAll('&apos;', "'"), targets };
}
for (const file of ['student-en.docx', 'student-en.pptx', 'student-ar.docx', 'student-ar.pptx']) {
  const { text, xml } = await contents(file);
  assert(!/Answer:|Answer key|نموذج الإجابة|الإجابة:|Newton’s second law:|طبقاً لقانون نيوتن الثاني/.test(text), `${file}: student copy leaks a solution`);
  if (file.includes('-ar.')) { assert(text.includes('اختبار الفيزياء')); assert(file.endsWith('docx') ? xml.includes('<w:bidi') && xml.includes('<w:rtl') : /rtl="1"/.test(xml), `${file}: RTL metadata missing`); }
  console.log(`PASS ${file}: valid package, correct audience${file.includes('-ar.') ? ', Arabic text and RTL' : ''}`);
}
const key = await contents('key-en.docx'); assert(key.text.includes('Answer key')); assert(key.text.includes('Answer:')); assert(key.text.includes('Mass is a measure of inertia.'));
console.log('PASS key-en.docx: teacher answers and explanation present in separate package');
const csv = await readFile(path.join(root, 'students-safe.csv'), 'utf8'); assert(csv.startsWith('\uFEFF')); assert(csv.includes('يوسف Test')); assert(csv.includes("'=1+1"));
console.log('PASS students-safe.csv: UTF-8 BOM, Arabic and escaped formula');
