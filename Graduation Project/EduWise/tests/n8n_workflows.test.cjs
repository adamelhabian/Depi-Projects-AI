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
      for (const edge of (connection.main ?? []).flat().filter(Boolean)) assert.ok(nodes.has(edge.node));
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
  assert.match(result.json.text, /Algebra &amp; Calculus/);
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
  assert.match(result.json.text, /^📊 <b>النتيجة/);
  assert.match(result.json.text, /👤/);
  assert.match(result.json.text, /📊/);
  assert.match(result.json.text, /✅/);
  assert.match(result.json.text, /<code>/);
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

test('the Telegram bot routes general text questions to inquiry route with query', async () => {
  const update = event => run(homework, 'Route Private Telegram Message', { message: { ...message, ...event } });
  const inquiries = [
    'ما هي مواعيد حصص الصف الثالث الثانوي؟',
    'أين يقع مقر السنتر في مدينة نصر؟',
    'بكام سعر الملازم والاشتراك الشهري؟',
    'لو غبت حصة إزاي أقدر أعوضها؟',
  ];
  for (const q of inquiries) {
    const [res] = await update({ text: q });
    assert.equal(res.json.route, 'inquiry');
    assert.equal(res.json.chat_id, '22');
    assert.equal(res.json.query, q);
  }
});

test('/start and /help menu announces all 3 core capabilities in clean BiDi layout', async () => {
  const update = event => run(homework, 'Route Private Telegram Message', { message: { ...message, ...event } });
  for (const cmd of ['/start', '/help', 'start', 'help', '/start@EduWiseBot']) {
    const [res] = await update({ text: cmd });
    assert.equal(res.json.route, 'reply');
    assert.equal(res.json.chat_id, '22');
    const text = res.json.text;
    assert.match(text, /تصحيح الواجبات والاختبارات/);
    assert.match(text, /تنبيهات أولياء الأمور/);
    assert.match(text, /\/parent_risk/);
    assert.match(text, /\/parent_absence/);
    assert.match(text, /\/parent_ok/);
    assert.match(text, /المساعد الذكي للاستفسارات/);
    assert.match(text, /مواعيد الحصص/);
    assert.match(text, /المقرات/);
    assert.match(text, /الأسعار/);
    assert.match(text, /التعويض/);
  }
});

async function routeInquiry(query) {
  const [item] = await run(homework, 'Route Private Telegram Message', { message: { ...message, text: query } });
  return { 'Route Private Telegram Message': item.json };
}

test('Format Center Inquiry Response delivers accurate knowledge answers for schedules, fees, locations, and makeup', async () => {
  // 1. Schedule inquiry
  const schedPrev = await routeInquiry('ما هي مواعيد الحصص ومجموعات الجمعة؟');
  const [schedRes] = await run(homework, 'Format Center Inquiry Response', candidate(''), schedPrev);
  assert.equal(schedRes.json.route, 'inquiry');
  assert.match(schedRes.json.text, /الأول الثانوي/);
  assert.match(schedRes.json.text, /الثاني الثانوي/);
  assert.match(schedRes.json.text, /الثالث الثانوي|الثانوية العامة/);
  assert.match(schedRes.json.text, /الجمعة/);
  assert.match(schedRes.json.text, /الأحد/);

  // 2. Fees & Booklets inquiry
  const feesPrev = await routeInquiry('كام سعر الملازم والاشتراك الشهري؟');
  const [feesRes] = await run(homework, 'Format Center Inquiry Response', candidate(''), feesPrev);
  assert.equal(feesRes.json.route, 'inquiry');
  assert.match(feesRes.json.text, /60 جنيه/);
  assert.match(feesRes.json.text, /80 جنيه/);
  assert.match(feesRes.json.text, /550 جنيه/);
  assert.match(feesRes.json.text, /850 جنيه/);

  // 3. Locations inquiry
  const locPrev = await routeInquiry('أين يقع مقر السنتر في مدينة نصر والدقي؟');
  const [locRes] = await run(homework, 'Format Center Inquiry Response', candidate(''), locPrev);
  assert.equal(locRes.json.route, 'inquiry');
  assert.match(locRes.json.text, /مدينة نصر/);
  assert.match(locRes.json.text, /عباس العقاد/);
  assert.match(locRes.json.text, /الدقي/);
  assert.match(locRes.json.text, /شارع التحرير/);
  assert.match(locRes.json.text, /01012345678/);

  // 4. Makeup & Absence policy inquiry
  const makeupPrev = await routeInquiry('لو غبت حصة إزاي أقدر أعوض؟');
  const [makeupRes] = await run(homework, 'Format Center Inquiry Response', candidate(''), makeupPrev);
  assert.equal(makeupRes.json.route, 'inquiry');
  assert.match(makeupRes.json.text, /بعذر/);
  assert.match(makeupRes.json.text, /بدون عذر/);
  assert.match(makeupRes.json.text, /السبت/);
  assert.match(makeupRes.json.text, /الثلاثاء/);
});

