const feedback = document.querySelector('#brand-feedback');
let feedbackTimer;
function announce(message) {
  clearTimeout(feedbackTimer);
  feedback.textContent = message;
  feedback.dataset.visible = 'true';
  feedbackTimer = setTimeout(() => { feedback.dataset.visible = 'false'; }, 4000);
}
for (const button of document.querySelectorAll('[data-copy-color]')) {
  button.addEventListener('click', async () => {
    const value = button.dataset.copyColor;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(value);
      announce('تم نسخ كود اللون.');
    } catch {
      const code = button.closest('.color-card')?.querySelector('code');
      if (code) { const range = document.createRange(); range.selectNodeContents(code); const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range); }
      announce('حدّدنا الكود. اضغط Ctrl+C لنسخه، أو انسخه من قائمة التحديد.');
    }
  });
}
const slider = document.querySelector('#type-size');
slider?.addEventListener('input', () => {
  document.querySelector('.type-grid').style.setProperty('--specimen-size', `${slider.value}px`);
  document.querySelector('#type-size-value').value = `${slider.value}px`;
});
for (const button of document.querySelectorAll('[data-logo-tone]')) {
  button.addEventListener('click', () => {
    for (const sibling of document.querySelectorAll('[data-logo-tone]')) sibling.setAttribute('aria-pressed', String(sibling === button));
    const tone = button.dataset.logoTone;
    const card = document.querySelector('.logo-card.light');
    card.dataset.tone = tone;
    const wordmark = card.querySelector('.wordmark');
    wordmark.classList.toggle('inverse', tone === 'dark');
    wordmark.querySelector('img').src = tone === 'dark' ? './mark-reversed.svg' : './mark.svg';
    document.querySelector('#logo-preview-status').textContent = `الخلفية المختارة: ${button.textContent.trim()}.`;
  });
}
for (const button of document.querySelectorAll('[data-product-view]')) {
  button.addEventListener('click', () => {
    for (const sibling of document.querySelectorAll('[data-product-view]')) sibling.setAttribute('aria-pressed', String(sibling === button));
    const view = button.dataset.productView;
    const image = document.querySelector('#product-preview-image');
    image.src = `./preview-${view}.png`;
    image.alt = view === 'overview' ? 'لقطة من لوحة اليوم في الديمو العربي' : 'لقطة من مكتبة المصادر في الديمو العربي';
    document.querySelector('#product-preview-link').href = view === 'overview' ? '/#overview' : '/#materials';
    document.querySelector('#product-preview-status').textContent = view === 'overview' ? 'معاينة لوحة اليوم.' : 'معاينة مكتبة المصادر.';
  });
}
const links = [...document.querySelectorAll('.site-header nav a')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    const entry = entries.filter(x => x.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!entry) return;
    for (const link of links) {
      if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }, { rootMargin: '-15% 0px -55% 0px', threshold: 0 });
  for (const section of document.querySelectorAll('section[id]')) observer.observe(section);
}
const topLink = document.querySelector('.back-to-top');
const onScroll = () => { topLink.hidden = scrollY < 700; };
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();
