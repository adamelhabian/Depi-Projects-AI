import { useState, useMemo } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import {
  TrendingUp, TrendingDown, Users, CheckCircle2, AlertTriangle, AlertCircle,
  Sparkles, BookOpen, Wallet, ArrowUpRight, BarChart3, HelpCircle, Layers
} from 'lucide-react';
import { useWorkspace } from '../../data/WorkspaceProvider';
import { calendarDate, eligible, outstanding } from '../../domain/workspace';
import { weekStats, studentsSeed, materialsSeed, examBank } from '../../data/mockData';
import { AnimatedCounter, InteractiveItem } from '../ui/MotionUi';

/**
 * Interactive SVG Line & Area Chart for Attendance Trends
 * Supports animated stroke-drawing, smooth bezier curves, and interactive hover tooltips.
 */
export function AttendanceTrendChart({ period = 'week', customSessions = [] }) {
  const { t, lang } = useWorkspace();
  const shouldReduceMotion = useReducedMotion();
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const points = useMemo(() => {
    if (customSessions && customSessions.length >= 3) {
      return customSessions.map((s, idx) => ({
        label: s.date.slice(5),
        sub: s.title ? (Array.isArray(s.title) ? (lang === 'ar' ? s.title[1] : s.title[0]) : s.title) : `Session ${idx + 1}`,
        attendance: Math.min(100, Math.max(70, 85 + ((idx * 7) % 15) - 3)),
        score: Math.min(100, Math.max(65, 78 + ((idx * 5) % 18) - 4)),
      }));
    }
    return weekStats.map(w => ({
      label: lang === 'ar' ? w.ar : w.day,
      sub: lang === 'ar' ? `يوم ${w.ar}` : `${w.day} Session`,
      attendance: w.attendance,
      score: w.score,
    }));
  }, [customSessions, lang]);

  const width = 640;
  const height = 220;
  const pad = { top: 25, right: 30, bottom: 35, left: 45 };
  const graphWidth = width - pad.left - pad.right;
  const graphHeight = height - pad.top - pad.bottom;

  const minVal = 60;
  const maxVal = 100;

  const coords = useMemo(() => {
    return points.map((p, i) => {
      const x = pad.left + (i / Math.max(points.length - 1, 1)) * graphWidth;
      const yAtt = pad.top + graphHeight - ((p.attendance - minVal) / (maxVal - minVal)) * graphHeight;
      const yScore = pad.top + graphHeight - ((p.score - minVal) / (maxVal - minVal)) * graphHeight;
      return { ...p, x, yAtt, yScore };
    });
  }, [points, graphWidth, graphHeight]);

  // Construct smooth SVG path
  const pathD = useMemo(() => {
    if (!coords.length) return '';
    return coords.reduce((acc, pt, i, arr) => {
      if (i === 0) return `M ${pt.x} ${pt.yAtt}`;
      const prev = arr[i - 1];
      const cx = (prev.x + pt.x) / 2;
      return `${acc} C ${cx} ${prev.yAtt}, ${cx} ${pt.yAtt}, ${pt.x} ${pt.yAtt}`;
    }, '');
  }, [coords]);

  const areaD = useMemo(() => {
    if (!coords.length) return '';
    const lastX = coords[coords.length - 1].x;
    const firstX = coords[0].x;
    const bottomY = pad.top + graphHeight;
    return `${pathD} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`;
  }, [pathD, coords, graphHeight]);

  // Secondary score path
  const scorePathD = useMemo(() => {
    if (!coords.length) return '';
    return coords.reduce((acc, pt, i, arr) => {
      if (i === 0) return `M ${pt.x} ${pt.yScore}`;
      const prev = arr[i - 1];
      const cx = (prev.x + pt.x) / 2;
      return `${acc} C ${cx} ${prev.yScore}, ${cx} ${pt.yScore}, ${pt.x} ${pt.yScore}`;
    }, '');
  }, [coords]);

  return (
    <div className="chart-card attendance-chart-card">
      <div className="chart-header">
        <div>
          <h3>{t('Weekly Attendance & Quiz Mastery', 'منحنى الحضور والاستيعاب الأسبوعي')}</h3>
          <p>{t('Daily attendance percentage vs quiz average across sessions', 'نسبة الحضور اليومية مقارنة بمتوسط استيعاب الكويزات')}</p>
        </div>
        <div className="chart-legend">
          <span className="legend-item"><i className="legend-dot attendance-dot" />{t('Attendance', 'نسبة الحضور')}</span>
          <span className="legend-item"><i className="legend-dot score-dot" />{t('Quiz Score', 'مستوى الكويز')}</span>
        </div>
      </div>

      <div className="svg-chart-container" style={{ position: 'relative', width: '100%', overflow: 'hidden' }}>
        <svg dir="ltr" viewBox={`0 0 ${width} ${height}`} className="responsive-svg-chart" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="attGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#315DA8" stopOpacity="0.28" />
              <stop offset="100%" stopColor="#315DA8" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F2B880" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#F2B880" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[60, 70, 80, 90, 100].map(val => {
            const y = pad.top + graphHeight - ((val - minVal) / (maxVal - minVal)) * graphHeight;
            return (
              <g key={val} className="chart-grid-line">
                <line x1={pad.left} y1={y} x2={width - pad.right} y2={y} stroke="var(--md-sys-color-outline-variant)" strokeDasharray="3 3" strokeOpacity="0.5" />
                <text x={pad.left - 10} y={y + 4} textAnchor="end" fontSize="10" fill="var(--md-sys-color-on-surface-variant)">
                  {val}%
                </text>
              </g>
            );
          })}

          {/* Filled Area */}
          <path d={areaD} fill="url(#attGradient)" />

          {/* Score Path (dashed secondary) */}
          <motion.path
            d={scorePathD}
            fill="none"
            stroke="#D97A2E"
            strokeWidth="2"
            strokeDasharray="4 4"
            initial={shouldReduceMotion ? { pathLength: 1 } : { pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.1, ease: 'easeOut' }}
          />

          {/* Attendance Path (solid primary) */}
          <motion.path
            d={pathD}
            fill="none"
            stroke="#315DA8"
            strokeWidth="3.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={shouldReduceMotion ? { pathLength: 1 } : { pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1, ease: 'easeInOut' }}
          />

          {/* Data Points */}
          {coords.map((pt, i) => {
            const isHovered = hoveredPoint?.i === i;
            return (
              <g key={i} className="chart-point-group" onMouseEnter={() => setHoveredPoint({ ...pt, i })} onMouseLeave={() => setHoveredPoint(null)}>
                {/* Invisible hover target */}
                <rect x={pt.x - 20} y={pad.top} width={40} height={graphHeight} fill="transparent" style={{ cursor: 'pointer' }} />
                
                {/* Subtle vertical indicator line on hover */}
                {isHovered && (
                  <line x1={pt.x} y1={pad.top} x2={pt.x} y2={pad.top + graphHeight} stroke="#315DA8" strokeWidth="1" strokeDasharray="2 2" strokeOpacity="0.6" />
                )}

                {/* Score circle */}
                <circle cx={pt.x} cy={pt.yScore} r={isHovered ? 4.5 : 3} fill="#FFFFFF" stroke="#D97A2E" strokeWidth="2" />

                {/* Attendance circle */}
                <circle cx={pt.x} cy={pt.yAtt} r={isHovered ? 6 : 4} fill="#FFFFFF" stroke="#315DA8" strokeWidth="2.5" />

                {/* X-axis label */}
                <text x={pt.x} y={height - 12} textAnchor="middle" fontSize="11" fontWeight={isHovered ? '600' : '400'} fill={isHovered ? '#315DA8' : 'var(--md-sys-color-on-surface-variant)'}>
                  {pt.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Floating tooltip */}
        {hoveredPoint && (
          <div
            className="chart-tooltip"
            style={{
              position: 'absolute',
              top: `${Math.max(10, hoveredPoint.yAtt - 55)}px`,
              left: `${Math.min(width - 150, Math.max(10, hoveredPoint.x - 65))}px`,
              pointerEvents: 'none',
            }}
          >
            <strong>{hoveredPoint.sub}</strong>
            <div className="tooltip-row">
              <span className="tooltip-color attendance-bg" />
              <span>{t('Attendance:', 'الحضور:')} <strong>{hoveredPoint.attendance}%</strong></span>
            </div>
            <div className="tooltip-row">
              <span className="tooltip-color score-bg" />
              <span>{t('Quiz Avg:', 'متوسط الكويز:')} <strong>{hoveredPoint.score}%</strong></span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Group Comparison Bar Chart
 * Compares Group A, B, and C in attendance rate, quiz average, and active students.
 */
export function GroupComparisonBars() {
  const { data, t, pick } = useWorkspace();
  const shouldReduceMotion = useReducedMotion();

  const groupMetrics = useMemo(() => {
    return data.groups.map((g, idx) => {
      const enrollments = data.enrollments.filter(e => e.groupId === g.id && !e.endDate);
      const studentIds = new Set(enrollments.map(e => e.studentId));
      const groupStudents = studentsSeed.filter(s => {
        const numId = Number(s.id.replace('EF-', '')) - 1000;
        return studentIds.has(`student-${numId}`);
      });

      const avgAttendance = groupStudents.length
        ? Math.round(groupStudents.reduce((acc, s) => acc + s.attendance, 0) / groupStudents.length)
        : idx === 0 ? 94 : idx === 1 ? 89 : 86;

      const avgScore = groupStudents.length
        ? Math.round(groupStudents.reduce((acc, s) => acc + s.score, 0) / groupStudents.length)
        : idx === 0 ? 82 : idx === 1 ? 76 : 74;

      return {
        id: g.id,
        name: pick(g.name),
        studentsCount: enrollments.length || 8,
        attendance: avgAttendance,
        score: avgScore,
      };
    });
  }, [data, pick]);

  return (
    <div className="chart-card group-bars-card">
      <div className="chart-header">
        <div>
          <h3>{t('Group Performance Comparison', 'مقارنة أداء المجموعات')}</h3>
          <p>{t('Attendance consistency and quiz mastery per group', 'معدل الحضور والانضباط الأكاديمي لكل مجموعة')}</p>
        </div>
      </div>

      <div className="group-bars-list">
        {groupMetrics.map(g => (
          <div key={g.id} className="group-bar-item">
            <div className="group-bar-header">
              <div className="group-bar-title-wrap">
                <strong>{g.name}</strong>
                <span className="group-count-tag">{g.studentsCount} {t('students', 'طلاب')}</span>
              </div>
              <div className="group-bar-badges">
                <span className="bar-badge attendance-badge">
                  <span className="badge-legend-dot att-dot" />
                  {t('Att.', 'حضور')} <strong>{g.attendance}%</strong>
                </span>
                <span className="bar-badge score-badge">
                  <span className="badge-legend-dot sc-dot" />
                  {t('Quiz', 'كويز')} <strong>{g.score}%</strong>
                </span>
              </div>
            </div>

            {/* Attendance Track */}
            <div className="metric-bar-track">
              <motion.div
                className="metric-bar-fill attendance-fill"
                initial={shouldReduceMotion ? { width: `${g.attendance}%` } : { width: '0%' }}
                animate={{ width: `${g.attendance}%` }}
                transition={{ duration: 0.85, ease: 'easeOut' }}
              />
            </div>

            {/* Score Track */}
            <div className="metric-bar-track secondary-track">
              <motion.div
                className="metric-bar-fill score-fill"
                initial={shouldReduceMotion ? { width: `${g.score}%` } : { width: '0%' }}
                animate={{ width: `${g.score}%` }}
                transition={{ duration: 0.95, ease: 'easeOut', delay: 0.1 }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Student Risk & Academic Retention Health Ring
 * Visual breakdown of students into Safe, Under Watch, and Risk categories.
 */
export function StudentRetentionGauge() {
  const { t } = useWorkspace();
  const shouldReduceMotion = useReducedMotion();

  const counts = useMemo(() => {
    const total = studentsSeed.length;
    const safe = studentsSeed.filter(s => s.risk === 'safe').length;
    const watch = studentsSeed.filter(s => s.risk === 'watch').length;
    const risk = studentsSeed.filter(s => s.risk === 'risk').length;

    return {
      total,
      safe,
      watch,
      risk,
      safePct: Math.round((safe / total) * 100),
      watchPct: Math.round((watch / total) * 100),
      riskPct: Math.round((risk / total) * 100),
    };
  }, []);

  return (
    <div className="chart-card retention-card">
      <div className="chart-header">
        <div>
          <h3>{t('Student Academic Retention', 'صحة المتابعة والانضباط')}</h3>
          <p>{t('Early intervention status based on attendance & homework', 'حالة الطلاب ومؤشرات التدخل الأكاديمي المبكر')}</p>
        </div>
      </div>

      <div className="retention-content">
        {/* Visual Multi-Segment Bar */}
        <div className="segmented-health-bar">
          <motion.div
            className="health-segment segment-safe"
            style={{ width: `${counts.safePct}%` }}
            initial={shouldReduceMotion ? { scaleX: 1 } : { scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.65 }}
            title={`${counts.safe} ${t('Stable', 'مستقر')}`}
          />
          <motion.div
            className="health-segment segment-watch"
            style={{ width: `${counts.watchPct}%` }}
            initial={shouldReduceMotion ? { scaleX: 1 } : { scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.65, delay: 0.1 }}
            title={`${counts.watch} ${t('Under Watch', 'متابعة')}`}
          />
          <motion.div
            className="health-segment segment-risk"
            style={{ width: `${counts.riskPct}%` }}
            initial={shouldReduceMotion ? { scaleX: 1 } : { scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.65, delay: 0.2 }}
            title={`${counts.risk} ${t('Need Support', 'دعم مكثف')}`}
          />
        </div>

        {/* Legend / Metrics Grid */}
        <div className="retention-legend-grid">
          <InteractiveItem as="a" href="#students?status=active" className="retention-stat-box box-safe">
            <span className="retention-dot safe-dot" />
            <div>
              <strong><AnimatedCounter value={counts.safe} /> {t('Students', 'طالب')}</strong>
              <small>{t('Stable & excelling (67%)', 'أداء مستقر وممتاز (67%)')}</small>
            </div>
            <CheckCircle2 size={16} className="retention-icon safe-icon" />
          </InteractiveItem>

          <InteractiveItem as="a" href="#students?status=active" className="retention-stat-box box-watch">
            <span className="retention-dot watch-dot" />
            <div>
              <strong><AnimatedCounter value={counts.watch} /> {t('Students', 'طلاب')}</strong>
              <small>{t('Needs follow-up (21%)', 'يحتاج متابعة وتذكير (21%)')}</small>
            </div>
            <AlertTriangle size={16} className="retention-icon watch-icon" />
          </InteractiveItem>

          <InteractiveItem as="a" href="#students?status=active" className="retention-stat-box box-risk">
            <span className="retention-dot risk-dot" />
            <div>
              <strong><AnimatedCounter value={counts.risk} /> {t('Students', 'طلاب')}</strong>
              <small>{t('Requires intervention (12%)', 'يحتاج تدخلاً وتواصلاً (12%)')}</small>
            </div>
            <AlertCircle size={16} className="retention-icon risk-icon" />
          </InteractiveItem>
        </div>
      </div>
    </div>
  );
}

/**
 * Physics Syllabus & Materials Progress Cards
 * Displays the 3 Physics chapters with their artwork, page counts, questions, and mastery.
 */
export function SyllabusCoverageCards() {
  const { t, pick } = useWorkspace();

  const modules = [
    {
      id: 'm1',
      title: ['Motion & forces', 'الحركة والقوى'],
      grade: 'Grade 12 · Physics',
      gradeAr: 'الصف الثالث الثانوي · فيزياء',
      pages: 24,
      questions: 5,
      mastery: 89,
      image: '/images/material-motion.webp',
    },
    {
      id: 'm2',
      title: ['Electricity, made clear', 'الكهربية ببساطة'],
      grade: 'Grade 12 · Physics',
      gradeAr: 'الصف الثالث الثانوي · فيزياء',
      pages: 36,
      questions: 3,
      mastery: 93,
      image: '/images/material-electricity.webp',
    },
    {
      id: 'm3',
      title: ['Waves & sound', 'الموجات والصوت'],
      grade: 'Grade 11 · Physics',
      gradeAr: 'الصف الثاني الثانوي · فيزياء',
      pages: 18,
      questions: 1,
      mastery: 82,
      image: '/images/material-waves.webp',
    },
  ];

  return (
    <div className="chart-card syllabus-coverage-card">
      <div className="chart-header">
        <div>
          <h3>{t('Study Material & Curriculum Progress', 'تغطية المذكرات ومصادر المنهج')}</h3>
          <p>{t('Verified question bank coverage and chapter completion', 'مدى جاهزية بنك الأسئلة ومعدلات تغطية الفصول')}</p>
        </div>
        <a href="#materials" className="text-link">
          {t('Open Library', 'عرض كل المذكرات')} <ArrowUpRight size={14} className="directional" />
        </a>
      </div>

      <div className="syllabus-grid">
        {modules.map(mod => (
          <InteractiveItem as="article" key={mod.id} className="syllabus-module-card">
            <div className="module-thumb">
              <img src={mod.image} alt={pick(mod.title)} loading="lazy" />
              <span className="module-pages-badge">{mod.pages} {t('pages', 'صفحة')}</span>
            </div>
            <div className="module-info">
              <h4>{pick(mod.title)}</h4>
              <p>{pick([mod.grade, mod.gradeAr])}</p>
              
              <div className="module-stats-row">
                <span>{t('Bank:', 'بنك الأسئلة:')} <strong>{mod.questions} {t('questions', 'أسئلة')}</strong></span>
                <span>{t('Mastery:', 'الاستيعاب:')} <strong>{mod.mastery}%</strong></span>
              </div>

              <div className="metric-bar-track">
                <div className="metric-bar-fill attendance-fill" style={{ width: `${mod.mastery}%` }} />
              </div>

              <a href={`#studio?materialId=${mod.id}`} className="module-action-link">
                {t('Prepare Exam', 'تجهيز اختبار')} <ArrowUpRight size={14} className="directional" />
              </a>
            </div>
          </InteractiveItem>
        ))}
      </div>
    </div>
  );
}

/**
 * AI Smart Insights Panel
 * Actionable automated observations adhering to EduFlow design tokens.
 */
export function AiInsightsPanel() {
  const { t } = useWorkspace();

  const insights = [
    {
      type: 'success',
      badge: t('High Attendance', 'انضباط ممتاز'),
      text: t(
        'Group A achieved 94% average attendance this week, outperforming the center target by 6%.',
        'مجموعة أ سجلت أعلى نسبة التزام بالحضور بنسبة 94% هذا الأسبوع متفوقة على المستهدف بـ 6%.'
      ),
    },
    {
      type: 'warning',
      badge: t('Support Opportunity', 'فرصة دعم'),
      text: t(
        '3 students in Electricity & Circuits require additional reinforcement on Ohm’s Law series combinations.',
        '3 طلاب في فصل الكهربية يحتاجون ورقة تقوية إضافية على توصيل المقاومات وتطبيقات قانون أوم.'
      ),
    },
    {
      type: 'info',
      badge: t('Financial Recovery', 'متابعة التحصيل'),
      text: t(
        '75% of subscriptions for the current period are collected on time, leaving 6 pending records under follow-up.',
        'تم تحصيل 75% من اشتراكات الشهر بنجاح، وتوجد 6 اشتراكات متبقية للمتابعة في بداية الأسبوع.'
      ),
    },
  ];

  return (
    <section className="panel ai-insights-panel" aria-label={t('AI Smart Insights', 'توصيات الذكاء الاصطناعي')}>
      <div className="ai-insights-header">
        <div className="ai-badge-title">
          <span className="sparkle-circle"><Sparkles size={16} /></span>
          <div>
            <h3>{t('AI Operational Insights & Recommendations', 'تحليلات وتوصيات الذكاء الاصطناعي')}</h3>
            <p>{t('Automated observations from your center’s attendance, homework and fee logs', 'ملاحظات وتوصيات مبنية على بيانات الحضور والواجبات وسجلات التحصيل')}</p>
          </div>
        </div>
      </div>

      <div className="ai-insights-grid">
        {insights.map((item, i) => (
          <InteractiveItem key={i} className={`ai-insight-card insight-${item.type}`}>
            <div className="insight-top">
              <span className={`insight-pill pill-${item.type}`}>{item.badge}</span>
            </div>
            <p className="insight-text">{item.text}</p>
          </InteractiveItem>
        ))}
      </div>
    </section>
  );
}

/**
 * Mini Analytics Preview Widget for the Overview Homepage
 */
export function OverviewAnalyticsWidget() {
  const { t } = useWorkspace();

  return (
    <section className="panel overview-analytics-widget" aria-label={t('Weekly Analytics Summary', 'ملخص التحليلات الأسبوعي')}>
      <div className="overview-widget-header">
        <div>
          <span className="widget-eyebrow">{t('WEEKLY PULSE', 'نبض الأسبوع الأكاديمي')}</span>
          <h2>{t('Attendance & Academic Trends', 'مؤشرات الحضور والأداء الأكاديمي')}</h2>
        </div>
        <a href="#analytics" className="btn btn-secondary">
          <BarChart3 size={16} />
          {t('Open Full Analytics Dashboard', 'فتح لوحة التحليلات الكاملة')}
          <ArrowUpRight size={15} className="directional" />
        </a>
      </div>

      <div className="overview-widget-content">
        <AttendanceTrendChart period="week" />
      </div>
    </section>
  );
}
