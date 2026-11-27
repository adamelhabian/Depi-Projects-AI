import { Children, cloneElement, isValidElement, useEffect, useId, useRef, useState } from 'react';
import { useWorkspace } from '../../data/WorkspaceProvider';
import { statusLabels } from '../../locales/i18n';
import { Button, EmptyState } from './Base';
import { Inbox, Search, X, LoaderCircle } from 'lucide-react';

export function Heading({ title, description, children }) { return <div className="page-heading"><div><h1>{title}</h1><p className="page-description">{description}</p></div><div className="page-heading-actions">{children}</div></div>; }
export function Field({ label, children, hint }) { const id = useId(); return <div className="field"><label htmlFor={id}>{label}</label>{cloneElement(children, { id })}{hint && <small>{hint}</small>}</div>; }
export function Feedback({ action }) {
  const { t, isDemo, errorText, refresh } = useWorkspace();
  return <div aria-live="polite">{action.error && <div role="alert" className="form-error">{errorText(action.error)}{action.error.code === 'CONFLICT' && <Button variant="secondary" onClick={refresh}>{t('Refresh data', 'تحديث البيانات')}</Button>}</div>}{action.success && <p className="success-text feedback">{isDemo ? t('Saved locally in this demo.', 'تم الحفظ محلياً في الديمو.') : t('Saved to the workspace.', 'تم الحفظ في مساحة العمل.')}</p>}</div>;
}
export function Submit({ action, children }) { const { t, readOnly } = useWorkspace(); return <Button type="submit" className="submit-control" aria-busy={action.busy} disabled={action.busy || readOnly}><span className={action.busy ? 'submit-copy is-pending' : 'submit-copy'}>{children || t('Save', 'حفظ')}</span>{action.busy && <span className="submit-pending"><LoaderCircle size={17} className="ux-spinner" />{t('Saving…', 'جارٍ الحفظ…')}</span>}</Button>; }
export function SearchField({ label, value, onChange, placeholder, inputRef, ...props }) {
  const { t } = useWorkspace(), id = useId(), ownRef = useRef(null), ref = inputRef || ownRef;
  return <div className="field search-field"><label htmlFor={id}>{label}</label><div className="search-input-wrap"><Search size={18} aria-hidden="true" /><input {...props} id={id} ref={ref} type="search" autoComplete="off" value={value} placeholder={placeholder} onChange={e => onChange(e.target.value)} />{value && <button type="button" className="icon-button search-clear" aria-label={t('Clear search', 'مسح البحث')} onClick={() => { onChange(''); ref.current?.focus(); }}><X size={17} /></button>}</div></div>;
}
export function Status({ value }) { const { pick } = useWorkspace(); return <span className="record-status" data-status={value}>{pick(statusLabels[value] || [value, value])}</span>; }
export function NoRecords({ action, onAction, filtered = false }) { const { t } = useWorkspace(); return <EmptyState icon={Inbox} title={filtered ? t('No matching results', 'مفيش نتائج مطابقة') : t('Nothing here yet', 'مفيش سجلات لسه')} text={filtered ? t('Change or clear the filters to see more records.', 'غيّر أو امسح الفلاتر لعرض السجلات.') : t('Add the first record to get started.', 'أضف أول سجل عشان تبدأ.')} action={action || t('Clear filters', 'مسح الفلاتر')} onAction={onAction || (() => { location.hash = 'overview'; })} />; }
function cellText(node) { return Children.toArray(node).map(x => isValidElement(x) ? cellText(x.props.children) : String(x ?? '')).join(' '); }
function isColumnSortable(header) {
  if (!header) return false;
  if (typeof header === 'object' && header.sortable !== undefined) return Boolean(header.sortable);
  const text = typeof header === 'object' ? String(header.label || '') : String(header);
  const norm = text.trim().toLowerCase();
  if (['actions', 'action', 'إجراءات', 'إجراء', 'record / correct', 'تسجيل / تصحيح'].some(w => norm.includes(w))) return false;
  return true;
}
function getCellSortValue(cell) {
  if (!cell) return '';
  if (isValidElement(cell) && cell.props?.['data-sort-value'] !== undefined) {
    return cell.props['data-sort-value'];
  }
  const text = cellText(cell).trim();
  const stripped = text.replace(/[\s,EGPج\.م%]/gi, '');
  if (stripped !== '' && !Number.isNaN(Number(stripped)) && /^-?\d+(\.\d+)?$/.test(stripped)) {
    return Number(stripped);
  }
  return text;
}
export function Table({ headers, children, caption }) {
  const { t, lang } = useWorkspace();
  const [page, setPage] = useState(0), [size, setSize] = useState(10), [sort, setSort] = useState(null);
  const rows = Children.toArray(children).filter(isValidElement);
  const datasetKey = rows.map(row => row.key).join('|');
  useEffect(() => { setPage(0); }, [datasetKey]);
  const sorted = sort ? [...rows].sort((a, b) => {
    const cellA = Children.toArray(a.props.children)[sort.index];
    const cellB = Children.toArray(b.props.children)[sort.index];
    const valA = getCellSortValue(cellA);
    const valB = getCellSortValue(cellB);
    if (typeof valA === 'number' && typeof valB === 'number') {
      return (valA - valB) * sort.direction;
    }
    return String(valA).localeCompare(String(valB), lang, { numeric: true, sensitivity: 'base' }) * sort.direction;
  }) : rows;
  const last = Math.max(0, Math.ceil(rows.length / size) - 1), current = Math.min(page, last);
  return <><div className="table-scroll" tabIndex={0} role="region" aria-label={caption}><table className="data-table"><caption className="sr-only">{caption}</caption><thead><tr>{headers.map((h, i) => {
    const sortable = isColumnSortable(h);
    const label = typeof h === 'object' && h !== null && 'label' in h ? h.label : h;
    if (!sortable) {
      return <th scope="col" key={i} className="table-th-static">{label}</th>;
    }
    const isSorted = sort?.index === i;
    return <th scope="col" key={i} aria-sort={isSorted ? (sort.direction === 1 ? 'ascending' : 'descending') : 'none'}>
      <button type="button" className="table-sort" onClick={() => { setPage(0); setSort({ index: i, direction: isSorted ? -sort.direction : 1 }); }}>
        <span>{label}</span><span className="table-sort-arrow" aria-hidden="true">{isSorted ? (sort.direction === 1 ? ' ↑' : ' ↓') : ' ↕'}</span>
      </button>
    </th>;
  })}</tr></thead><tbody>{sorted.slice(current * size, (current + 1) * size)}</tbody></table></div><div className="table-pagination"><span role="status">{rows.length ? current * size + 1 : 0}–{Math.min((current + 1) * size, rows.length)} / {rows.length}</span><label>{t('Rows', 'صفوف')} <select aria-label={t('Rows per page', 'صفوف في الصفحة')} value={size} onChange={e => { setSize(Number(e.target.value)); setPage(0); }}>{[10, 25, 50].map(n => <option key={n}>{n}</option>)}</select></label><Button variant="ghost" disabled={!current} onClick={() => setPage(current - 1)}>{t('Previous', 'السابق')}</Button><Button variant="ghost" disabled={current >= last} onClick={() => setPage(current + 1)}>{t('Next', 'التالي')}</Button></div></>;
}
