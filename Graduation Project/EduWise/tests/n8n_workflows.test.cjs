const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');

const path = join(__dirname, '..', 'data', 'n8n');
const alert = JSON.parse(readFileSync(join(path, 'eduflow_student_alert_workflow.json'), 'utf8'));
const homework = JSON.parse(readFileSync(join(path, 'eduflow_vision_homework_grader.json'), 'utf8'));
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

function run(workflow, name, input, previous = {}, helpers = {}, binary) {
  const node = workflow.nodes.find(node => node.name === name);
  const code = new AsyncFunction('$input', '$', node.parameters.jsCode);
  return code.call({ helpers }, { first: () => ({ json: input, binary }) }, name => ({
    first: () => ({ json: previous[name] }),
  }));
}

test('prototype graphs use native providers and a single Telegram trigger', () => {
  for (const workflow of [alert, homework]) {
    const nodes = new Set(workflow.nodes.map(node => node.name));
    assert.equal(nodes.size, workflow.nodes.length);
    assert.equal(workflow.settings.saveDataSuccessExecution, 'none');
    assert.equal(workflow.settings.saveDataErrorExecution, 'none');
    assert.ok(workflow.nodes.some(node => node.type.endsWith('.googleGemini')));
    assert.ok(workflow.nodes.every(node => !node.type.endsWith('.httpRequest')));
    for (const [name, connection] of Object.entries(workflow.connections)) {
      assert.ok(nodes.has(name));
      for (const edge of connection.main.flat()) assert.ok(nodes.has(edge.node));
    }
    for (const node of workflow.nodes) {
      if (node.parameters.jsCode) assert.doesNotThrow(() => new AsyncFunction(node.parameters.jsCode));
    }
  }
  assert.equal([...alert.nodes, ...homework.nodes].filter(n => n.type.endsWith('.telegramTrigger')).length, 1);
  assert.equal(alert.name, 'Smart Parental Intervention Alert');
  assert.equal(homework.name, 'Vision AI Homework and Quiz Assistant');
  assert.equal(homework.nodes.find(n => n.name === 'Run Parent Demo').parameters.workflowId.value, 'C04gl8dLAMCxy4Zm');
});

function candidate(text, finishReason = 'STOP') {
  return { candidates: [{ finishReason, content: { parts: [{ thought: true, text: 'Ignore' }, { text }] } }] };
}

test('guardian demo uses synthetic threshold scenarios and only approved coaching tips', async () => {
  const choose = input => run(alert, 'Validate Alert Input', input);
  const [demo] = await choose({});
  assert.equal(demo.json.missed, 4);
  assert.equal(demo.json.route, 'alert');
  assert.equal((await choose({ scenario: 'risk' }))[0].json.route, 'alert');
  assert.equal((await choose({ scenario: 'ok' }))[0].json.route, 'skip');
  const previous = { 'Validate Alert Input': demo.json };
  const [response] = await run(alert, 'Format Parent Telegram Alert', candidate('ATTENDANCE'), previous);
  assert.equal(response.json.source, 'gemini');
  assert.match(response.json.text, /Demo\nالطالب: طالب تجريبي/);
  const [fallback] = await run(alert, 'Format Parent Telegram Alert', candidate('fabricated message'), previous);
  assert.equal(fallback.json.source, 'fallback');
  assert.equal(response.json.text, fallback.json.text);
});

test('original webhook keeps the demo URL and cannot send Telegram messages', async () => {
  const webhook = alert.nodes.find(n => n.name === 'Webhook Trigger');
  assert.equal(webhook.parameters.path, 'student-eval');
  assert.equal(alert.connections['Webhook Trigger'].main[0][0].node, 'Preview Webhook Alert');
  assert.equal(alert.connections['Preview Webhook Alert'].main[0][0].node, 'Respond to Demo Webhook');
  assert.equal(alert.connections['Respond to Demo Webhook'], undefined);
  const [preview] = await run(alert, 'Preview Webhook Alert', { body: {
    missed_sessions_count: 4, telegram_chat_id: '12345', student_name: 'identity',
  } });
  assert.equal(preview.json.should_alert, true);
  assert.equal(preview.json.preview_only, true);
  assert.doesNotMatch(preview.json.message, /identity|12345/);
  const [invalid] = await run(alert, 'Preview Webhook Alert', { body: { missed_sessions_count: -1 } });
  assert.equal(invalid.json.status, 'invalid_attendance');
});

const message = { chat: { type: 'private', id: 22 }, from: { id: 22 } };

