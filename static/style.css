/* ============================================================
   دستیار SEO — Design tokens
   تم: پس‌زمینه‌ی کاملاً مشکی + پیغام‌های آبی نئونی
   ============================================================ */
:root {
  --bg-dark: #000000;       /* پس‌زمینه‌ی کلی صفحه — مشکی خالص */
  --bg-card: #0d0f14;       /* کارت‌ها/پنل‌ها — کمی روشن‌تر تا مرزها دیده شوند */
  --bg-sidebar: #0a0b10;
  --border-color: #20242f;

  --text-main: #f2f4f8;     /* روشن نگه داشته شد تا روی پس‌زمینه‌ی مشکی خوانا بماند */
  --text-muted: #9aa3b5;
  --text-dim: #626b7d;

  --accent: #3b6ef6;
  --accent-ink: #ffffff;

  /* پیغام‌ها (موفقیت/خطا) — هر دو یکدست آبی نئونی با کمی درخشش */
  --neon-blue: #22d3ee;
  --success-bg: rgba(34, 211, 238, 0.10);
  --success-text: #7fe3f7;
  --success-border: rgba(34, 211, 238, 0.45);

  --error-bg: rgba(34, 211, 238, 0.10);
  --error-text: #7fe3f7;
  --error-border: rgba(34, 211, 238, 0.45);

  --font-body: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;

  --radius: 12px;
  --radius-sm: 8px;
}

@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-dark);
  min-height: 100%;
}

html {
  height: 100%;
}

/* ============================================================
   اجبار فونت فارسی روی همه‌چیز — چون Bootstrap در base.html
   بعد از این فایل لود می‌شود و فونت پیش‌فرضش را جایگزین می‌کند،
   اینجا با !important قطعی می‌کنیم که همه‌جا Vazirmatn بماند
   ============================================================ */
html, body,
input, button, select, textarea, optgroup,
.btn, .form-control, .form-select,
h1, h2, h3, h4, h5, h6,
.modal, .modal-content, .dropdown-menu {
  font-family: var(--font-body) !important;
}

body {
  background-color: var(--bg-dark);
  color: var(--text-main);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

a {
  color: var(--accent);
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* ============================================================
   Status / flash messages — آبی نئونی با درخشش ملایم
   ============================================================ */
.status {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  margin-bottom: 16px;
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.15);
}

.status.success {
  background-color: var(--success-bg);
  color: var(--success-text);
  border: 1px solid var(--success-border);
}

.status.error {
  background-color: var(--error-bg);
  color: var(--error-text);
  border: 1px solid var(--error-border);
}

/* ============================================================
   صفحات ورود / ثبت‌نام (auth)
   ============================================================ */
.auth-body {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-dark);
  padding: 24px;
}

.auth-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 40px 36px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.auth-title {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 24px;
  text-align: center;
  color: var(--text-main);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.auth-form label {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 12px;
}

.auth-form input[type="text"],
.auth-form input[type="email"],
.auth-form input[type="password"] {
  background-color: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 0.95rem;
  width: 100%;
}

.auth-form input::placeholder {
  color: var(--text-dim);
}

.auth-form input:focus {
  outline: none;
  border-color: var(--accent);
}

.remember-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
}

.remember-row label {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.auth-btn {
  background-color: var(--accent);
  color: var(--accent-ink);
  border: none;
  border-radius: var(--radius-sm);
  padding: 12px 20px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 20px;
  transition: opacity 0.15s ease;
}

.auth-btn:hover {
  opacity: 0.9;
}

.auth-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.auth-switch a {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
}

.auth-switch a:hover {
  text-decoration: underline;
}

/* ============================================================
   Layout اصلی داشبورد
   ============================================================ */
.layout {
  min-height: 100vh;
}

.sidebar.dashboard-sidebar {
  width: 260px;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  background-color: var(--bg-sidebar);
  border-left: 1px solid var(--border-color);
  padding: 24px 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow-y: auto;
}

.sidebar.dashboard-sidebar h2 {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 24px;
  padding: 0 8px;
  color: var(--text-main);
}

.tab-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tab-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.tab-link:hover {
  background-color: var(--bg-card);
  color: var(--text-main);
}

.tab-link.active {
  background-color: var(--accent);
  color: var(--accent-ink);
  font-weight: 700;
}

.tab-icon {
  font-size: 1rem;
}

.sidebar-footer {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
  margin-top: 16px;
}

.user-email {
  font-size: 0.8rem;
  color: var(--text-dim);
  margin: 0 8px 8px;
  word-break: break-all;
}

.logout-link {
  display: block;
  padding: 8px;
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
}

.logout-link:hover {
  color: var(--neon-blue);
}

.main {
  margin-right: 260px;
  padding: 32px 40px;
  min-width: 0;
  min-height: 100vh;
  background-color: var(--bg-dark);
}

.main h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 24px;
  color: var(--text-main);
}