test('Format Center Inquiry Response formats model answers cleanly with HTML', async () => {
  const previous = {
    'Route Private Telegram Message': { chat_id: '22', query: 'مواعيد سنتر إديو وايز' }
  };
  const modelText = 'مواعيد الحصص يوم الأحد والجمعة لجميع المراحل الثانوية.';
  const [res] = await run(homework, 'Format Center Inquiry Response', candidate(modelText), previous);
  assert.equal(res.json.status, 'answered');
  assert.match(res.json.text, /مواعيد الحصص يوم الأحد والجمعة/);
  assert.doesNotMatch(res.json.text, /\\n/);
});

test('Build Demo Error Reply handles errors gracefully across all routes', async () => {
  const checkError = async (route) => {
    const prev = { 'Route Private Telegram Message': { chat_id: '22', route } };
    const [res] = await run(homework, 'Build Demo Error Reply', {}, prev);
    return res.json.text;
  };
  assert.match(await checkError('parent'), /تنبيه ولي الأمر/);
  assert.match(await checkError('inquiry'), /معالجة الاستفسار|إدارة السنتر/);
  assert.match(await checkError('homework'), /تصحيح صورة الواجب/);
});

test('the Telegram bot routes parent demo commands (/parent_risk, /parent_absence, /parent_ok) with zero regressions', async () => {
  const update = event => run(homework, 'Route Private Telegram Message', { message: { ...message, ...event } });
  const cases = [
    ['/parent_risk', 'risk'],
    ['/parent_absence', 'absence'],
    ['/parent_ok', 'ok'],
    ['/parent_risk@EduWiseBot', 'risk'],
    ['/parent_absence@EduWiseBot', 'absence'],
    ['/parent_ok@EduWiseBot', 'ok'],
    ['/risk', 'risk'],
    ['/absence', 'absence'],
    ['/ok', 'ok'],
    ['/parent risk', 'risk'],
    ['/parent absence', 'absence'],
    ['/parent ok', 'ok'],
    ['/parent', 'absence'],
  ];
  for (const [cmd, expected] of cases) {
    const [res] = await update({ text: cmd });
    assert.deepEqual(res.json, { route: 'parent', chat_id: '22', scenario: expected });
  }
});

test('zero regression on document image uploads and multi-photo media group handling', async () => {
  const update = event => run(homework, 'Route Private Telegram Message', { message: { ...message, ...event } });
  // Document image upload (PNG / JPEG)
  const doc = { file_id: 'doc_img_123', mime_type: 'image/png', file_size: 1024 * 500 };
  const [docRes] = await update({ document: doc });
  assert.equal(docRes.json.route, 'homework');
  assert.equal(docRes.json.assignment_code, 'PRACTICE');
  assert.equal(docRes.json.file_id, 'doc_img_123');

  // Media group guard (multiple photos in one post)
  const groupPhoto = [{ file_id: 'p1', width: 800, height: 600 }];
  const [groupRes] = await update({ photo: groupPhoto, media_group_id: 'album_999', caption: 'واجب' });
  assert.equal(groupRes.json.route, 'reply');
  assert.match(groupRes.json.text, /صورة واحدة فقط/);
});