test('the Telegram bot routes homeworks and parent demo commands back to the sender', async () => {
  const update = event => run(homework, 'Route Private Telegram Message', { message: { ...message, ...event } });
  for (const [text, scenario] of [['/parent', 'absence'], ['/parent risk', 'risk'], ['/parent@EduWiseBot ok', 'ok']]) {
    assert.deepEqual((await update({ text }))[0].json, { route: 'parent', chat_id: '22', scenario });
  }
  const photo = [{ file_id: 'clear', width: 400, height: 500 }];
  assert.equal((await update({ photo }))[0].json.assignment_code, 'PRACTICE');
  assert.equal((await update({ photo, caption: '#HW-01' }))[0].json.assignment_code, 'HW-01');
  assert.equal((await update({ photo, caption: '#UNKNOWN-02' }))[0].json.route, 'reply');
  assert.deepEqual(await update({ photo, chat: { type: 'group', id: 22 } }), []);
});

test('the demo rubric matches the bundled worksheet and Gemini receives verified binary data', async () => {
  const previous = { 'Route Private Telegram Message': { assignment_code: 'HW-01' } };
  const binary = { data: { id: 'fixture', mimeType: 'application/octet-stream' } };
  const helpers = { getBinaryDataBuffer: async () => Buffer.from([0xff, 0xd8, 0xff, 0x00]) };
  const prepare = await run(homework, 'Build Gemini Vision Request', {}, previous, helpers, binary);
  assert.equal(prepare[0].binary.data.mimeType, 'image/jpeg');
  assert.match(prepare[0].json.rubric[2].criterion, /154 cm²/);
  assert.match(prepare[0].json.prompt, /exactly these four questions/);
  await assert.rejects(run(homework, 'Build Gemini Vision Request', {}, previous, {
    getBinaryDataBuffer: async () => Buffer.from('unsupported'),
  }, binary), /Unsupported/);
});

test('the prototype computes totals, rejects malformed grades and asks for a clearer photo', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const question = { question_id: '1', status: 'scored', earned: 0.5, observed: 'x = 5', feedback_ar: 'راجع القسمة.', solution_ar: 'x = 4' };
  const grade = input => run(homework, 'Format Feedback and Payload', input, previous);
  const valid = await grade(candidate(JSON.stringify({ questions: [question] })));
  assert.equal(valid[0].json.score, 0.5);
  assert.match(valid[0].json.text, /0\.5 من 1/);
  const unclear = await grade(candidate(JSON.stringify({ questions: [{ ...question, status: 'unreadable', earned: 0 }] })));
  assert.equal(unclear[0].json.score, null);
  assert.match(unclear[0].json.text, /صورة أوضح/);
  await assert.rejects(grade(candidate('invalid JSON')), SyntaxError);
  await assert.rejects(grade(candidate(JSON.stringify({ questions: [{ ...question, earned: 10 }] }))), /per-question/);
  await assert.rejects(grade(candidate('invalid', 'MAX_TOKENS')), /incomplete/);
});

test('multi-part Gemini response is joined and unescaped LaTeX backslashes are sanitized', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const multiPartCandidate = {
    candidates: [{
      finishReason: 'STOP',
      content: {
        parts: [
          { thought: true, text: 'Thinking step by step...' },
          { text: '```json\n{"student_name": "سارة", "questions": [{"question_id": "1", ' },
          { text: '"status": "scored", "earned": 1, "observed": "Area = \\pi r^2 = 154", ' },
          { text: '"feedback_ar": "كافة الإجابات صحيحة وممتازة.", "solution_ar": "\\frac{22}{7} \\times 49 = 154"}]}' },
          { text: '\n```' },
        ],
      },
    }],
  };
  const [result] = await run(homework, 'Format Feedback and Payload', multiPartCandidate, previous);
  assert.equal(result.json.score, 1);
  assert.equal(result.json.max_score, 1);
  assert.match(result.json.text, /سارة/);
  assert.match(result.json.text, /1 من 1/);
  assert.doesNotMatch(result.json.text, /\\n/);
});

test('edge case: English high-school sheet (4 questions, 4 correct -> 4/4 100%)', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const questions = [
    { question_id: '1', status: 'scored', earned: 1, observed: 'x = 4', feedback_ar: 'حل سليم.', solution_ar: 'x = 4' },
    { question_id: '2', status: 'scored', earned: 1, observed: '6x + 5', feedback_ar: 'مشتقة صحيحة.', solution_ar: '6x + 5' },
    { question_id: '3', status: 'scored', earned: 1, observed: '154 cm^2', feedback_ar: 'تطبيق رائع لقانون المساحة.', solution_ar: 'A = 154' },
    { question_id: '4', status: 'scored', earned: 1, observed: '45 degrees', feedback_ar: 'زاوية دقيقة.', solution_ar: '45 deg' },
  ];
  const payload = candidate(JSON.stringify({ assignment_title: 'Algebra & Calculus', questions }));
  const [result] = await run(homework, 'Format Feedback and Payload', payload, previous);
  assert.equal(result.json.score, 4);
  assert.equal(result.json.max_score, 4);
  assert.equal(result.json.percentage, 100);
  assert.match(result.json.text, /4 من 4 \(100٪\)/);
  assert.match(result.json.text, /Algebra & Calculus/);
  assert.match(result.json.text, /✅/);
  assert.doesNotMatch(result.json.text, /\\n/);
  assert.doesNotMatch(result.json.text, /"questions":/);
});