.models-section-title {
  font-weight: 700;
  letter-spacing: -0.01em;
}

.tab-placeholder {
  background-color: var(--bg-card);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius);
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

/* ============================================================
   عناصر عمومی فرم داخل تب‌ها (select / textarea / input / دکمه‌ها)
   این قوانین کلی‌اند تا هر تبی که از کلاس‌های خام Bootstrap استفاده
   کند (مثل تحلیل محتوا) هم بی‌استایل نماند
   ============================================================ */
.main .form-control,
.main .form-select,
.main textarea {
  background-color: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  font-size: 0.9rem;
}

.main .form-control::placeholder,
.main textarea::placeholder {
  color: var(--text-dim);
}

.main .form-control:focus,
.main .form-select:focus,
.main textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: none;
  background-color: var(--bg-sidebar);
  color: var(--text-main);
}

.main label {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.main .btn-primary {
  background-color: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
  font-weight: 700;
  border-radius: var(--radius-sm);
  padding: 10px 20px;
}

.main .btn-primary:hover {
  background-color: var(--accent);
  border-color: var(--accent);
  opacity: 0.9;
  color: var(--accent-ink);
}

.main .btn-outline-secondary,
.main .btn-secondary {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--text-muted);
  border-radius: var(--radius-sm);
  padding: 10px 20px;
}

.main .btn-outline-secondary:hover,
.main .btn-secondary:hover {
  background-color: var(--bg-sidebar);
  border-color: var(--text-muted);
  color: var(--text-main);
}

/* ============================================================
   جعبه‌ی جستجو (یوتیوب / گوگل / داک‌داک‌گو)
   ============================================================ */
.search-box-container {
  margin-bottom: 24px;
}

.search-form .input-group {
  display: flex;
  gap: 8px;
}

.search-form .form-control {
  flex: 1;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  font-size: 0.9rem;
}

.search-form .form-control::placeholder {
  color: var(--text-dim);
}

.search-form .form-control:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: none;
}

.search-form .btn-primary {
  background-color: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
  font-weight: 700;
  border-radius: var(--radius-sm);
  padding: 10px 18px;
}

.search-form .btn-primary:hover {
  background-color: var(--accent);
  opacity: 0.9;
  border-color: var(--accent);
}

.search-info-badge {
  margin-top: 10px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.search-info-badge span {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

.section-title h3 {
  font-size: 1.05rem;
  margin: 0 0 4px;
  color: var(--text-main);
}

.section-title p {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 20px;
}

/* ============================================================
   کارت‌های نتایج ویدیو (یوتیوب)
   ============================================================ */
.video-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.video-thumbnail {
  position: relative;
}

.video-thumbnail img {
  width: 100%;
  display: block;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background-color: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono) !important;
}

.video-info {
  padding: 14px 16px 4px;
  flex: 1;
}

.video-title {
  font-size: 0.95rem;
  color: var(--text-main);
  margin: 0 0 6px;
  line-height: 1.4;
}

.video-channel {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0 0 4px;
}

.video-views {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin: 0;
}

.video-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px 16px;
}

.video-actions .btn-outline-secondary {
  color: var(--text-muted);
  border-color: var(--border-color);
  background: transparent;
}

.video-actions .btn-outline-secondary:hover {
  color: var(--text-main);
  border-color: var(--text-muted);
  background-color: var(--bg-sidebar);
}

.video-actions .btn-primary,
.summarize-article-btn {
  background-color: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
  font-weight: 700;
}

.video-actions .btn-primary:hover,
.summarize-article-btn:hover {
  opacity: 0.9;
  background-color: var(--accent);
  border-color: var(--accent);
}

/* ============================================================
   مودال خلاصه‌سازی (Bootstrap modal overrides)
   ============================================================ */
.modal-content {
  color: var(--text-main);
}

.summary-result h1,
.summary-result h2,
.summary-result h3,
.summary-result h4,
.summary-result h5,
.summary-result h6 {
  color: var(--text-main);
}

