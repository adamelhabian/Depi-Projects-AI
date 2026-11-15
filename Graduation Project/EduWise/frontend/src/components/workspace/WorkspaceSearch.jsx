import { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, BookOpen, Search, UsersRound } from 'lucide-react';
import { useWorkspace } from '../../data/WorkspaceProvider';
import { Modal } from '../ui/Base';
import { SearchField } from '../ui/FeatureUi';

const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();
export function WorkspaceSearch({ pages, disabled = false }) {
  const { data, t, pick, can, role } = useWorkspace();
  const [open, setOpen] = useState(false), [query, setQuery] = useState('');
  const input = useRef(null), results = useRef(null), trigger = useRef(null);
  useEffect(() => {
    const handleKey = event => {
      if (event.isComposing || event.repeat || !(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== 'k') return;
      if (document.querySelector('[role="dialog"]') || disabled) return;
      event.preventDefault(); setOpen(true);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [disabled]);
  useEffect(() => { setOpen(false); setQuery(''); }, [role]);
  const close = () => { setOpen(false); setQuery(''); };
  const needle = normalize(query);
  const matches = text => !needle || normalize(text).includes(needle);
  const items = [
    ...pages.filter(p => can(p.id) && matches(p.label.join(' '))).map(p => ({ key: p.id, title: pick(p.label), subtitle: t('Workspace page', 'صفحة في مساحة العمل'), href: `#${p.id}`, Icon: p.icon })),
    ...(needle && can('students') ? (data?.students || []).filter(s => matches([s.code, ...s.name].join(' '))).slice(0, 6).map(s => ({ key: s.id, title: pick(s.name), subtitle: s.code, href: `#students?q=${encodeURIComponent(s.code)}&status=all`, Icon: UsersRound })) : []),
    ...(needle && can('materials') ? (data?.materials || []).filter(m => matches(m.title.join(' '))).slice(0, 4).map(m => ({ key: m.id, title: pick(m.title), subtitle: t('Material library', 'مكتبة المذكرات'), href: `#materials?q=${encodeURIComponent(pick(m.title))}`, Icon: BookOpen })) : []),
  ];
  const move = (event, index = -1) => {
    if (event.isComposing || !['ArrowDown', 'ArrowUp', 'Enter'].includes(event.key)) return;
    const links = [...(results.current?.querySelectorAll('a') || [])];
    if (event.key === 'Enter') { if (index === -1 && links.length) { event.preventDefault(); links[0].click(); } return; }
    event.preventDefault();
    if (event.key === 'ArrowUp' && index <= 0) input.current?.focus();
    else links[Math.min(Math.max(index + (event.key === 'ArrowDown' ? 1 : -1), 0), links.length - 1)]?.focus();
  };
  return <><button ref={trigger} type="button" className="workspace-search-trigger" disabled={disabled} onClick={() => setOpen(true)} aria-label={t('Search workspace', 'البحث في مساحة العمل')}><Search size={18} /><span>{t('Find a student or page…', 'دوّر على طالب أو صفحة…')}</span><kbd dir="ltr">Ctrl K</kbd></button>
    <Modal open={open} onClose={close} initialFocus={input} className="workspace-search-modal" closeLabel={t('Close search', 'إغلاق البحث')} title={t('Where do you want to go?', 'عايز توصل لإيه؟')} description={t('Search pages, student names or codes, and materials available to your role.', 'ابحث عن صفحة أو اسم طالب أو كوده أو مذكرة متاحة لصلاحيتك.')}>
      <SearchField label={t('Search workspace', 'البحث في مساحة العمل')} placeholder={t('Try a student code or “attendance”', 'جرّب كود طالب أو «الحضور»')} inputRef={input} value={query} onChange={setQuery} onKeyDown={move} />
      <p className="search-result-count" role="status">{items.length ? `${items.length} ${t('destinations', 'نتائج متاحة')}` : t('No matching results', 'مفيش نتائج مطابقة')}</p>
      <div className="workspace-search-results" ref={results}>{items.map(({ key, title, subtitle, href, Icon }, i) => <a key={key} href={href} onClick={close} onKeyDown={event => move(event, i)}><span className="search-result-icon"><Icon size={20} /></span><span><strong>{title}</strong><small dir="auto">{subtitle}</small></span><ArrowUpRight size={17} className="directional" /></a>)}{!items.length && <div className="search-no-results"><Search size={28} /><h3>{t('Try another name or code', 'جرّب اسم أو كود تاني')}</h3><p>{t('Clear your search to see the available pages.', 'امسح البحث لعرض الصفحات المتاحة.')}</p></div>}</div>
      <div className="search-keyboard-hint"><span>{t('↑ ↓ to move · Enter to open', '↑ ↓ للتنقّل · Enter للفتح')}</span><span>{t('Esc to close', 'Esc للإغلاق')}</span></div>
    </Modal></>;
}