test('Gemini Center Assistant system prompt and graph topology verification', () => {
  const assistantNode = homework.nodes.find(n => n.name === 'Gemini Center Assistant');
  assert.ok(assistantNode, 'Gemini Center Assistant node must exist');
  assert.equal(assistantNode.type, '@n8n/n8n-nodes-langchain.googleGemini');
  assert.equal(assistantNode.onError, 'continueErrorOutput');

  const sysPrompt = assistantNode.parameters.options.systemMessage;
  // 1. Schedules
  assert.match(sysPrompt, /الصف الأول الثانوي/);
  assert.match(sysPrompt, /الصف الثاني الثانوي/);
  assert.match(sysPrompt, /الصف الثالث الثانوي|الثانوية العامة/);
  assert.match(sysPrompt, /الأحد والأربعاء/);
  assert.match(sysPrompt, /الجمعة/);

  // 2. Locations
  assert.match(sysPrompt, /مدينة نصر/);
  assert.match(sysPrompt, /عباس العقاد/);
  assert.match(sysPrompt, /الدقي/);
  assert.match(sysPrompt, /شارع التحرير/);
  assert.match(sysPrompt, /01012345678/);
  assert.match(sysPrompt, /01198765432/);

  // 3. Fees & Booklets
  assert.match(sysPrompt, /80 جنيه/);
  assert.match(sysPrompt, /120 جنيه/);
  assert.match(sysPrompt, /550 جنيه/);
  assert.match(sysPrompt, /850 جنيه/);
  assert.match(sysPrompt, /60 جنيه/);

  // 4. Absence & Makeup
  assert.match(sysPrompt, /الغياب بعذر/);
  assert.match(sysPrompt, /الغياب بدون عذر/);
  assert.match(sysPrompt, /السبت/);
  assert.match(sysPrompt, /الثلاثاء/);

  // Graph topology verification
  const inquiryIf = homework.connections['Inquiry Message?'];
  assert.equal(inquiryIf.main[0][0].node, 'Gemini Center Assistant');
  assert.equal(inquiryIf.main[1][0].node, 'Send Student Telegram Feedback');

  const assistantConn = homework.connections['Gemini Center Assistant'];
  assert.equal(assistantConn.main[0][0].node, 'Format Center Inquiry Response');
  assert.equal(assistantConn.main[1][0].node, 'Build Demo Error Reply');

  const formatConn = homework.connections['Format Center Inquiry Response'];
  assert.equal(formatConn.main[0][0].node, 'Send Student Telegram Feedback');
  assert.equal(formatConn.main[1][0].node, 'Build Demo Error Reply');
});

test('Format Center Inquiry Response handles diverse Egyptian inquiries and default fallback', async () => {
  const checkAnswer = async (query) => {
    const prev = await routeInquiry(query);
    const [res] = await run(homework, 'Format Center Inquiry Response', candidate(''), prev);
    return res.json.text;
  };

  // Diverse phrasing
  const q1 = await checkAnswer('كام مصاريف أولى ثانوي في الشهر؟');
  assert.match(q1, /550 جنيه/);

  const q2 = await checkAnswer('فين عنوان فرع مدينة نصر بالتفصيل؟');
  assert.match(q2, /عباس العقاد/);

  const q3 = await checkAnswer('ممكن اعرف مواعيد تانية ثانوي يوم الأربعاء؟');
  assert.match(q3, /الأربعاء/);
  assert.match(q3, /الثاني الثانوي/);

  const q4 = await checkAnswer('لو طالب غاب بدون عذر إيه الإجراء؟');
  assert.match(q4, /بدون عذر/);

  // General query outside known keywords returns helpful guide
  const qGeneral = await checkAnswer('مساء الخير، ممكن مساعدة؟');
  assert.match(qGeneral, /مرحباً بك في سنتر EduWise التعليمي/);
  assert.match(qGeneral, /مواعيد الحصص/);
  assert.match(qGeneral, /عناوين المقرات/);
  assert.match(qGeneral, /الأسعار والاشتراكات/);
  assert.match(qGeneral, /سياسة الغياب/);
});

