import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { createDemoService } from './service.js';
import { applyContent } from '../domain/content.js';
import { can } from '../domain/workspace.js';
import { translateError, formatDate, formatMoney, formatGrade, translatePaymentMethod, resolveEmployeeDisplay, isValidDateRange, dateRangeErrorText } from '../locales/i18n.js';

const Context = createContext(null);
export function WorkspaceProvider({ children }) {
  const [service] = useState(() => { let storage; try { storage = window.localStorage; } catch { storage = { getItem() { throw new Error('STORAGE'); }, setItem() { throw new Error('STORAGE'); } }; } return createDemoService({ storage, contentOperation: applyContent }); });
  const [role, setRoleState] = useState('admin');
  const [lang, setLanguage] = useState(() => { try { return localStorage.getItem('eduflow.language.v1')?.includes('ar') ? 'ar' : 'en'; } catch { return 'en'; } });
  const [response, setResponse] = useState(null), [error, setError] = useState(null), [loading, setLoading] = useState(true);
  const sequence = useRef(0), roleRef = useRef(role), abort = useRef(null);
  roleRef.current = role;
  const refresh = useCallback(async () => {
    if (roleRef.current !== role) return;
    const ticket = ++sequence.current; abort.current?.abort(); const controller = new AbortController(); abort.current = controller; setLoading(true); setError(null);
    try { const result = await service.read(role, { signal: controller.signal }); if (ticket === sequence.current) setResponse(result); }
    catch (e) { if (ticket === sequence.current) setError(e); }
    finally { if (ticket === sequence.current) setLoading(false); }
  }, [role, service]);
  useEffect(() => { refresh(); const update = () => refresh(); window.addEventListener('storage', update); return () => { sequence.current++; window.removeEventListener('storage', update); }; }, [refresh]);
  useEffect(() => { document.documentElement.lang = lang; document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'; }, [lang]);
  const setLang = value => { setLanguage(value); try { localStorage.setItem('eduflow.language.v1', JSON.stringify(value)); } catch { /* Persistence of language is optional. */ } };
  const setRole = value => { if (roleRef.current === value) return; sequence.current++; roleRef.current = value; abort.current?.abort(); setResponse(null); setLoading(true); setRoleState(value); };
  const execute = async (command, input, idempotencyKey) => {
    const result = await service.execute(command, input, { role, expectedRevision: response.data.revision, idempotencyKey });
    // A role change/navigation must not apply an older request's projection.
    if (roleRef.current === role) await refresh(); return result;
  };
  const value = { role, setRole, lang, setLang, t: (en, ar) => lang === 'ar' ? ar : en, pick: pair => pair?.[lang === 'ar' ? 1 : 0] ?? '',
    data: response?.data, notice: response?.notice, readOnly: response?.readOnly, loading, error, refresh, execute, service,
    can: permission => can(role, permission), errorText: e => translateError(e, lang), money: n => formatMoney(n, lang), date: (d, instant) => formatDate(d, lang, instant),
    grade: g => formatGrade(g, lang), paymentMethod: m => translatePaymentMethod(m, lang), employee: id => resolveEmployeeDisplay(id, response?.data?.users, lang),
    isValidDateRange, dateRangeError: (from, to) => !isValidDateRange(from, to) ? dateRangeErrorText(lang) : null,
  };
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export const useWorkspace = () => useContext(Context);
export function useAction() {
  const workspace = useWorkspace(); const [busy, setBusy] = useState(false), [error, setError] = useState(null), [success, setSuccess] = useState(false);
  const lock = useRef(false), retry = useRef(null), mounted = useRef(true);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);
  async function run(command, input, after) {
    if (lock.current) return; lock.current = true; setBusy(true); setError(null); setSuccess(false);
    const fingerprint = JSON.stringify({ command, input });
    if (retry.current?.fingerprint !== fingerprint) retry.current = { fingerprint, key: crypto.randomUUID() };
    try {
      const result = await workspace.execute(command, input, retry.current.key); retry.current = null;
      if (mounted.current) { setSuccess(true); after?.(result); } return result;
    } catch (e) { if (mounted.current) setError(e); }
    finally { lock.current = false; if (mounted.current) setBusy(false); }
  }
  return { run, busy, error, success, clear: () => { setError(null); setSuccess(false); } };
}