test('edge case: Arabic high-school sheet (3 questions, 2 correct, 1 wrong -> 2/3 67%)', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const questions = [
    { question_id: '1', status: 'scored', earned: 1, observed: 'س = ٣', feedback_ar: 'إجابة صحيحة.', solution_ar: 'س = ٣' },
    { question_id: '2', status: 'scored', earned: 1, observed: 'المحيط = ٤٤ سم', feedback_ar: 'حساب دقيق.', solution_ar: '٤٤ سم' },
    { question_id: '3', status: 'scored', earned: 0, observed: 'المساحة = ٤٤', feedback_ar: 'خلطت بين المحيط والمساحة، قانون المساحة ط نق².', solution_ar: 'المساحة = ١٥٤ سم²' },
  ];
  const payload = candidate(JSON.stringify({ student_name: 'أحمد', questions }));
  const [result] = await run(homework, 'Format Feedback and Payload', payload, previous);
  assert.equal(result.json.score, 2);
  assert.equal(result.json.max_score, 3);
  assert.equal(result.json.percentage, 67);
  assert.match(result.json.text, /2 من 3 \(67٪\)/);
  assert.match(result.json.text, /أحمد/);
  assert.match(result.json.text, /❌/);
  assert.match(result.json.text, /✅/);
  assert.doesNotMatch(result.json.text, /\\n/);
});

test('edge case: University math sheet (determinants and advanced calculus)', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const questions = [
    { question_id: '1', status: 'scored', earned: 1, observed: 'det(A) = ad - bc = 10 - 12 = -2', feedback_ar: 'حساب صحيح للمحدد.', solution_ar: 'det(A) = -2' },
    { question_id: '2', status: 'scored', earned: 0.5, observed: 'dy/dx = 2x e^x', feedback_ar: 'نسيت تطبيق قاعدة ضرب دالتين على الجزء الثاني.', solution_ar: 'dy/dx = 2x e^x + x^2 e^x' },
  ];
  const payload = candidate(JSON.stringify({ assignment_title: 'Linear Algebra & Calculus III', questions }));
  const [result] = await run(homework, 'Format Feedback and Payload', payload, previous);
  assert.equal(result.json.score, 1.5);
  assert.equal(result.json.max_score, 2);
  assert.equal(result.json.percentage, 75);
  assert.match(result.json.text, /1\.5 من 2 \(75٪\)/);
  assert.match(result.json.text, /⚠️/);
  assert.doesNotMatch(result.json.text, /\\n/);
});

test('Telegram message formatting has proper emojis, line breaks, and no raw JSON', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const questions = [
    { question_id: '1', status: 'scored', earned: 1, observed: '2x = 8 -> x = 4', feedback_ar: 'ممتاز', solution_ar: 'x = 4' },
  ];
  const payload = candidate(JSON.stringify({ student_name: 'عمر', assignment_title: 'جبر', feedback_ar: 'استمر في التفوق!', questions }));
  const [result] = await run(homework, 'Format Feedback and Payload', payload, previous);
  assert.match(result.json.text, /📝/);
  assert.match(result.json.text, /👤/);
  assert.match(result.json.text, /📊/);
  assert.match(result.json.text, /✅/);
  assert.match(result.json.text, /💡/);
  assert.doesNotMatch(result.json.text, /\\n/);
  assert.doesNotMatch(result.json.text, /{"/);
});

test('valid JSON with already escaped backslashes in markdown fences parses directly without corruption', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: [] },
  };
  const fencedPayload = candidate('```json\n{"questions": [{"question_id": "1", "status": "scored", "earned": 1, "observed": "A = \\\\pi r^2", "feedback_ar": "صحيح", "solution_ar": "A = \\\\pi r^2"}]}\n```');
  const [result] = await run(homework, 'Format Feedback and Payload', fencedPayload, previous);
  assert.equal(result.json.score, 1);
  assert.equal(result.json.max_score, 1);
  assert.match(result.json.text, /1 من 1/);
  assert.doesNotMatch(result.json.text, /\\n/);
});