test('Telegram inquiry pipeline with a simulated Gemini response', async () => {
  // Step 1: Telegram incoming message
  const inquiryText = 'ما هي مواعيد مجموعات الثانوية العامة ومقر مدينة نصر؟';
  const incomingTelegramEvent = {
    message: {
      chat: { type: 'private', id: 777123 },
      from: { id: 777123, is_bot: false, first_name: 'زياد' },
      text: inquiryText
    }
  };

  // Node 1: Route Private Telegram Message
  const [routed] = await run(homework, 'Route Private Telegram Message', incomingTelegramEvent);
  assert.equal(routed.json.route, 'inquiry');
  assert.equal(routed.json.chat_id, '777123');
  assert.equal(routed.json.query, inquiryText);

  // Node 2: Is Photo Message? (evaluates routed item)
  // In n8n, false output routes to "Inquiry Message?"
  assert.equal(routed.json.route !== 'homework', true);

  // Node 3: Inquiry Message? (evaluates $json.route === 'inquiry')
  assert.equal(routed.json.route === 'inquiry', true);

  // Node 4: Gemini Center Assistant (model execution)
  const assistantNode = homework.nodes.find(n => n.name === 'Gemini Center Assistant');
  const userPrompt = assistantNode.parameters.messages.values[0].content.replace('{{ $json.query }}', routed.json.query);
  assert.match(userPrompt, /الثانوية العامة/);

  // Node 5: Format Center Inquiry Response
  const modelCandidate = candidate('مواعيد الثانوية العامة: الجمعة 2-5 عصراً والأحد 6-9 مساءً. المقر: شارع عباس العقاد بمدينة نصر.');
  const prevNodes = {
    'Route Private Telegram Message': routed.json
  };
  const [formatted] = await run(homework, 'Format Center Inquiry Response', modelCandidate, prevNodes);
  assert.equal(formatted.json.status, 'answered');
  assert.equal(formatted.json.chat_id, '777123');
  assert.equal(formatted.json.route, 'inquiry');
  assert.match(formatted.json.text, /مواعيد الثانوية العامة/);
  assert.match(formatted.json.text, /عباس العقاد/);

  // Node 6: Send Student Telegram Feedback (verifying parameter mappings)
  const telegramSendNode = homework.nodes.find(n => n.name === 'Send Student Telegram Feedback');
  assert.equal(telegramSendNode.parameters.additionalFields.parse_mode, 'HTML');
  assert.ok(
    telegramSendNode.parameters.chatId === "={{ $('Route Private Telegram Message').first().json.chat_id }}" ||
    telegramSendNode.parameters.chatId === "={{ $json.chat_id || $('Route Private Telegram Message').first().json.chat_id }}"
  );
  assert.equal(telegramSendNode.parameters.text, "={{ $json.text }}");
});

test('scoring ignores praise, checks the complete rubric and escapes Telegram HTML', async () => {
  const prior = {
    'Route Private Telegram Message': { chat_id: '22' },
    'Build Gemini Vision Request': { rubric: ['1', '2', '3', '4'].map(question_id => ({ question_id })) },
  };
  const questions = ['1', '2', '3', '4'].map((question_id, i) => ({
    question_id, status: 'scored', earned: i === 0 ? 0 : 1,
    observed: 'x_1 < 2 & x > 0', feedback_ar: 'راجع المقارنة', solution_ar: 'المساحة 154',
  }));
  const grade = async qs => (await run(homework, 'Format Feedback and Payload',
    candidate(JSON.stringify({ questions: qs, feedback_ar: 'جميع الإجابات صحيحة' })), prior))[0].json;
  const valid = await grade(questions);
  assert.equal(valid.score, 3);
  assert.equal(valid.max_score, 4);
  assert.doesNotMatch(valid.text, /جميع الإجابات صحيحة/);
  assert.match(valid.text, /x_1 &lt; 2 &amp; x &gt; 0/);
  for (const invalid of [questions.slice(0, 1), [...questions.slice(0, 3), questions[0]],
    [...questions.slice(0, 3), { ...questions[3], question_id: '5' }]]) {
    const result = await grade(invalid);
    assert.equal(result.status, 'needs_review');
    assert.equal(result.score, null);
    assert.equal(result.max_score, 4);
  }
});

