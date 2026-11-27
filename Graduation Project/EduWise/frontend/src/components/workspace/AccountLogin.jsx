import { useEffect, useState } from 'react';
import { Globe2 } from 'lucide-react';
import { useWorkspace } from '../../data/WorkspaceProvider.jsx';
import { Button, Logo } from '../ui';
import { Field } from '../ui/FeatureUi.jsx';

export function AccountLogin() {
  const { t, lang, setLang, login, authBusy, checkingSession, sessionError, errorText, restoreSession } = useWorkspace();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  useEffect(() => {
    document.title = `${t('Sign in', 'تسجيل الدخول')} · EduFlow AI`;
  }, [lang]);
  return (
    <main className="account-page">
      <section className="panel account-panel">
        <div className="section-heading">
          <Logo />
          <Button variant="ghost" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}>
            <Globe2 size={17} /> {t('العربية', 'English')}
          </Button>
        </div>
        <h1>{t('Sign in to your workspace', 'سجّل الدخول لمساحة عملك')}</h1>
        {checkingSession ? (
          <p role="status">{t('Checking your session…', 'جارٍ التحقق من تسجيل الدخول…')}</p>
        ) : (
          <form className="feature-form" onSubmit={event => { event.preventDefault(); login(email, password); }}>
            <Field label={t('Email address', 'البريد الإلكتروني')}>
              <input type="email" dir="ltr" autoComplete="username" required maxLength={254} value={email} onChange={event => setEmail(event.target.value)} />
            </Field>
            <Field label={t('Password', 'كلمة المرور')}>
              <input type="password" dir="ltr" autoComplete="current-password" required maxLength={256} value={password} onChange={event => setPassword(event.target.value)} />
            </Field>
            {sessionError && <p className="form-error" role="alert">{errorText(sessionError)}</p>}
            <Button type="submit" disabled={authBusy}>{authBusy ? t('Signing in…', 'جارٍ تسجيل الدخول…') : t('Sign in', 'تسجيل الدخول')}</Button>
            {sessionError?.code === 'API_UNAVAILABLE' && (
              <Button variant="secondary" disabled={authBusy} onClick={() => restoreSession()}>
                {t('Retry connection', 'إعادة الاتصال')}
              </Button>
            )}
          </form>
        )}
        <a className="text-link" href="?mode=demo">{t('Open the sample workspace', 'افتح مساحة العمل التجريبية')}</a>
      </section>
    </main>
  );
}
