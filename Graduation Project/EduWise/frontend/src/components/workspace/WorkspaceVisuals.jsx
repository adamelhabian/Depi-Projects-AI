import { ArrowUpRight, BookOpen, Check, ClipboardCheck, FileText, UsersRound, Wallet } from 'lucide-react';
import { useWorkspace } from '../../data/WorkspaceProvider';
import { InteractiveItem } from '../ui/MotionUi';

export function WorkspaceShortcuts() {
  const { t, can } = useWorkspace();
  const tasks = [
    { permission: 'attendance', href: '#attendance', Icon: ClipboardCheck, title: t('Take attendance', 'تسجيل الحضور'), detail: t('Open the session register', 'افتح كشف الحصة') },
    { permission: 'students', href: '#students', Icon: UsersRound, title: t('Find a student', 'الوصول لطالب'), detail: t('Profiles and enrollments', 'الملفات والاشتراكات') },
    { permission: 'studio', href: '#studio', Icon: FileText, title: t('Prepare an exam', 'تجهيز اختبار'), detail: t('Start from your sources', 'ابدأ من مصادرك') },
    { permission: 'payments', href: '#payments?outstanding=1', Icon: Wallet, title: t('Review balances', 'متابعة المتبقي'), detail: t('Outstanding charges', 'الرسوم المتبقية') },
  ].filter(x => can(x.permission));
  return <section className="workspace-shortcuts" aria-label={t('Quick actions', 'إجراءات سريعة')}>{tasks.map(({ href, Icon, title, detail }) => <InteractiveItem as="a" href={href} key={href}><span className="shortcut-icon"><Icon size={21} /></span><span><strong>{title}</strong><small>{detail}</small></span><ArrowUpRight size={16} className="directional" /></InteractiveItem>)}</section>;
}

export function TeachingSpotlight() {
  const { t, can } = useWorkspace();
  if (!can('studio')) return null;
  return <section className="teaching-spotlight" aria-labelledby="teaching-spotlight-title"><div className="section-heading"><div><h2 id="teaching-spotlight-title">{t('A little preparation. A better lesson.', 'تحضير أهدى. حصة أوضح.')}</h2><p>{t('Your sources and your next draft, one step away.', 'مصادرك ومسودتك الجاية، على بُعد خطوة.')}</p></div></div><div className="spotlight-grid"><InteractiveItem as="a" className="spotlight-card" href="#materials"><img src="/images/spotlight-library.webp" alt={t('Blue lesson folders and an open notebook', 'ملفات شرح زرقاء وكراسة مفتوحة')} width="1536" height="1024" loading="lazy" /><div><span className="spotlight-label"><BookOpen size={15} />{t('Your source library', 'مكتبة مصادرك')}</span><h3>{t('A good question starts here.', 'السؤال الكويس، بيبدأ من هنا.')}</h3><span className="spotlight-action">{t('Explore materials', 'تصفّح المذكرات')}<ArrowUpRight size={17} className="directional" /></span></div></InteractiveItem><InteractiveItem as="a" className="spotlight-card" href="#studio"><img src="/images/spotlight-preparation.webp" alt={t('Teacher preparing a lesson at his desk', 'مدرّس يجهّز حصة على مكتبه')} width="1536" height="1024" loading="lazy" /><div><span className="spotlight-label"><FileText size={15} />{t('Teaching preparation', 'تجهيز المحتوى')}</span><h3>{t('Make room for your next idea.', 'مساحة لفكرة شرح جديدة.')}</h3><span className="spotlight-action">{t('Open the studio', 'افتح الاستوديو')}<ArrowUpRight size={17} className="directional" /></span></div></InteractiveItem></div></section>;
}

export function ContextBanner({ title, description, image = 'educator', children }) {
  const { t } = useWorkspace();
  const bannerImage = image === 'educator' ? '/images/educator-blue.webp' : image === 'studio' ? '/images/spotlight-preparation.webp' : `/images/${image}.webp`;
  return <section className="context-banner"><div><span className="context-eyebrow">{t('MAKE ROOM FOR TEACHING', 'مساحة أكبر للتعليم')}</span><h2>{title}</h2><p>{description}</p>{children}</div><img src={bannerImage} alt="" width="1536" height="1024" /></section>;
}

export function PreparationSteps({ hasSources, draft }) {
  const { t } = useWorkspace();
  const current = !hasSources ? 0 : !draft ? 1 : draft.status !== 'reviewed' ? 2 : 3;
  const steps = [t('Choose sources', 'اختار المصادر'), t('Prepare a draft', 'جهّز مسودة'), t('Review & export', 'راجع وصدّر')];
  return <ol className="preparation-steps" aria-label={t('Preparation progress', 'خطوات التجهيز')}>{steps.map((label, i) => <li key={i} data-complete={i < current} aria-current={i === Math.min(current, 2) && current < 3 ? 'step' : undefined}><span>{i < current ? <Check size={14} strokeWidth={2.5} style={{ display: 'inline-block', verticalAlign: 'middle' }} /> : i + 1}</span><strong>{label}</strong></li>)}</ol>;
}
