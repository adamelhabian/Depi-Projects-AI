export const names = [
  ['Omar Ahmed', 'عمر أحمد'], ['Salma Mahmoud', 'سلمى محمود'], ['Youssef Ali', 'يوسف علي'], ['Mariam Hassan', 'مريم حسن'],
  ['Ahmed Mostafa', 'أحمد مصطفى'], ['Farida Khaled', 'فريدة خالد'], ['Adam Mohamed', 'آدم محمد'], ['Nour Ibrahim', 'نور إبراهيم'],
  ['Malak Sherif', 'ملك شريف'], ['Seif Tarek', 'سيف طارق'], ['Jana Amr', 'جنى عمرو'], ['Ziad Emad', 'زياد عماد'],
  ['Hana Adel', 'هنا عادل'], ['Yassin Wael', 'ياسين وائل'], ['Habiba Samir', 'حبيبة سمير'], ['Kareem Nasser', 'كريم ناصر'],
  ['Laila Ashraf', 'ليلى أشرف'], ['Mostafa Hany', 'مصطفى هاني'], ['Reem Fathy', 'ريم فتحي'], ['Ali Gamal', 'علي جمال'],
  ['Aya Ehab', 'آية إيهاب'], ['Mahmoud Reda', 'محمود رضا'], ['Dina Ayman', 'دينا أيمن'], ['Mohamed Essam', 'محمد عصام'],
];
export const groups = [['Physics · Group A', 'الفيزياء · مجموعة أ'], ['Physics · Group B', 'الفيزياء · مجموعة ب'], ['Physics · Group C', 'الفيزياء · مجموعة ج']];
export const studentsSeed = names.map((name, i) => ({
  id: `EF-${1001 + i}`, name, group: i % 3,
  attendance: i % 5 === 0 ? 62 + i % 9 : 88 + i % 12,
  score: i % 5 === 0 ? 43 + i % 12 : i % 4 === 0 ? 67 : 76 + i % 22,
  trend: i % 5 === 0 ? -12 : 3 + i % 8,
  payment: i % 4 === 0 ? 'due' : 'paid', present: false,
  risk: i % 5 === 0 ? 'risk' : i % 4 === 0 ? 'watch' : 'safe',
}));
export const materialsSeed = [
  { id: 'm1', title: ['Motion & forces', 'الحركة والقوى'], subtitle: ['Grade 12 · Physics', 'الصف الثالث الثانوي · فيزياء'], pages: 24, type: 'PDF', date: '2026-10-18', cover: 'green', source: 'sample', image: '/images/material-motion.webp' },
  { id: 'm2', title: ['Electricity, made clear', 'الكهربية ببساطة'], subtitle: ['Grade 12 · Physics', 'الصف الثالث الثانوي · فيزياء'], pages: 36, type: 'PDF', date: '2026-10-16', cover: 'sand', source: 'sample', image: '/images/material-electricity.webp' },
  { id: 'm3', title: ['Waves & sound', 'الموجات والصوت'], subtitle: ['Grade 11 · Physics', 'الصف الثاني الثانوي · فيزياء'], pages: 18, type: 'PDF', date: '2026-10-14', cover: 'clay', source: 'sample', image: '/images/material-waves.webp' },
];
export const examBank = [
  { topic: 'm1', q: ['A 2 kg object accelerates at 3 m/s². What is the net force?', 'جسم كتلته 2 كجم يتحرك بعجلة 3 م/ث². ما محصلة القوى؟'], options: [['6 N', '6 نيوتن'], ['1.5 N', '1.5 نيوتن'], ['5 N', '5 نيوتن'], ['9 N', '9 نيوتن']], answer: 0, source: 8, explanation: ['Newton’s second law: F = m × a = 2 × 3 = 6 N.', 'طبقاً لقانون نيوتن الثاني: القوة = الكتلة × العجلة = 6 نيوتن.'] },
  { topic: 'm1', q: ['Which quantity describes resistance to a change in motion?', 'أي كمية تصف مقاومة الجسم لتغيير حالته الحركية؟'], options: [['Velocity', 'السرعة'], ['Mass', 'الكتلة'], ['Acceleration', 'العجلة'], ['Distance', 'المسافة']], answer: 1, source: 5, explanation: ['Mass is a measure of inertia.', 'الكتلة مقياس للقصور الذاتي.'] },
  { topic: 'm1', q: ['What happens when the net force on an object is zero?', 'ماذا يحدث عندما تكون محصلة القوى المؤثرة على جسم صفراً؟'], options: [['It must stop', 'يتوقف بالضرورة'], ['Its speed always increases', 'تزداد سرعته دائماً'], ['Its velocity remains constant', 'تظل سرعته المتجهة ثابتة'], ['Its mass decreases', 'تقل كتلته']], answer: 2, source: 6, explanation: ['Zero net force means zero acceleration.', 'انعدام محصلة القوى يعني انعدام العجلة.'] },
  { topic: 'm1', q: ['What is the SI unit of acceleration?', 'ما وحدة قياس العجلة في النظام الدولي؟'], options: [['m/s', 'م/ث'], ['kg', 'كجم'], ['N', 'نيوتن'], ['m/s²', 'م/ث²']], answer: 3, source: 3, explanation: ['Acceleration measures change in velocity per second.', 'العجلة هي معدل تغير السرعة المتجهة بالنسبة للزمن.'] },
  { topic: 'm1', q: ['A force of 10 N acts on a 5 kg object. Find its acceleration.', 'تؤثر قوة 10 نيوتن على جسم كتلته 5 كجم. احسب العجلة.'], options: [['2 m/s²', '2 م/ث²'], ['50 m/s²', '50 م/ث²'], ['0.5 m/s²', '0.5 م/ث²'], ['15 m/s²', '15 م/ث²']], answer: 0, source: 9, explanation: ['a = F / m = 10 / 5 = 2 m/s².', 'العجلة = القوة ÷ الكتلة = 2 م/ث².'] },
  { topic: 'm2', q: ['A 6 Ω resistor has a 12 V potential difference. Find the current.', 'فرق الجهد بين طرفي مقاومة 6 أوم يساوي 12 فولت. احسب شدة التيار.'], options: [['2 A', '2 أمبير'], ['72 A', '72 أمبير'], ['0.5 A', '0.5 أمبير'], ['18 A', '18 أمبير']], answer: 0, source: 7, explanation: ['Ohm’s law: I = V / R = 2 A.', 'قانون أوم: شدة التيار = فرق الجهد ÷ المقاومة = 2 أمبير.'] },
  { topic: 'm2', q: ['What is the SI unit of electrical resistance?', 'ما وحدة قياس المقاومة الكهربية؟'], options: [['Volt', 'فولت'], ['Ohm', 'أوم'], ['Ampere', 'أمبير'], ['Watt', 'وات']], answer: 1, source: 4, explanation: ['Electrical resistance is measured in ohms (Ω).', 'تُقاس المقاومة الكهربية بالأوم.'] },
  { topic: 'm2', q: ['How do resistances combine in a series circuit?', 'كيف تُحسب المقاومة المكافئة لمقاومات متصلة على التوالي؟'], options: [['Multiply them', 'نضربها'], ['Use the smallest', 'نستخدم الأصغر'], ['Add them', 'نجمعها'], ['They cancel out', 'تلغي بعضها']], answer: 2, source: 10, explanation: ['For series resistors, add their resistances.', 'في التوالي، المقاومة المكافئة تساوي مجموع المقاومات.'] },
  { topic: 'm3', q: ['Which formula connects wave speed, frequency, and wavelength?', 'ما العلاقة بين سرعة الموجة وترددها وطولها الموجي؟'], options: [['v = f × λ', 'v = f × λ'], ['v = f / λ', 'v = f / λ'], ['v = λ / f', 'v = λ / f'], ['v = f + λ', 'v = f + λ']], answer: 0, source: 4, explanation: ['Wave speed equals frequency multiplied by wavelength.', 'سرعة الموجة = التردد × الطول الموجي.'] },
];
export const defaultFlows = [
  { id: 'absence', name: ['A gentler absence follow-up', 'متابعة الغياب أولاً بأول'], desc: ['Attendance recorded → draft a parent update', 'تسجيل الغياب ← تجهيز رسالة لولي الأمر'], trigger: ['After each class', 'بعد كل حصة'], enabled: true },
  { id: 'risk', name: ['Catch a learning gap early', 'تدخل مبكر لدعم الطلاب'], desc: ['Low quiz score → prepare a remedial worksheet', 'درجة اختبار منخفضة ← تجهيز ورقة تقوية'], trigger: ['After grading', 'بعد التصحيح'], enabled: true },
  { id: 'report', name: ['A meaningful weekly update', 'ملخص أسبوعي واضح'], desc: ['Weekly results → draft a progress report', 'نتائج الأسبوع ← إعداد تقرير متابعة'], trigger: ['Every Thursday', 'كل خميس'], enabled: false },
];
export const weekStats = [
  { day: 'Sat', ar: 'سبت', attendance: 88, score: 70 }, { day: 'Sun', ar: 'أحد', attendance: 93, score: 76 },
  { day: 'Mon', ar: 'إثنين', attendance: 85, score: 73 }, { day: 'Tue', ar: 'ثلاثاء', attendance: 96, score: 82 },
  { day: 'Wed', ar: 'أربعاء', attendance: 91, score: 78 }, { day: 'Thu', ar: 'خميس', attendance: 94, score: 84 },
];