test('provider errors and truncated replies use the same local center answer', async () => {
  const previous = await routeInquiry('مصاريف الاشتراك كام؟');
  const [failure] = await run(homework, 'Build Demo Error Reply', { error: 'Unavailable' }, previous);
  const [partial] = await run(homework, 'Format Center Inquiry Response', candidate('partial', 'MAX_TOKENS'), previous);
  assert.equal(failure.json.text, partial.json.text);
  assert.equal(failure.json.source, 'local');
  assert.match(failure.json.text, /550 جنيه/);
  const [ok] = await run(homework, 'Format Center Inquiry Response', candidate('<3 & >'), previous);
  assert.equal(ok.json.source, 'gemini');
  assert.equal(ok.json.text, '&lt;3 &amp; &gt;');
});

test('Laplace math keeps shifts and denominators grouped in left-to-right Telegram code', async () => {
  const previous = { 'Build Gemini Vision Request': { rubric: [] }, 'Route Private Telegram Message': { chat_id: '22' } };
  const formula = 'F(s) = e^{-(s+3)} \\left(\\frac{2}{(s+3)^{3}} + \\frac{2}{(s+3)^{2}} + \\frac{1}{s+3}\\right)';
  const question = { question_id: '1', status: 'scored', earned: 0, observed: 'x < 3', feedback_ar: 'راجع الإزاحة.',
    solution_ar: 'نطبّق الإزاحة الزمنية.\n$' + formula + '$' };
  const [item] = await run(homework, 'Format Feedback and Payload', candidate(JSON.stringify({questions:[question]})), previous);
  const message = item.json.text;
  assert.match(message, /^📊 <b>النتيجة/);
  assert.match(message, /<code>\u2066F\(s\) = e\^\(-\(s\+3\)\)/);
  assert.match(message, /2\/\(\(s\+3\)³\)/);
  assert.match(message, /1\/\(s\+3\)/);
  assert.match(message, /x &lt; 3/);
  assert.doesNotMatch(message, /\\(?:frac|left|right)|[$═─]/);
});

test('fixed rubric supplies a worked result when the model only returns marks', async () => {
  const route = {assignment_code:'HW-01', chat_id:'22'};
  const [built] = await run(homework, 'Build Gemini Vision Request', {}, {'Route Private Telegram Message':route},
    { getBinaryDataBuffer: async () => Buffer.from([255,216,255]) }, {data:{}});
  const questions = [1,1,0,1].map((earned,i) => ({question_id:String(i+1),status:'scored',earned,observed:'44',feedback_ar:'',solution_ar:''}));
  const [item] = await run(homework, 'Format Feedback and Payload', candidate(JSON.stringify({questions})), {
    'Build Gemini Vision Request': built.json, 'Route Private Telegram Message':route});
  assert.equal(item.json.score, 3);
  assert.match(item.json.text, /A = 154 cm²/);
});

test('fast vision labels are accepted only when the earned mark agrees', async () => {
  const previous = { 'Build Gemini Vision Request': {rubric: []}, 'Route Private Telegram Message': {chat_id: '22'} };
  const q = {question_id:'1', status:'incorrect', earned:0, observed:'x = 2', feedback_ar:'راجع الإشارة.', solution_ar:'باستخدام x = 1 نحصل على الناتج.\ny = 2'};
  const grade = earned => run(homework, 'Format Feedback and Payload', candidate(JSON.stringify({questions:[{...q, earned}]})), previous);
  const [result] = await grade(0);
  assert.equal(result.json.score, 0);
  assert.match(result.json.text, /باستخدام <code>\u2066x = 1\u2069<\/code> نحصل/);
  await assert.rejects(grade(1), /per-question/);
});

test('Telegram immediate processing notice node is configured to sendMessage and runs parallel to image download', () => {
  const draftNode = homework.nodes.find(n => n.name === 'Send Homework Processing Draft');
  assert.ok(draftNode, 'Send Homework Processing Draft node must exist');
  assert.equal(draftNode.type, 'n8n-nodes-base.telegram');
  assert.equal(draftNode.parameters.resource, 'message');
  assert.equal(draftNode.parameters.operation, 'sendMessage');
  assert.match(draftNode.parameters.text, /استلمت الصورة/);
  assert.equal(draftNode.onError, 'continueErrorOutput');

  // Verify parallel execution from Is Photo Message? (output 0)
  const isPhotoConnections = homework.connections['Is Photo Message?'].main[0];
  const targetNodes = isPhotoConnections.map(c => c.node);
  assert.ok(targetNodes.includes('Download Homework Image'), 'Must connect to Download Homework Image');
  assert.ok(targetNodes.includes('Send Homework Processing Draft'), 'Must connect in parallel to Send Homework Processing Draft');
});