.summary-result p {
  color: var(--text-muted);
  line-height: 1.8;
}

.loading-spinner {
  color: var(--text-muted);
}

/* ============================================================
   صفحه‌ی مدیریت API Key / مدل‌ها
   ============================================================ */
.models-section {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 28px;
}

.models-section-title {
  font-size: 1.1rem;
  margin: 0 0 20px;
  color: var(--text-main);
}

.provider-form .form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.provider-form .form-field {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.provider-form label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.provider-form input[type="text"],
.provider-form input[type="password"],
.provider-form select {
  background-color: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 0.9rem;
}

.provider-form input:focus,
.provider-form select:focus {
  outline: none;
  border-color: var(--accent);
}

.provider-hint {
  font-size: 0.8rem;
  color: var(--text-dim);
  margin: 4px 0 12px;
}

.provider-card input[type="text"] {
  font-family: var(--font-body) !important;
}

/* ============================================================
   Responsive
   ============================================================ */
@media (max-width: 900px) {
  .sidebar.dashboard-sidebar {
    width: 100%;
    height: 64px;
    bottom: auto;
    flex-direction: row;
    align-items: center;
    border-left: none;
    border-bottom: 1px solid var(--border-color);
    overflow-x: auto;
    overflow-y: hidden;
    padding: 10px 14px;
  }

  .sidebar.dashboard-sidebar h2,
  .sidebar-footer {
    display: none;
  }

  .tab-nav {
    flex-direction: row;
  }

  .tab-label {
    white-space: nowrap;
  }

  .main {
    margin-right: 0;
    margin-top: 64px;
    padding: 24px 20px;
  }
}

@media (max-width: 520px) {
  .auth-card {
    padding: 28px 22px;
  }

  .provider-form .form-row {
    flex-direction: column;
  }

  .search-form .input-group {
    flex-direction: column;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
  }
}

/* ============================================================
   صفحه اصلی (Landing Page)
   ============================================================ */

.landing-body {
  background: var(--bg-dark);
  min-height: 100vh;
}

/* --- هدر --- */
.site-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 6%;
  background: rgba(5, 6, 10, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-main);
  text-decoration: none;
  white-space: nowrap;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 28px;
}

.main-nav a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.main-nav a:hover {
  color: var(--text-main);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-panel {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--accent);
  color: var(--accent-ink);
  border: none;
  padding: 10px 22px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.92rem;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
}

.btn-panel:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 22px rgba(59, 110, 246, 0.35);
  color: var(--accent-ink);
  opacity: 0.95;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 8px 18px 8px 8px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: border-color 0.2s, background 0.2s;
}

.user-chip:hover {
  border-color: var(--accent);
  background: var(--bg-sidebar);
  color: var(--text-main);
}

.user-chip .avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--accent-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.logout-mini {
  color: var(--text-dim);
  text-decoration: none;
  font-size: 0.85rem;
  border: 1px solid var(--border-color);
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  transition: color 0.2s, border-color 0.2s;
}

.logout-mini:hover {
  color: var(--text-main);
  border-color: var(--accent);
}

.nav-toggle {
  display: none;
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  width: 42px;
  height: 38px;
  font-size: 1.1rem;
  cursor: pointer;
}

/* --- Hero --- */
.hero {
  position: relative;
  padding: 90px 6% 70px;
  text-align: center;
  overflow: hidden;
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 25% 20%, rgba(59, 110, 246, 0.18), transparent 45%),
    radial-gradient(circle at 75% 30%, rgba(34, 211, 238, 0.14), transparent 45%);
  pointer-events: none;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 7px 18px;
  border-radius: 999px;
  font-size: 0.85rem;
  margin-bottom: 26px;
  position: relative;
}

.hero h1 {
  position: relative;
  font-size: clamp(2rem, 4.5vw, 3.2rem);
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.4;
  margin-bottom: 22px;
}

.hero h1 span {
  color: var(--accent);
  background: linear-gradient(90deg, var(--accent), var(--neon-blue));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero p.lead {
  position: relative;
  max-width: 680px;
  margin: 0 auto 38px;
  color: var(--text-muted);
  font-size: 1.08rem;
  line-height: 2;
}

.hero-ctas {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--accent);
  color: var(--accent-ink);
  border: none;
  padding: 15px 34px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 1.02rem;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(59, 110, 246, 0.4);
  color: var(--accent-ink);
}

