import { useEffect, useRef, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Dialog } from '@base-ui/react/dialog';
import { BookOpen, ChartNoAxesCombined, Globe2, LayoutDashboard, LibraryBig, Menu, ScanLine, Settings2, UsersRound, Wallet, WandSparkles, Workflow, X } from 'lucide-react';
import { Button, Logo, Modal, cn, PageTransition } from './components/ui';
import { WorkspaceSearch } from './components/workspace';
import { WorkspaceProvider, useWorkspace } from './data/WorkspaceProvider';
import { Students, Attendance, Payments } from './features/Operations';
import { Materials, Studio } from './features/Teaching';
import { Overview, Automations, Analytics } from './features/Management';
import { saveFile } from './utils/exports';

const navigation = [
  { group: ['Daily operations', 'العمليات اليومية'], items: [
    { id: 'overview', icon: LayoutDashboard, label: ['Overview', 'نظرة عامة'], Page: Overview },
    { id: 'students', icon: UsersRound, label: ['Students & groups', 'الطلاب والمجموعات'], Page: Students },
    { id: 'attendance', icon: ScanLine, label: ['Sessions & attendance', 'الحصص والحضور'], Page: Attendance },
    { id: 'payments', icon: Wallet, label: ['Charges & collections', 'الرسوم والتحصيلات'], Page: Payments },
  ] },
  { group: ['Teaching & content', 'التدريس والمحتوى'], items: [
    { id: 'studio', icon: WandSparkles, label: ['AI studio', 'استوديو الذكاء الاصطناعي'], Page: Studio },
    { id: 'materials', icon: LibraryBig, label: ['Material library', 'مكتبة المذكرات'], Page: Materials },
  ] },
  { group: ['Management & reports', 'الإدارة والتقارير'], items: [
    { id: 'automations', icon: Workflow, label: ['Automations', 'الأتمتة'], Page: Automations },
    { id: 'analytics', icon: ChartNoAxesCombined, label: ['Insights & reports', 'التحليلات والتقارير'], Page: Analytics },
  ] },
];
function Workspace() {
  const { role, setRole, data, lang, setLang, t, pick, can, notice, readOnly, error, errorText, loading, refresh, service } = useWorkspace();
  const [hash, setHash] = useState(location.hash || '#overview'), [mobile, setMobile] = useState(false), [settings, setSettings] = useState(false), [diagnostic, setDiagnostic] = useState(false);
  const mainRef = useRef(null);
  const id = hash.slice(1).split('?')[0], entry = navigation.flatMap(g => g.items).find(n => n.id === id);
  useEffect(() => { const change = () => { setHash(location.hash || '#overview'); setMobile(false); mainRef.current?.focus(); window.scrollTo({ top: 0 }); }; window.addEventListener('hashchange', change); return () => window.removeEventListener('hashchange', change); }, []);
  useEffect(() => { document.title = `${entry ? pick(entry.label) : t('Page unavailable', 'الصفحة غير متاحة')} · EduFlow AI`; }, [id, lang]);
  const chooseRole = value => { setRole(value); location.hash = 'overview'; };
  const sidebar = <><a href="#overview" className="logo-link" aria-label={t('EduFlow AI · Return to overview', 'EduFlow AI · العودة للرئيسية')}><Logo /></a><div className="workspace-picker"><span className="workspace-avatar">N</span><span className="workspace-name"><strong>{t('Nile Learning Center', 'سنتر النيل التعليمي')}</strong><small>{t('Africa/Cairo · EGP', 'توقيت القاهرة · جنيه مصري')}</small></span></div><nav aria-label={t('Main navigation', 'التنقل الرئيسي')} className="main-nav">{navigation.map(group => { const items = group.items.filter(n => can(n.id)); return items.length > 0 && <div className="nav-group" key={group.group[0]}><p className="nav-eyebrow">{pick(group.group)}</p>{items.map(({ id: key, label, icon: Icon }) => <a href={`#${key}`} key={key} aria-current={id === key ? 'page' : undefined} className={cn('nav-link', id === key && 'active')}><Icon size={19} strokeWidth={1.7} /><span>{pick(label)}</span></a>)}</div>; })}</nav><div className="sidebar-bottom"><div className="sidebar-note"><BookOpen size={24} /><h3>{t('Make room for teaching.', 'مساحة أكبر للتعليم.')}</h3><p>{t('A calmer, clearer teaching day.', 'يوم تعليمي أهدى وأوضح.')}</p></div><button className="bottom-link" onClick={() => setSettings(true)}><Settings2 size={18} />{t('Settings & demo tools', 'الإعدادات وأدوات الديمو')}</button></div></>;
  const Page = entry?.Page;
  const backup = () => {
    try { const values = {}; for (let i = 0; i < localStorage.length; i++) { const key = localStorage.key(i); if (key.startsWith('eduflow.')) values[key] = localStorage.getItem(key); } saveFile(new Blob([JSON.stringify(values, null, 2)], { type: 'application/json' }), 'EduFlow-demo-backup.json'); }
    catch { setDiagnostic('storage'); }
  };
  return <div className="app-shell"><a href="#main-content" className="skip-link" onClick={e => { e.preventDefault(); mainRef.current?.focus(); }}>{t('Skip to content', 'تخطي إلى المحتوى')}</a><aside className="sidebar desktop-sidebar">{sidebar}</aside><Dialog.Root open={mobile} onOpenChange={setMobile}><Dialog.Portal><Dialog.Backdrop className="mobile-backdrop" /><Dialog.Popup className="mobile-sidebar"><Dialog.Title className="sr-only">{t('Navigation', 'التنقل')}</Dialog.Title><Dialog.Description className="sr-only">{t('Open a workspace section', 'افتح قسماً من مساحة العمل')}</Dialog.Description><Dialog.Close className="icon-button mobile-close" aria-label={t('Close navigation', 'إغلاق القائمة')}><X size={20} /></Dialog.Close>{sidebar}</Dialog.Popup></Dialog.Portal></Dialog.Root>
    <div className="main-shell"><header className="topbar"><div className="breadcrumb"><button className="icon-button mobile-menu" aria-label={t('Open navigation', 'فتح القائمة')} onClick={() => setMobile(true)}><Menu size={20} /></button><span>EduFlow</span><span className="breadcrumb-divider" aria-hidden="true">/</span><strong>{entry ? pick(entry.label) : t('Unavailable', 'غير متاح')}</strong></div><div className="topbar-actions"><WorkspaceSearch pages={navigation.flatMap(group => group.items)} disabled={loading || Boolean(error)} /><button className="language-button" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')} aria-label={t('Switch to Arabic', 'التبديل للإنجليزية')}><Globe2 size={17} />{t('العربية', 'EN')}</button><button className="icon-button" onClick={() => setSettings(true)} aria-label={t('Settings', 'الإعدادات')}><Settings2 size={19} /></button></div></header>
      <div className="demo-toolbar"><span className="demo-label"><i className="status-dot" />{t('Local demo · sample center', 'ديمو محلي · سنتر تجريبي')}</span><label>{t('Role preview', 'معاينة الصلاحيات')}<select aria-label={t('Role preview', 'معاينة الصلاحيات')} value={role} onChange={e => chooseRole(e.target.value)}><option value="admin">{t('Administrator', 'مدير السنتر')}</option><option value="teacher">{t('Teacher', 'مدرّس')}</option><option value="secretary">{t('Secretary', 'سكرتارية')}</option></select></label><small>{t('Not authentication', 'ليست تسجيل دخول')}</small></div>
      <main id="main-content" ref={mainRef} className="main-content" tabIndex={-1}>
        {notice && <div role="status" className="recovery-note">{errorText(notice)}<Button variant="ghost" onClick={() => setSettings(true)}>{t('Backup & details', 'نسخة احتياطية وتفاصيل')}</Button></div>}
        {loading && !data ? <div className="panel structural-loading" role="status">{t('Loading workspace…', 'جارٍ تحميل مساحة العمل…')}<div /><div /><div /></div> : error ? <section className="panel feature-card" role="alert"><h1>{t('Workspace unavailable', 'مساحة العمل غير متاحة')}</h1><p>{errorText(error)}</p><Button onClick={refresh}>{t('Retry', 'إعادة المحاولة')}</Button></section> : !entry || !can(id) ? <section className="panel feature-card"><h1>{t('This page is unavailable for this role', 'الصفحة غير متاحة للصلاحية دي')}</h1><p>{t('Preview another role, or return to your overview.', 'عاين صلاحية أخرى أو ارجع للنظرة العامة.')}</p><a href="#overview" className="btn btn-primary">{t('Go to overview', 'العودة للرئيسية')}</a></section> : data && <AnimatePresence mode="wait"><PageTransition routeKey={`${role}/${hash}`}><Page /></PageTransition></AnimatePresence>}
      </main><footer className="app-footer"><span>© {new Date().getFullYear()} EduFlow AI</span><span>{t('Local demo · no files or messages sent externally', 'ديمو محلي · لا يتم إرسال ملفات أو رسائل خارجياً')}</span></footer>
    </div><Modal open={settings} onClose={() => setSettings(false)} title={t('Workspace settings', 'إعدادات مساحة العمل')} description={t('Clear demo boundaries and recoverable data.', 'حدود الديمو واضحة والبيانات قابلة للاسترجاع.')}><div className="feature-form"><label className="field"><span>{t('Workspace language', 'لغة مساحة العمل')}</span><select value={lang} onChange={e => setLang(e.target.value)}><option value="en">English</option><option value="ar">العربية</option></select></label><p className="info-note">{t('Role switching is a preview, not security. The backend must authenticate each request and enforce center isolation. This app has no live adapter because no API contract is confirmed.', 'تغيير الصلاحية معاينة وليس حماية. الـBackend لازم يتحقق من كل طلب ويعزل بيانات السناتر. لا يوجد ربط حي لأن عقد API لم يتم تأكيده.')}</p><Button variant="secondary" onClick={backup}>{t('Download workspace & recovery backups', 'تنزيل نسخة مساحة العمل ونسخ الاسترجاع')}</Button><Button variant="secondary" disabled={Boolean(diagnostic) || readOnly} onClick={() => { service.failNextMutation(); setDiagnostic('armed'); }}>{t('Simulate next save failure', 'محاكاة فشل الحفظ القادم')}</Button>{diagnostic && <p role="status">{diagnostic === 'storage' ? errorText('STORAGE') : t('The next save will fail once; fields will remain for retry.', 'الحفظ القادم هيفشل مرة واحدة؛ الحقول هتفضل لإعادة المحاولة.')}</p>}<p className="info-note">{t('Metadata-only PDFs are not stored or indexed. Generation uses a fixed bank. Scheduling, delivery and real grades require server integration. Browser storage is not encrypted or a production backup.', 'ملفات PDF بيانات وصفية فقط. التوليد يستخدم بنكاً ثابتاً. الجدولة والإرسال والدرجات الفعلية تحتاج سيرفر. تخزين المتصفح غير مشفر وليس نسخة احتياطية للإنتاج.')}</p></div></Modal>
  </div>;
}
export default function WorkspaceApp() { return <WorkspaceProvider><Workspace /></WorkspaceProvider>; }