test('Telegram rich message node is configured with RTL and fallback error connection', () => {
  const richNode = homework.nodes.find(n => n.name === 'Send Rich Student Feedback');
  assert.ok(richNode, 'Send Rich Student Feedback node must exist');
  assert.equal(richNode.type, 'n8n-nodes-base.telegram');
  assert.equal(richNode.parameters.resource ?? 'message', 'message');
  assert.equal(richNode.parameters.operation, 'sendRichMessage');
  assert.equal(richNode.parameters.richFormat ?? 'html', 'html');
  assert.equal(richNode.parameters.additionalFields?.is_rtl, true);
  assert.equal(richNode.onError, 'continueErrorOutput');

  // Verify Format Feedback connects to Send Rich Student Feedback
  const formatConnections = homework.connections['Format Feedback and Payload'].main[0];
  assert.equal(formatConnections[0].node, 'Send Rich Student Feedback');

  // Verify duplicate prevention (output 0 is terminal)
  const richOutputs = homework.connections['Send Rich Student Feedback'].main;
  assert.ok(!richOutputs[0] || richOutputs[0].length === 0, 'Success branch must terminate to avoid duplicate message');

  // Verify fallback connection on error (output 1 connects to Send Student Telegram Feedback)
  assert.equal(richOutputs[1][0].node, 'Send Student Telegram Feedback', 'Error branch must route to fallback HTML node');
});

test('rich formatting produces tg-math-block and collapsible details for homework report', async () => {
  const route = { assignment_code: 'HW-01', chat_id: '884290887' };
  const [built] = await run(homework, 'Build Gemini Vision Request', {}, { 'Route Private Telegram Message': route },
    { getBinaryDataBuffer: async () => Buffer.from([255, 216, 255]) }, { data: {} });

  const questions = [
    { question_id: '1', status: 'scored', earned: 1, observed: 'x = 4', feedback_ar: '', solution_ar: '' },
    { question_id: '2', status: 'scored', earned: 1, observed: '6x + 5', feedback_ar: '', solution_ar: '' },
    { question_id: '3', status: 'scored', earned: 0, observed: '44', feedback_ar: 'الناتج 44 هو المحيط وليس المساحة.', solution_ar: '' },
    { question_id: '4', status: 'scored', earned: 1, observed: '45°', feedback_ar: '', solution_ar: '' }
  ];

  const [item] = await run(homework, 'Format Feedback and Payload',
    candidate(JSON.stringify({ student_name: 'زياد', assignment_title: 'واجب التفاضل #HW-01', questions })),
    { 'Build Gemini Vision Request': built.json, 'Route Private Telegram Message': route });

  assert.equal(item.json.score, 3);
  assert.equal(item.json.max_score, 4);
  assert.equal(item.json.percentage, 75);

  // Standard fallback text assertions
  assert.match(item.json.text, /📊 <b>النتيجة: 3 من 4 \(75٪\)<\/b>/);
  assert.match(item.json.text, /A = 154 cm²/);

  // Rich message assertions
  const rich = item.json.rich_text;
  assert.ok(rich, 'rich_text must be present on output');
  assert.match(rich, /📊 <b>النتيجة: 3 من 4 \(75٪\)<\/b>/);
  assert.match(rich, /👤 زياد/);
  assert.match(rich, /<details><summary><b>الحل النموذجي<\/b><\/summary>/);
  assert.match(rich, /<details><summary><b>خطوات الحل والتصحيح<\/b><\/summary>/);
  assert.match(rich, /<tg-math-block>/);
});