.btn-hero-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: var(--text-main);
  border: 1px solid var(--border-color);
  padding: 15px 30px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  transition: border-color 0.2s, background 0.2s;
}

.btn-hero-secondary:hover {
  border-color: var(--accent);
  background: var(--bg-card);
  color: var(--text-main);
}

.hero-stats {
  position: relative;
  display: flex;
  justify-content: center;
  gap: 50px;
  flex-wrap: wrap;
  margin-top: 60px;
}

.hero-stats .stat-num {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-main);
}

.hero-stats .stat-label {
  color: var(--text-dim);
  font-size: 0.85rem;
  margin-top: 4px;
}

/* --- بخش‌های عمومی --- */
.section {
  padding: 80px 6%;
  max-width: 1180px;
  margin: 0 auto;
}

.section-heading {
  text-align: center;
  max-width: 620px;
  margin: 0 auto 50px;
}

.section-heading .eyebrow {
  display: inline-block;
  color: var(--accent);
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.03em;
  margin-bottom: 10px;
}

.section-heading h2 {
  color: var(--text-main);
  font-weight: 800;
  font-size: clamp(1.5rem, 3vw, 2.1rem);
  margin-bottom: 14px;
}

.section-heading p {
  color: var(--text-muted);
  font-size: 1rem;
  line-height: 1.9;
}

/* --- ویژگی‌ها --- */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 30px 26px;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent);
  box-shadow: 0 14px 30px rgba(59, 110, 246, 0.15);
}

.feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(59, 110, 246, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 18px;
}

.feature-card h3 {
  color: var(--text-main);
  font-size: 1.08rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.feature-card p {
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.85;
  margin: 0;
}

/* --- درباره ما --- */
.about-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
}

.about-text h2 {
  color: var(--text-main);
  font-weight: 800;
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  margin-bottom: 18px;
}

.about-text .eyebrow {
  display: inline-block;
  color: var(--accent);
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 10px;
}

.about-text p {
  color: var(--text-muted);
  line-height: 2;
  margin-bottom: 16px;
  font-size: 0.98rem;
}

.about-points {
  list-style: none;
  padding: 0;
  margin: 26px 0 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.about-points li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  color: var(--text-main);
  font-size: 0.95rem;
}

.about-points li i {
  color: var(--neon-blue);
  margin-top: 3px;
}

.about-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 36px;
}

.about-card .about-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.about-card .about-stat {
  text-align: center;
  padding: 18px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--bg-sidebar);
}

.about-card .about-stat .num {
  color: var(--accent);
  font-size: 1.6rem;
  font-weight: 800;
}

.about-card .about-stat .label {
  color: var(--text-dim);
  font-size: 0.82rem;
  margin-top: 6px;
}

/* --- ارتباط با ما --- */
.contact-wrap {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 40px;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.contact-info-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
}

.contact-info-item .icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(34, 211, 238, 0.12);
  color: var(--neon-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  flex-shrink: 0;
}

.contact-info-item h4 {
  color: var(--text-main);
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.contact-info-item p, .contact-info-item a {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin: 0;
  text-decoration: none;
}

.contact-form-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 34px;
}

.contact-form .form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.contact-form label {
  display: block;
  color: var(--text-muted);
  font-size: 0.88rem;
  margin-bottom: 8px;
  margin-top: 16px;
}

.contact-form label:first-of-type {
  margin-top: 0;
}

.contact-form input,
.contact-form textarea {
  width: 100%;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-family: var(--font-body);
  font-size: 0.92rem;
  transition: border-color 0.2s;
}

.contact-form input:focus,
.contact-form textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.contact-form textarea {
  resize: vertical;
  min-height: 110px;
}

.contact-submit {
  margin-top: 22px;
  width: 100%;
  background: var(--accent);
  color: var(--accent-ink);
  border: none;
  padding: 14px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.98rem;
  cursor: pointer;
  transition: opacity 0.2s;
}

.contact-submit:hover {
  opacity: 0.9;
}

.contact-form-note {
  margin-top: 14px;
  font-size: 0.82rem;
  color: var(--text-dim);
  display: none;
}

.contact-form-note.visible {
  display: block;
  color: var(--success-text);
}

/* --- CTA پایانی --- */
.cta-banner {
  margin: 0 6% 90px;
  background: linear-gradient(120deg, rgba(59, 110, 246, 0.14), rgba(34, 211, 238, 0.1));
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 56px 40px;
  text-align: center;
}

