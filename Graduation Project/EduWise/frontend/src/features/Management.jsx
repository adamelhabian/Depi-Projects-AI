import { useState } from 'react';
import { Switch } from '@base-ui/react/switch';
import {
  ArrowUpRight, BookOpen, CheckCheck, ClipboardList, UsersRound, Wallet, Workflow,
  TrendingUp, BarChart3, Sparkles, Calendar, Layers
} from 'lucide-react';
import { useAction, useWorkspace } from '../data/WorkspaceProvider';
import { calendarDate, eligible, outstanding } from '../domain/workspace';
import { Button, Feedback, Field, Heading, NoRecords, Status, Submit, Table, AnimatedCounter, InteractiveItem, AnimatedSegmented } from '../components/ui';
import { WorkspaceShortcuts, TeachingSpotlight } from '../components/workspace';
import { OverviewEvidence, OverviewAnalyticsWidget } from '../components/analytics';
import { examBank } from '../data/mockData';

function SecretaryFinancialPulse() {
  const { data, t, money } = useWorkspace();
  const uncollected = outstanding(data);
  const receiptsCount = data.payments.length;

  return (
    <section className="panel feature-card secretary-pulse-card" aria-label={t('Daily financial pulse', 'نبض التحصيلات اليومية')}>
      <div className="section-heading">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Wallet size={20} style={{ color: 'var(--md-sys-color-primary, #315da8)' }} />
          <h2 style={{ margin: 0 }}>{t('Collections & cash register pulse', 'نبض التحصيلات والخزينة')}</h2>
        </div>
        <a className="text-link" href="#payments">
          {t('Open payments ledger', 'فتح دفتر التحصيلات')}
          <ArrowUpRight size={14} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} />
        </a>
      </div>
      <p style={{ margin: '4px 0 16px', fontSize: '13px', color: 'var(--md-sys-color-on-surface-variant, #44474f)' }}>
        {t('Track daily receipt activity, active enrollments, and pending student dues in one glance.', 'متابعة حركة الإيصالات اليومية، اشتراكات الطلاب النشطة، والمستحقات المعلقة في مكان واحد.')}
      </p>
      <div className="stats-grid overview-stats" style={{ marginTop: '0', marginBottom: '16px' }}>
        <InteractiveItem as="a" className="stat-card metric-link" href="#payments">
          <div className="stat-top">
            <span>{t('Total receipts issued', 'إجمالي الإيصالات المسجلة')}</span>
            <ClipboardList size={18} />
          </div>
          <div className="stat-value">
            <AnimatedCounter value={receiptsCount} />
          </div>
          <p>{t('View recorded receipts', 'عرض الإيصالات المسجلة')} <ArrowUpRight size={13} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} /></p>
        </InteractiveItem>
        <InteractiveItem as="a" className="stat-card metric-link" href="#payments?outstanding=1">
          <div className="stat-top">
            <span>{t('Pending student dues', 'مستحقات طلاب معلقة')}</span>
            <Wallet size={18} />
          </div>
          <div className="stat-value">
            <AnimatedCounter value={money(uncollected)} />
          </div>
          <p>{t('Filter unpaid students', 'تصفية الطلاب غير المسددين')} <ArrowUpRight size={13} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} /></p>
        </InteractiveItem>
      </div>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
        <a href="#payments" className="btn btn-primary btn-sm">
          <Wallet size={15} />
          {t('Record a payment & issue receipt', 'تسجيل تحصيل وإصدار إيصال')}
        </a>
        <a href="#students" className="btn btn-secondary btn-sm">
          <UsersRound size={15} />
          {t('Browse student profiles', 'تصفح ملفات الطلاب')}
        </a>
      </div>
    </section>
  );
}

