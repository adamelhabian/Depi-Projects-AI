import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Dialog } from '@base-ui/react/dialog';
import { ArrowUpRight, X } from 'lucide-react';

export const cn = (...inputs) => twMerge(clsx(inputs));

export function Logo({ small = false }) {
  return <span className={cn('brand', small && 'brand-small')} dir="ltr"><img src="/brand/mark.svg?v=forward-pages" alt="" width="38" height="36" decoding="async" /><span>Edu<span className="brand-ai">Flow</span></span><sup>AI</sup></span>;
}

export function Button({ children, className, variant = 'primary', type = 'button', onClick, ...props }) {
  return <button type={type} onClick={onClick} className={cn('btn', `btn-${variant}`, className)} {...props}>{children}</button>;
}

export function SectionTitle({ title, subtitle, action, onAction }) {
  return <div className="section-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action && <button className="text-link" onClick={onAction}>{action}<ArrowUpRight size={16} className="directional" /></button>}</div>;
}

export function Modal({ open, onClose, title, description, children, wide = false, className, initialFocus, closeLabel = 'Close / إغلاق' }) {
  return <Dialog.Root open={open} onOpenChange={value => { if (!value) onClose(); }}><Dialog.Portal><Dialog.Backdrop className="modal-backdrop" /><Dialog.Popup initialFocus={initialFocus} className={cn('modal-panel', wide && 'modal-wide', className)}><div className="modal-heading"><div><Dialog.Title className="modal-title">{title}</Dialog.Title><Dialog.Description className="muted mt-2">{description}</Dialog.Description></div><Dialog.Close className="icon-button" aria-label={closeLabel}><X size={20} /></Dialog.Close></div>{children}</Dialog.Popup></Dialog.Portal></Dialog.Root>;
}

export function Progress({ value, label }) {
  return <div role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100} aria-label={label} className="progress-track"><div style={{ width: `${value}%` }} /></div>;
}

export function EmptyState({ icon: Icon, title, text, action, onAction }) {
  return <div className="empty-state"><span className="empty-icon"><Icon size={28} /></span><h3>{title}</h3><p>{text}</p>{action && <Button onClick={onAction}>{action}</Button>}</div>;
}