.cta-banner h2 {
  color: var(--text-main);
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  font-weight: 800;
  margin-bottom: 14px;
}

.cta-banner p {
  color: var(--text-muted);
  margin-bottom: 28px;
}

/* --- فوتر --- */
.site-footer {
  border-top: 1px solid var(--border-color);
  padding: 40px 6% 26px;
}

.footer-top {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 26px;
}

.footer-brand p {
  color: var(--text-dim);
  font-size: 0.85rem;
  margin-top: 10px;
  max-width: 320px;
  line-height: 1.8;
}

.footer-links {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
}

.footer-col h5 {
  color: var(--text-main);
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 14px;
}

.footer-col a {
  display: block;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  margin-bottom: 10px;
  transition: color 0.2s;
}

.footer-col a:hover {
  color: var(--text-main);
}

.footer-bottom {
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.8rem;
}

/* --- ریسپانسیو --- */
@media (max-width: 900px) {
  .main-nav {
    position: fixed;
    top: 66px;
    inset-inline: 0;
    background: var(--bg-dark);
    border-bottom: 1px solid var(--border-color);
    flex-direction: column;
    align-items: flex-start;
    padding: 18px 6%;
    gap: 16px;
    transform: translateY(-140%);
    opacity: 0;
    transition: transform 0.25s, opacity 0.25s;
    z-index: 999;
  }

  .main-nav.open {
    transform: translateY(0);
    opacity: 1;
  }

  .nav-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .features-grid {
    grid-template-columns: 1fr 1fr;
  }

  .about-wrap,
  .contact-wrap {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .features-grid {
    grid-template-columns: 1fr;
  }

  .contact-form .form-row-2 {
    grid-template-columns: 1fr;
  }

  .hero {
    padding: 70px 6% 50px;
  }

  .header-actions .user-chip span.chip-label {
    display: none;
  }
}

/* --- خدمات طراحی سایت و سئو / پلن‌های قیمتی --- */
.services-hero {
  text-align: center;
  padding: 70px 6% 20px;
  max-width: 780px;
  margin: 0 auto;
}

.services-hero .hero-badge {
  display: inline-block;
  background: rgba(59, 110, 246, 0.12);
  color: var(--accent);
  border: 1px solid rgba(59, 110, 246, 0.3);
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.services-hero h1 {
  color: var(--text-main);
  font-weight: 800;
  font-size: clamp(1.6rem, 3.4vw, 2.3rem);
  line-height: 1.6;
  margin-bottom: 16px;
}

.services-hero p {
  color: var(--text-muted);
  font-size: 1.02rem;
  line-height: 2;
}

.services-hero .btn-call-hero {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-top: 28px;
  background: var(--accent);
  color: var(--accent-ink);
  border: none;
  padding: 15px 34px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 1.02rem;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
}

.services-hero .btn-call-hero:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(59, 110, 246, 0.4);
  color: var(--accent-ink);
}

/* شامل خدمات */
.included-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.included-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 18px 20px;
}

.included-item i {
  color: var(--accent);
  margin-top: 3px;
}

.included-item p {
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.9;
  margin: 0;
}

.included-item strong {
  display: block;
  color: var(--text-main);
  font-size: 0.98rem;
  margin-bottom: 4px;
}

/* پلن‌های قیمتی */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  align-items: stretch;
}

.pricing-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 34px 28px;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.pricing-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent);
  box-shadow: 0 14px 30px rgba(59, 110, 246, 0.15);
}

.pricing-card.featured {
  border-color: var(--accent);
  box-shadow: 0 14px 34px rgba(59, 110, 246, 0.2);
}

.pricing-badge {
  position: absolute;
  top: -14px;
  right: 50%;
  transform: translateX(50%);
  background: var(--accent);
  color: var(--accent-ink);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 5px 16px;
  border-radius: 999px;
  white-space: nowrap;
}

.pricing-card h3 {
  color: var(--text-main);
  font-size: 1.15rem;
  font-weight: 800;
  margin-bottom: 8px;
  text-align: center;
}

.pricing-card .plan-desc {
  color: var(--text-muted);
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 22px;
  line-height: 1.8;
}

.pricing-card .plan-price {
  text-align: center;
  color: var(--accent);
  font-weight: 800;
  font-size: 1.3rem;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
  flex-grow: 1;
}

.plan-features li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.9;
  padding: 8px 0;
}

.plan-features li i {
  color: var(--accent);
  margin-top: 4px;
}

