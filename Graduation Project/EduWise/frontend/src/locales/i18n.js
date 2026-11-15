export const messages = {
  VALIDATION: ['Check the required fields.', 'راجع البيانات المطلوبة.'], NOT_FOUND: ['The record is no longer available. Refresh the workspace.', 'السجل لم يعد متاحاً. حدّث مساحة العمل.'],
  FORBIDDEN: ['This role cannot perform this action.', 'الصلاحية الحالية لا تسمح بالعملية.'], CONFLICT: ['Data changed in another action or tab. Refresh, check your entries and submit again.', 'البيانات اتغيرت في عملية أو تبويب آخر. حدّث وراجع مدخلاتك ثم احفظ مجدداً.'],
  DUPLICATE_CODE: ['Student codes must be unique in this center, including archived students.', 'كود الطالب لازم يكون فريداً داخل السنتر، حتى للطلاب المؤرشفين.'],
  DUPLICATE_ENROLLMENT: ['This student already has an overlapping enrollment in this group.', 'الطالب مشترك بالفعل في المجموعة خلال نفس الفترة.'],
  DUPLICATE_SESSION: ['A session already exists for this group at this date and time.', 'توجد حصة للمجموعة في نفس اليوم والوقت.'],
  DUPLICATE_ATTENDANCE: ['Already recorded with this status for this session. No duplicate was created.', 'الحالة مسجلة بالفعل لهذه الحصة. لم يتم إنشاء سجل مكرر.'],
  NOT_ENROLLED: ['Student is not enrolled in the selected group on this session date.', 'الطالب غير مشترك في المجموعة بتاريخ الحصة المحددة.'], ARCHIVED: ['Archived records cannot receive new activity. Historical records are retained.', 'السجلات المؤرشفة لا تقبل عمليات جديدة. التاريخ محفوظ.'],
  MONEY: ['Enter a positive EGP amount with at most two decimal places.', 'اكتب مبلغاً بالجنيه المصري بمنزلتين عشريتين بحد أقصى.'], PHONE: ['Enter a valid phone number.', 'اكتب رقم تليفون صالحاً.'], DATE: ['Check the calendar date and session time.', 'راجع التاريخ ووقت الحصة.'],
  DUPLICATE_REFERENCE: ['This payment reference has already been used in this center, even if voided.', 'مرجع التحصيل مستخدم في السنتر بالفعل، حتى لو الإيصال ملغي.'], PAYMENT_LIMIT: ['The amount must not exceed the outstanding charge or refundable payment.', 'المبلغ يجب ألا يتجاوز المتبقي من الرسوم أو المتاح للاسترداد.'],
  IDEMPOTENCY_CONFLICT: ['This retry key belongs to different entries. Reload and check the ledger before resubmitting.', 'مفتاح إعادة المحاولة مرتبط ببيانات مختلفة. أعد التحميل وراجع الدفتر قبل الحفظ.'],
  REQUEST_FAILED: ['Simulated request failure. Your entries are unchanged; retry to save.', 'فشل طلب تجريبي. مدخلاتك محفوظة؛ جرّب الحفظ مرة أخرى.'],
  STORAGE: ['Browser storage is unavailable or full. No mutation was committed. Export a backup or free space, then reload.', 'تخزين المتصفح غير متاح أو ممتلئ. لم يتم حفظ العملية. صدّر نسخة احتياطية أو وفّر مساحة ثم أعد التحميل.'],
  CORRUPT: ['Stored data is invalid. Reload to recover from a preserved backup.', 'البيانات المحفوظة غير صالحة. أعد التحميل للاسترجاع مع الاحتفاظ بنسخة من الأصل.'],
  FUTURE_VERSION: ['Newer demo data was detected. This view is read-only; the original data was not overwritten.', 'تم اكتشاف بيانات من نسخة أحدث. العرض للقراءة فقط ولم تُستبدل البيانات الأصلية.'],
  MIGRATED: ['Your previous demo was migrated. Unscoped attendance, payment labels and old AI drafts are preserved in the legacy backup, not treated as verified records.', 'تم ترحيل الديمو السابق. الحضور غير المرتبط بحصة وعلامات الدفع ومسودات AI القديمة محفوظة في الأرشيف، وليست سجلات مؤكدة.'],
  RECOVERED: ['Invalid demo data was backed up before a fresh sample workspace was opened. Download the backup from settings.', 'تم نسخ البيانات غير الصالحة احتياطياً قبل فتح ديمو جديد. حمّل النسخة من الإعدادات.'],
  PDF_LIMIT: ['Choose a PDF file, no larger than 15 MB.', 'اختار ملف PDF لا يتجاوز 15 ميجابايت.'], PDF_HEADER: ['The file does not have a valid PDF header.', 'الملف لا يحتوي على ترويسة PDF صالحة.'],
  INDEXING_UNAVAILABLE: ['Metadata saved only. Document storage and indexing require a backend. Choose a ready demo chapter or reselect the original file after integration.', 'تم حفظ البيانات الوصفية فقط. تخزين وفهرسة المستند يحتاجان Backend. اختار فصلاً تجريبياً جاهزاً أو أعد اختيار الملف الأصلي بعد الربط.'],
  SOURCE_REQUIRED: ['Select at least one ready material.', 'اختار مذكرة جاهزة واحدة على الأقل.'], NOT_READY: ['Only ready materials can be used for generation.', 'التوليد متاح للمذكرات الجاهزة فقط.'],
  UNSUPPORTED_SOURCE: ['Selected material does not match the subject and grade.', 'المذكرات المحددة لا تطابق المادة والصف.'], UNSUPPORTED_REQUEST: ['The demo bank does not support this request.', 'بنك الديمو لا يدعم الطلب ده.'],
  INSUFFICIENT_QUESTIONS: ['Not enough demo questions match these filters. Reduce the count, add ready sources or change difficulty.', 'الأسئلة التجريبية لا تكفي للفلاتر دي. قلل العدد أو أضف مصادر جاهزة أو غيّر المستوى.'],
  ESSAY_LENGTH: ['Enter an answer of 15–20,000 characters.', 'اكتب إجابة بين 15 و20 ألف حرف.'], RUBRIC: ['Score every criterion within its maximum and explain the override.', 'حدد درجة لكل معيار في حدود الحد الأقصى ووضح سبب التعديل.'],
  FLOW_DISABLED: ['Activate the workflow before running the demo.', 'فعّل سير العمل قبل تشغيل الديمو.'], DUPLICATE_EVENT: ['This workflow already produced follow-up for this session. Review the existing run.', 'سير العمل أنشأ المتابعة لهذه الحصة بالفعل. راجع التشغيل الموجود.'],
  NO_EVIDENCE: ['No matching recorded attendance. Unrecorded students are not counted as absent.', 'لا توجد سجلات حضور مطابقة. غير المسجلين لا يُعتبروا غائبين.'], REVIEW_REQUIRED: ['Review the draft before approval or export.', 'راجع المسودة قبل الاعتماد أو التصدير.'], APPROVED_LOCKED: ['Approved drafts are read-only; nothing has been delivered.', 'المسودات المعتمدة للقراءة فقط؛ لم يتم إرسال أي شيء.'],
  EXPORT: ['Export failed. Your draft is saved; retry.', 'تعذر التصدير. المسودة محفوظة؛ جرّب مجدداً.'],
  INVALID_DATE_RANGE: ['Start date must be on or before end date.', 'تاريخ البداية لازم يكون قبل تاريخ النهاية أو مساوي له'],
};
export const translateError = (error, lang) => (messages[error?.code || error] || messages.VALIDATION)[lang === 'ar' ? 1 : 0];
export const isValidDateRange = (from, to) => !from || !to || from <= to;
export const dateRangeErrorText = lang => lang === 'ar' ? 'تاريخ البداية لازم يكون قبل تاريخ النهاية أو مساوي له' : 'Start date must be on or before end date.';
export const paymentMethods = {
  cash: ['Cash', 'نقدي'],
  card: ['Card', 'بطاقة'],
  transfer: ['Bank transfer', 'تحويل بنكي'],
};
export const translatePaymentMethod = (method, lang) => paymentMethods[method]?.[lang === 'ar' ? 1 : 0] || method;
export const grades = {
  '11': ['Grade 11', 'الصف الثاني الثانوي'],
  '12': ['Grade 12', 'الصف الثالث الثانوي'],
};
export const formatGrade = (grade, lang) => {
  if (!grade) return '';
  const key = String(grade).trim();
  if (grades[key]) return grades[key][lang === 'ar' ? 1 : 0];
  return lang === 'ar' ? `الصف ${key}` : `Grade ${key}`;
};
export const userRoles = {
  admin: ['Center Manager', 'مدير السنتر'],
  teacher: ['Teacher', 'مدرّس'],
  secretary: ['Secretary', 'سكرتارية'],
};
export const translateUserRole = (role, lang) => userRoles[role]?.[lang === 'ar' ? 1 : 0] || role;
export const resolveEmployeeDisplay = (userId, users = [], lang = 'ar') => {
  if (!userId) return lang === 'ar' ? 'غير متاح' : 'Not available';
  const user = users.find(u => u.id === userId);
  if (user?.name) {
    if (Array.isArray(user.name)) {
      return lang === 'ar' ? (user.name[1] || user.name[0]) : (user.name[0] || user.name[1]);
    }
    if (typeof user.name === 'string' && user.name.trim()) return user.name.trim();
  }
  if (user?.role) {
    return translateUserRole(user.role, lang);
  }
  return lang === 'ar' ? 'غير متاح' : 'Not available';
};
export const statusLabels = {
  present: ['Present', 'حاضر'], late: ['Late', 'متأخر'], absent: ['Absent', 'غائب'], excused: ['Excused', 'بعذر'], unrecorded: ['Not recorded', 'غير مسجل'],
  active: ['Active', 'نشط'], archived: ['Archived', 'مؤرشف'], draft: ['Draft', 'مسودة'], reviewed: ['Reviewed', 'تمت المراجعة'], approved: ['Approved · not delivered', 'معتمد · لم يُرسل'],
  ready: ['Ready · demo bank', 'جاهز · بنك تجريبي'], failed: ['Failed', 'فشل'], uploading: ['Uploading', 'جارٍ الرفع'], processing: ['Processing', 'جارٍ التجهيز'], succeeded: ['Succeeded · demo', 'نجح · تجريبي'], 'teacher-reviewed': ['Teacher reviewed · not a final grade', 'مراجعة مدرس · ليست درجة نهائية'],
};
export const formatMoney = (minor, lang) => new Intl.NumberFormat(lang === 'ar' ? 'ar-EG-u-nu-latn' : 'en-EG', { style: 'currency', currency: 'EGP' }).format(minor / 100);
export const formatDate = (date, lang, instant = false) => new Intl.DateTimeFormat(lang === 'ar' ? 'ar-EG-u-nu-latn' : 'en-GB', { timeZone: 'Africa/Cairo', dateStyle: 'medium', ...(instant ? { timeStyle: 'short' } : {}) }).format(new Date(instant ? date : `${date}T12:00:00Z`));
