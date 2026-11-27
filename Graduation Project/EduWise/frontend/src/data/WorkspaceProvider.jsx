import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { createDemoService } from './service.js';
import { api } from './api.js';
import { applyContent } from '../domain/content.js';
import { can } from '../domain/workspace.js';
import { translateError, formatDate, formatMoney, formatGrade, translatePaymentMethod, resolveEmployeeDisplay, isValidDateRange, dateRangeErrorText } from '../locales/i18n.js';

const Context = createContext(null);
export function WorkspaceProvider({ children, isDemo }) {
  const [service] = useState(() => {
    if (!isDemo) return api;
    let storage;
    try { storage = window.localStorage; }
    catch { storage = { getItem() { throw new Error('STORAGE'); }, setItem() { throw new Error('STORAGE'); } }; }
    return createDemoService({ storage, contentOperation: applyContent });
  });
  const [previewRole, setRoleState] = useState('admin');
  const [account, setAccount] = useState(null);
  const [checkingSession, setCheckingSession] = useState(!isDemo);
  const [sessionError, setSessionError] = useState(null);
  const [authBusy, setAuthBusy] = useState(false);
  const [lang, setLanguage] = useState(() => { try { return localStorage.getItem('eduflow.language.v1')?.includes('ar') ? 'ar' : 'en'; } catch { return 'en'; } });
  const [response, setResponse] = useState(null), [error, setError] = useState(null), [loading, setLoading] = useState(true);
  const role = isDemo ? previewRole : account?.role;
  const actorId = account?.id;
  const identity = actorId ?? role;
  const sequence = useRef(0), identityRef = useRef(identity), abort = useRef(null), authLock = useRef(false);
  identityRef.current = identity;
  const clearWorkspace = useCallback(() => {
    sequence.current++;
    abort.current?.abort();
    setResponse(null);
    setError(null);
    setLoading(true);
  }, []);
  const expireSession = useCallback(() => {
    identityRef.current = undefined;
    clearWorkspace();
    setAccount(null);
  }, [clearWorkspace]);
  const restoreSession = useCallback(async signal => {
    setCheckingSession(true);
    setSessionError(null);
    try {
      const { user } = await api.session(signal);
      if (!signal?.aborted) setAccount(user);
    } catch (e) {
      if (!signal?.aborted && e.code !== 'AUTH_REQUIRED') setSessionError(e);
    } finally {
      if (!signal?.aborted) setCheckingSession(false);
    }
  }, []);
  useEffect(() => {
    if (isDemo) return;
    const controller = new AbortController();
    restoreSession(controller.signal);
    return () => controller.abort();
  }, [isDemo, restoreSession]);
  const refresh = useCallback(async () => {
    if (!role || identityRef.current !== identity) return;
    const ticket = ++sequence.current; abort.current?.abort(); const controller = new AbortController(); abort.current = controller; setLoading(true); setError(null);
    try { const result = await service.read(role, { signal: controller.signal, actorId }); if (ticket === sequence.current) setResponse(result); }
    catch (e) {
      if (ticket !== sequence.current) return;
      if (!isDemo && e.code === 'AUTH_REQUIRED') expireSession();
      else setError(e);
    }
    finally { if (ticket === sequence.current) setLoading(false); }
  }, [role, identity, actorId, service, isDemo, expireSession]);
  useEffect(() => {
    refresh();
    const event = isDemo ? 'storage' : 'focus';
    const update = () => refresh();
    window.addEventListener(event, update);
    return () => { sequence.current++; abort.current?.abort(); window.removeEventListener(event, update); };
  }, [refresh, isDemo]);
  useEffect(() => { document.documentElement.lang = lang; document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'; }, [lang]);
  const setLang = value => { setLanguage(value); try { localStorage.setItem('eduflow.language.v1', JSON.stringify(value)); } catch { /* Persistence of language is optional. */ } };
  const setRole = value => {
    if (!isDemo || identityRef.current === value) return;
    clearWorkspace();
    identityRef.current = value;
    setRoleState(value);
  };
  async function login(email, password) {
    if (authLock.current) return;
    authLock.current = true;
    setAuthBusy(true);
    setSessionError(null);
    try {
      const { user } = await api.login(email, password);
      clearWorkspace();
      setAccount(user);
    } catch (e) { setSessionError(e); }
    finally { authLock.current = false; setAuthBusy(false); }
  }
  async function logout() {
    if (authLock.current) return;
    authLock.current = true;
    setAuthBusy(true);
    setSessionError(null);
    try {
      await api.logout();
      expireSession();
    } catch (e) { setSessionError(e); }
    finally { authLock.current = false; setAuthBusy(false); }
  }
  const execute = async (command, input, idempotencyKey) => {
    try {
      const result = await service.execute(command, input, { role, actorId, expectedRevision: response.data.revision, idempotencyKey });
      if (identityRef.current === identity) await refresh();
      return result;
    } catch (e) {
      if (!isDemo && e.code === 'AUTH_REQUIRED' && identityRef.current === identity) expireSession();
      throw e;
    }
  };
  const value = { role, setRole, isDemo, account, checkingSession, sessionError, authBusy, restoreSession, login, logout,
    lang, setLang, t: (en, ar) => lang === 'ar' ? ar : en, pick: pair => pair?.[lang === 'ar' ? 1 : 0] ?? '',
    data: response?.data, notice: response?.notice, readOnly: response?.readOnly, questionBankCount: response?.questionBankCount ?? 0, loading, error, refresh, execute, service,
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