test('Laplace formula renders in native tg-math-block with shift and cubic denominator preserved', async () => {
  const previous = { 'Build Gemini Vision Request': { rubric: [] }, 'Route Private Telegram Message': { chat_id: '99' } };
  const formula = 'F(s) = e^{-(s+3)} \\left(\\frac{2}{(s+3)^{3}} + \\frac{2}{(s+3)^{2}} + \\frac{1}{s+3}\\right)';
  const question = {
    question_id: '1',
    status: 'scored',
    earned: 0,
    observed: 'F(s) = \\frac{1}{s}',
    feedback_ar: 'راجع قانون الإزاحة الزمنية.',
    solution_ar: 'نطبّق الإزاحة الزمنية:\n$' + formula + '$'
  };

  const [item] = await run(homework, 'Format Feedback and Payload',
    candidate(JSON.stringify({ questions: [question] })), previous);

  const rich = item.json.rich_text;
  assert.ok(rich.includes('<tg-math-block>' + formula + '</tg-math-block>'));
  assert.match(rich, /<details><summary><b>خطوات الحل والتصحيح<\/b><\/summary>/);
  assert.match(rich, /نطبّق الإزاحة الزمنية:/);
});

test('Structured Output Parser format wrapping in output object is handled seamlessly', async () => {
  const previous = { 'Build Gemini Vision Request': { rubric: [] }, 'Route Private Telegram Message': { chat_id: '99' } };
  const mockStructuredOutput = {
    output: {
      student_name: 'أحمد',
      assignment_title: 'اختبار الجبر',
      questions: [
        { question_id: '1', status: 'scored', earned: 1, observed: 'x = 2', feedback_ar: '', solution_ar: 'x = 2' },
        { question_id: '2', status: 'scored', earned: 0.5, observed: 'y < 5', feedback_ar: 'راجع علامة المتباينة', solution_ar: 'y <= 5' }
      ]
    }
  };

  const [item] = await run(homework, 'Format Feedback and Payload', mockStructuredOutput, previous);
  assert.equal(item.json.score, 1.5);
  assert.equal(item.json.max_score, 2);
  assert.equal(item.json.percentage, 75);
  assert.match(item.json.rich_text, /📊 <b>النتيجة: 1\.5 من 2 \(75٪\)<\/b>/);
  assert.match(item.json.rich_text, /<details><summary>/);
});

test('Fourier transform and mixed Arabic-LaTeX solutions render equations in tg-math-block and restore missing backslashes', async () => {
  const previous = { 'Build Gemini Vision Request': { rubric: [] }, 'Route Private Telegram Message': { chat_id: '99' } };
  const rawFourier = 'تحويل فورييه لدالة المستطيل rect(t/T) يُعطى بالقانون: mathcal{F}\\{\\text{rect}(t/T)\\} = T \\text{sinc}(T f) أو \\frac{2\\sin(\\omega)}{\\omega}. بما أن T = 2، فإن التحويل هو: \\mathcal{F}(\\omega) = 2 \\text{sinc}(\\omega) = \\frac{2\\sin(\\omega)}{\\omega}.';
  const question = {
    question_id: '2',
    status: 'scored',
    earned: 0,
    observed: 'Sinc Sinc(Sin - 1/2) = 0',
    feedback_ar: 'خطأ في حساب تحويل فورييه لدالة المستطيل rec(t/2).',
    solution_ar: rawFourier
  };

  const [item] = await run(homework, 'Format Feedback and Payload',
    candidate(JSON.stringify({ questions: [question] })), previous);

  const rich = item.json.rich_text;
  assert.ok(rich.includes('<tg-math-block>\\mathcal{F}\\{\\text{rect}(t/T)\\} = T \\text{sinc}(T f)</tg-math-block>'));
  assert.ok(rich.includes('<tg-math-block>\\frac{2\\sin(\\omega)}{\\omega}</tg-math-block>'));
  assert.ok(rich.includes('<tg-math-block>\\mathcal{F}(\\omega) = 2 \\text{sinc}(\\omega) = \\frac{2\\sin(\\omega)}{\\omega}</tg-math-block>'));
  assert.match(rich, /<details><summary><b>خطوات الحل والتصحيح<\/b><\/summary>/);
  assert.ok(!rich.match(/(?<!\\)mathcal\{F\}/), 'Must not contain un-backslashed mathcal{F}');
});