.btn-plan-call {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: var(--accent);
  color: var(--accent-ink);
  border: none;
  padding: 14px 20px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.98rem;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
}

.btn-plan-call:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(59, 110, 246, 0.35);
  color: var(--accent-ink);
  opacity: 0.95;
}

.pricing-card:not(.featured) .btn-plan-call {
  background: transparent;
  color: var(--text-main);
  border: 1px solid var(--border-color);
}

.pricing-card:not(.featured) .btn-plan-call:hover {
  border-color: var(--accent);
  color: var(--accent);
  box-shadow: none;
}

.services-contact-banner {
  margin: 0 6% 90px;
  background: linear-gradient(120deg, rgba(59, 110, 246, 0.14), rgba(34, 211, 238, 0.1));
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 50px 40px;
  text-align: center;
}

.services-contact-banner h2 {
  color: var(--text-main);
  font-size: clamp(1.3rem, 3vw, 1.7rem);
  font-weight: 800;
  margin-bottom: 12px;
}

.services-contact-banner p {
  color: var(--text-muted);
  margin-bottom: 26px;
}

.services-contact-banner .phone-number {
  direction: ltr;
  display: inline-block;
  font-weight: 700;
  color: var(--text-main);
  margin-inline-start: 6px;
}

@media (max-width: 900px) {
  .pricing-grid {
    grid-template-columns: 1fr;
  }

  .included-grid {
    grid-template-columns: 1fr;
  }
}

/* --- کلیدهای دیفالت (دیپ‌سیک / kwfinder) --- */
.default-keys-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.default-key-card {
  background: var(--bg-dark);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 18px 20px;
}

.default-key-card.not-configured {
  opacity: 0.75;
}

.default-key-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.default-key-card-head strong {
  color: var(--text-main);
  font-size: 0.95rem;
}

.default-key-badge {
  font-size: 0.72rem;
  padding: 2px 10px;
  border-radius: 12px;
  white-space: nowrap;
}

.default-key-badge.active {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border: 1px solid #064e3b;
}

.default-key-badge.inactive {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  border: 1px solid #334155;
}

.default-key-card p {
  color: var(--text-muted);
  font-size: 0.82rem;
  line-height: 1.8;
  margin: 0 0 8px;
}

.default-key-value {
  display: inline-block;
  direction: ltr;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  padding: 4px 10px;
  border-radius: 6px;
  color: var(--accent);
  font-size: 0.82rem;
}

.default-key-hint {
  font-size: 0.78rem !important;
  color: var(--text-dim) !important;
  margin: 0 !important;
}

@media (max-width: 700px) {
  .default-keys-grid {
    grid-template-columns: 1fr;
  }
}

/* --- بنر خوش‌آمدگویی هفت‌روز رایگان (flash) --- */
.trial-welcome-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(90deg, rgba(59, 110, 246, 0.16), rgba(34, 211, 238, 0.12));
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin-bottom: 20px;
  color: var(--text-main);
  font-size: 0.95rem;
  box-shadow: 0 0 20px rgba(59, 110, 246, 0.15);
}

.trial-welcome-banner i {
  color: var(--accent);
  font-size: 1.3rem;
  flex-shrink: 0;
}

/* --- نشان روزهای باقی‌مانده در سایدبار --- */
.trial-sidebar-badge {
  margin: 6px 8px 14px;
  padding: 9px 10px;
  border-radius: var(--radius-sm);
  background: rgba(59, 110, 246, 0.12);
  border: 1px solid rgba(59, 110, 246, 0.3);
  color: var(--text-main);
  font-size: 0.78rem;
  text-align: center;
}

.trial-sidebar-badge.expired {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

/* --- قفل شدن ابزار پس از پایان دوره رایگان --- */
.trial-locked-content {
  filter: blur(6px);
  pointer-events: none;
  user-select: none;
}

.trial-lock-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 260px;
  bottom: 0;
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  padding: 20px;
}

.trial-lock-card {
  background: var(--bg-card);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  padding: 40px 36px;
  max-width: 420px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.trial-lock-icon {
  font-size: 2.2rem;
  color: var(--accent);
  margin-bottom: 16px;
}

.trial-lock-card h3 {
  color: var(--text-main);
  font-size: 1.12rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.trial-lock-card p {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.85;
  margin-bottom: 24px;
}

@media (max-width: 900px) {
  .trial-sidebar-badge {
    display: none;
  }

  .trial-lock-overlay {
    right: 0;
    top: 64px;
  }
}