export function Overview() {
  const { data, role, t, pick, money, date, can } = useWorkspace(), today = calendarDate();
  const todaySessions = data.sessions.filter(s => s.date === today), records = data.attendance.filter(a => todaySessions.some(s => s.id === a.sessionId));
  const dashboardSessions = role === 'teacher' ? data.sessions.filter(s => s.date >= today).sort((a, b) => (a.date + a.startTime).localeCompare(b.date + b.startTime)) : todaySessions;
  const metrics = [
    { label: t('Active students', 'الطلاب النشطون'), value: data.students.filter(s => s.status === 'active').length, icon: UsersRound, href: '#students' },
    { label: t('Today’s recorded attendance', 'سجلات حضور اليوم'), value: records.length, icon: ClipboardList, href: '#attendance' },
    can('payments') ? { label: t('Outstanding balance', 'الرصيد المتبقي'), value: money(outstanding(data)), icon: Wallet, href: '#payments?outstanding=1' } : { label: t('Ready sources', 'المصادر الجاهزة'), value: data.materials.filter(m => m.status === 'ready').length, icon: BookOpen, href: '#materials' },
    can('studio') ? { label: t('Exam drafts to review', 'اختبارات تنتظر المراجعة'), value: data.drafts.filter(d => d.kind === 'exam' && d.status === 'draft').length, icon: CheckCheck, href: '#studio' } : { label: t('Today’s sessions', 'حصص اليوم'), value: todaySessions.length, icon: ClipboardList, href: '#attendance' },
  ];
  const roles = { admin: [t('Your center, at a glance.', 'سنترك كله، في نظرة.'), t('Review collections, sessions and what needs your attention.', 'راجع التحصيلات والحصص والحاجات اللي محتاجة متابعتك.')], teacher: [t('More room for teaching.', 'مساحة أكبر للتدريس.'), t('Your assigned groups, lesson preparation and drafts to review.', 'مجموعاتك المخصصة وتحضير الحصص والمسودات المطلوبة للمراجعة.')], secretary: [t('A well-organized day starts here.', 'يوم منظم، يبدأ من هنا.'), t('Today’s sessions, the student directory and clear collections.', 'حصص اليوم ودليل الطلاب وتحصيلات واضحة.')] };
  return <><Heading title={t('Good morning, Youssef', 'صباح الخير، يوسف')} description={`${date(today)} · ${t('Africa/Cairo · local demo observations', 'توقيت القاهرة · بيانات ديمو محلية')}`} />
    <section className="hero-banner compact-hero"><div className="hero-copy"><div className="hero-eyebrow"><span className="small-dot" />{t('MAKE ROOM FOR TEACHING', 'يوم تعليمي أهدى وأوضح')}</div><h2>{roles[role][0]}</h2><p>{roles[role][1]}</p><div className="hero-actions"><a className="btn btn-primary btn-sm" href={role === 'teacher' ? '#studio' : '#attendance'}>{role === 'teacher' ? t('Prepare a lesson', 'تجهيز حصة') : t('Open today’s register', 'فتح كشف اليوم')}<ArrowUpRight size={15} className="directional" /></a></div></div><div className="hero-image-wrap"><img className="hero-image" width="1536" height="1024" fetchPriority="high" src="/images/educator-blue.webp" alt={t('Teacher preparing a lesson in a blue and cream studio', 'مدرّسة تجهّز حصة في مساحة زرقاء وفاتحة')} /></div></section>
    <div className="stats-grid overview-stats">{metrics.map(({ label, value, icon: Icon, href }) => <InteractiveItem as="a" className="stat-card metric-link" key={href} href={href}><div className="stat-top"><span>{label}</span><Icon size={18} /></div><div className="stat-value"><AnimatedCounter value={value} /></div><p>{t('Open matching records', 'عرض السجلات المرتبطة')} <ArrowUpRight size={13} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} /></p></InteractiveItem>)}</div>
    <WorkspaceShortcuts />
    <div className="dashboard-two-col"><section className="panel feature-card"><div className="section-heading"><h2>{role === 'teacher' ? t('Today & upcoming sessions', 'حصص اليوم والحصص القادمة') : t('Today’s sessions', 'حصص اليوم')}</h2><a className="text-link" href="#attendance">{t('Open register', 'فتح الكشف')}</a></div>{dashboardSessions.length ? dashboardSessions.map(s => <InteractiveItem as="a" className="session-link" key={s.id} href={`#attendance?sessionId=${s.id}`}><span className="session-time"><bdi>{s.startTime}</bdi></span><span><strong>{pick(data.groups.find(g => g.id === s.groupId)?.name)}</strong><small>{pick(s.title)} · {date(s.date)} · {data.attendance.filter(a => a.sessionId === s.id).length} {t('recorded', 'سجلات')}</small></span><ArrowUpRight size={16} className="directional" /></InteractiveItem>) : <NoRecords action={t('Create a session', 'إنشاء حصة')} onAction={() => { location.hash = 'attendance'; }} />}</section><section className="panel feature-card"><h2>{role === 'teacher' ? t('Your assigned groups', 'مجموعاتك المخصصة') : t('A clear next step', 'خطوتك الجاية واضحة')}</h2>{role === 'teacher' ? data.groups.map(g => <InteractiveItem as="a" className="session-link" key={g.id} href={`#students?groupId=${g.id}`}>{pick(g.name)}<ArrowUpRight size={16} className="directional" /></InteractiveItem>) : <><p>{t('Not-recorded attendance is missing data, not absence. Use the session register before preparing a follow-up.', 'الحضور غير المسجل بيانات ناقصة، مش غياب. سجّل الحصة قبل تجهيز المتابعة.')}</p><a href="#students" className="btn btn-secondary">{t('Manage students & enrollments', 'إدارة الطلاب والاشتراكات')}</a>{can('analytics') && <a href="#analytics" className="text-link">{t('Review operational report', 'مراجعة تقرير العمليات')}</a>}{can('payments') && role === 'secretary' && <a href="#payments" className="text-link">{t('Review collections & receipt ledger', 'متابعة دفتر التحصيلات والإيصالات')} <ArrowUpRight size={14} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} /></a>}</>}</section></div>
    {can('analytics') && <OverviewAnalyticsWidget />}
    {can('analytics') && <OverviewEvidence />}
    {role === 'secretary' && <SecretaryFinancialPulse />}
    <TeachingSpotlight />
  </>;
}
function AutomationDraft({ draft }) {
  const { t, lang, pick, date } = useWorkspace(), action = useAction(); const [content, setContent] = useState([...draft.content]), [dirty, setDirty] = useState(false); const i = lang === 'ar' ? 1 : 0;
  return <article className="panel feature-card"><div className="section-heading"><h3>{t('Follow-up draft', 'مسودة متابعة')}</h3><Status value={dirty ? 'draft' : draft.status} /></div><small>{date(draft.createdAt, true)} · <bdi>{draft.id}</bdi></small><form noValidate className="feature-form" onSubmit={e => { e.preventDefault(); action.run('automation.edit', { draftId: draft.id, content }, () => setDirty(false)); }}><Field label={t('Message · English and Arabic stored separately', 'الرسالة · العربية والإنجليزية محفوظتان منفصلتين')}><textarea className="resize-none" disabled={draft.status === 'approved'} required maxLength={10000} value={content[i]} onChange={e => { setContent(content.map((x, j) => j === i ? e.target.value : x)); setDirty(true); }} /></Field><Feedback action={action} /><div className="row-actions"><Submit action={{ ...action, busy: action.busy || draft.status === 'approved' || !dirty }}>{t('Save edit', 'حفظ التعديل')}</Submit><Button variant="secondary" disabled={dirty || action.busy || draft.status !== 'draft'} onClick={() => action.run('automation.review', { draftId: draft.id })}>{t('Mark reviewed', 'تأكيد المراجعة')}</Button><Button variant="secondary" disabled={dirty || action.busy || draft.status !== 'reviewed'} onClick={() => action.run('automation.approve', { draftId: draft.id })}>{t('Approve draft', 'اعتماد المسودة')}</Button></div></form><p className="info-note">{t('Delivery unavailable. Approval does not send a message.', 'الإرسال غير متاح. اعتماد المسودة لا يرسل رسالة.')}</p>{draft.reviewedAt && <small>{t('Reviewed:', 'تمت المراجعة:')} {date(draft.reviewedAt, true)}</small>}{draft.approvedAt && <small>{t('Approved:', 'تم الاعتماد:')} {date(draft.approvedAt, true)}</small>}</article>;
}
function WorkflowCard({ flow }) {
  const { data, t, pick } = useWorkspace(), action = useAction(); const [sessionId, setSession] = useState(data.sessions[0]?.id || '');
  return <section className="panel feature-card"><Workflow size={25} /><h2>{flow.id === 'absence' ? t('Absence follow-up', 'متابعة الغياب') : t('Session summary', 'ملخص الحصة')}</h2><p>{flow.id === 'absence' ? t('Recorded absence → draft parent update. Not-recorded students are excluded.', 'غياب مسجل ← مسودة رسالة لولي الأمر. غير المسجلين مستبعدين.') : t('Recorded session attendance → summary draft. No scheduled weekly run.', 'سجلات حضور الحصة ← مسودة ملخص. لا يوجد تشغيل أسبوعي مجدول.')}</p><label className="switch-label"><Switch.Root className="flow-switch" checked={flow.enabled} disabled={action.busy} onCheckedChange={enabled => action.run('automation.configure', { workflowId: flow.id, enabled })}><Switch.Thumb className="flow-switch-thumb" /></Switch.Root>{t('Workflow active · demo', 'سير العمل مفعّل · تجريبي')}</label><Field label={t('Trigger event · session', 'الحدث المحفّز · الحصة')}><select value={sessionId} onChange={e => setSession(e.target.value)}>{data.sessions.map(s => <option key={s.id} value={s.id}>{s.date} · {s.startTime} · {pick(data.groups.find(g => g.id === s.groupId)?.name)}</option>)}</select></Field><Button disabled={!flow.enabled || action.busy || !sessionId} onClick={() => action.run('automation.run', { workflowId: flow.id, sessionId })}>{t('Run once · demo', 'تشغيل مرة · تجريبي')}</Button><Feedback action={action} /><p className="info-note">{t('Scheduling and delivery are unavailable until integrated.', 'الجدولة والإرسال غير متاحين قبل الربط.')}</p></section>;
}
export function Automations() {
  const { data, t, date, errorText } = useWorkspace(), drafts = data.drafts.filter(d => d.kind === 'automation');
  return <><Heading title={t('Automations', 'الأتمتة')} description={t('Configure → run → edit → review → approve. Delivery remains separate.', 'إعداد ← تشغيل ← تعديل ← مراجعة ← اعتماد. الإرسال خطوة مستقلة.')} /><div className="feature-grid two-columns">{data.workflows.map(f => <WorkflowCard key={f.id} flow={f} />)}</div><section className="panel ledger-panel"><h2>{t('Run history', 'سجل التشغيل')}</h2><Table caption={t('Automation runs', 'مرات تشغيل الأتمتة')} headers={[t('Event key', 'مفتاح الحدث'), t('State', 'الحالة'), t('Started / completed', 'البداية / الانتهاء'), t('Result', 'النتيجة')]}>{data.automationRuns.map(r => <tr key={r.id}><td><bdi dir="ltr">{r.eventKey}</bdi></td><td><Status value={r.status} /></td><td>{date(r.startedAt, true)}<small className="cell-detail">{date(r.completedAt, true)}</small></td><td>{r.failure ? errorText(r.failure) : `${r.draftIds.length} ${t('drafts', 'مسودات')}`}</td></tr>)}</Table>{!data.automationRuns.length && <p className="info-note">{t('No runs yet. Activate a workflow and select a recorded session.', 'لم يتم التشغيل بعد. فعّل سير العمل واختار حصة مسجلة.')}</p>}</section><h2 className="subheading">{t('Review outbox · nothing is sent', 'صندوق المراجعة · لم يتم إرسال شيء')}</h2><div className="feature-grid two-columns">{drafts.map(d => <AutomationDraft key={d.id} draft={d} />)}</div>{!drafts.length && <NoRecords action={t('Record a session first', 'تسجيل الحصة أولاً')} onAction={() => { location.hash = 'attendance'; }} />}</>;
}
export { default as Analytics } from '../components/analytics/OperationalAnalytics';

