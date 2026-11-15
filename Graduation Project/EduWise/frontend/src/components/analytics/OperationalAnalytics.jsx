import { useState } from 'react';
import { useWorkspace } from '../../data/WorkspaceProvider';
import { calendarDate } from '../../domain/workspace';
import { attendanceSummary, operationalReport } from '../../domain/reports';
import { Field, Heading, Table, NoRecords } from '../ui/FeatureUi';
import { AnimatedCounter, InteractiveItem, AnimatedSegmented } from '../ui/MotionUi';
import {
  AttendanceTrendChart, GroupComparisonBars, StudentRetentionGauge,
  SyllabusCoverageCards, AiInsightsPanel
} from './AnalyticsCharts';
import {
  TrendingUp, UsersRound, Wallet, BookOpen, BarChart3, ArrowUpRight
} from 'lucide-react';
import { examBank } from '../../data/mockData';

export function OverviewEvidence() {
  const { data, t } = useWorkspace();
  const report = operationalReport(data, { from: calendarDate(), to: calendarDate() });
  return (
    <section className="panel feature-card">
      <h2>{t('Today’s register coverage', 'اكتمال كشف اليوم')}</h2>
      <p>{report.recorded} / {report.expected} {t('attendance records', 'سجل حضور')} · {report.missing} {t('not recorded', 'غير مسجل')}</p>
      <a className="text-link" href="#analytics">{t('Open evidence report', 'فتح تقرير السجلات')} <ArrowUpRight size={14} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} /></a>
    </section>
  );
}

export default function OperationalAnalytics() {
  const { data, t, pick, date, money, can, dateRangeError } = useWorkspace();
  const today = calendarDate();
  const [periodPreset, setPeriodPreset] = useState('month');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [from, setFrom] = useState(`${today.slice(0, 7)}-01`);
  const [to, setTo] = useState(today);

  // Quick period presets
  const handlePeriodChange = (preset) => {
    setPeriodPreset(preset);
    const now = new Date();
    if (preset === 'week') {
      const past = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      setFrom(calendarDate(past));
      setTo(today);
    } else if (preset === 'month') {
      setFrom(`${today.slice(0, 7)}-01`);
      setTo(today);
    } else if (preset === 'term') {
      setFrom('2026-09-01');
      setTo(today);
    }
  };

  const handleFromChange = (val) => {
    setFrom(val);
    setPeriodPreset('custom');
  };

  const handleToChange = (val) => {
    setTo(val);
    setPeriodPreset('custom');
  };

  const dateError = dateRangeError(from, to);
  const isValid = !dateError;
  const report = isValid ? operationalReport(data, { from, to, groupId: selectedGroup }) : null;
  const link = student => `#students?studentId=${encodeURIComponent(student.id)}&status=all`;
  const absences = report ? report.students.map(student => ({ student, ...attendanceSummary(report.records.filter(r => r.studentId === student.id)) })).filter(s => s.absent > 0) : [];
  const totalStudentsCount = data.students.filter(s => s.status === 'active').length;

  return (
    <>
      <Heading
        title={t('Insights & Executive Analytics', 'التحليلات والتقارير')}
        description={t(
          'Calculated from saved registers and receipts in the selected period.',
          'محسوبة من كشوف الحضور والإيصالات المحفوظة خلال الفترة المحددة.'
        )}
      />

      {/* Control bar: Preset pills & Group filter */}
      <div className="analytics-toolbar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap', marginBottom: '16px' }}>
        <AnimatedSegmented
          layoutId="analytics-period-pill"
          ariaLabel={t('Select time period', 'اختر الفترة الزمنية')}
          selected={periodPreset}
          onChange={handlePeriodChange}
          items={[
            ['week', t('This week', 'هذا الأسبوع')],
            ['month', t('This month', 'هذا الشهر')],
            ['term', t('Full term', 'الفصل الدراسي')],
            ['custom', t('Custom range', 'تاريخ مخصص')],
          ]}
        />

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <Field label={t('Group', 'المجموعة')}>
            <select value={selectedGroup} onChange={e => setSelectedGroup(e.target.value)} style={{ minWidth: '150px' }}>
              <option value="">{t('All groups', 'كل المجموعات')}</option>
              {data.groups.map(g => (
                <option key={g.id} value={g.id}>{pick(g.name)}</option>
              ))}
            </select>
          </Field>
        </div>
      </div>

      {/* Filter panel with date inputs */}
      <section className="panel" style={{ marginBottom: '20px' }}>
        <div className="filter-bar">
          <Field label={t('From · Cairo date', 'من · تاريخ القاهرة')}>
            <input type="date" value={from} onChange={e => handleFromChange(e.target.value)} />
          </Field>
          <Field label={t('To · Cairo date', 'إلى · تاريخ القاهرة')}>
            <input type="date" value={to} onChange={e => handleToChange(e.target.value)} />
          </Field>
        </div>
        {dateError ? (
          <p role="alert" className="form-error" style={{ margin: '14px 0 4px', fontWeight: 500 }}>
            {dateError}
          </p>
        ) : (
          <p className="info-note">
            {from && to ? `${date(from)} — ${date(to)}` : ''} · {t('Attendance = present + late ÷ recorded excluding excused. Missing records are never absence.', 'نسبة الحضور = حاضر + متأخر ÷ المسجل باستثناء بعذر. غير المسجل ليس غيابًا.')}
          </p>
        )}
      </section>

      {dateError ? (
        <section className="panel feature-card" role="region" aria-label={t('Date range validation', 'التحقق من الفترة')}>
          <p className="form-error" role="alert" style={{ fontSize: '15px', fontWeight: 600 }}>{dateError}</p>
          <p className="info-note">{t('Choose a valid date range to view operational insights and session records.', 'اختر فترة تاريخ صحيحة لعرض التحليلات وسجلات الحصص.')}</p>
        </section>
      ) : (
        <>
          {/* Top Executive KPI Cards with Animated Counters & Badges */}
          <div className="stats-grid report-stats analytics-kpi-grid">
            <InteractiveItem className="stat-card analytics-kpi-card">
              <div className="kpi-top">
                <span className="kpi-label">{t('Recorded attendance rate', 'نسبة الحضور المسجّل')}</span>
                <span className="kpi-icon-wrap"><TrendingUp size={18} /></span>
              </div>
              <div className="kpi-value-row">
                <strong className="stat-value kpi-value">
                  {report.rate === null ? '—' : <AnimatedCounter value={report.rate} suffix="%" />}
                </strong>
                <span className="kpi-badge positive">{report.present} / {report.denominator}</span>
              </div>
              <div className="kpi-progress-bar">
                <div className="kpi-progress-fill success-fill" style={{ width: `${report.rate ?? 0}%` }} />
              </div>
              <span className="kpi-subtext">
                {report.denominator ? `${report.present} ${t('present out of', 'حاضر من')} ${report.denominator}` : t('No sessions recorded', 'لا توجد حصص مسجلة')}
              </span>
            </InteractiveItem>

            <InteractiveItem className="stat-card analytics-kpi-card">
              <div className="kpi-top">
                <span className="kpi-label">{t('Active students', 'الطلاب النشطون')}</span>
                <span className="kpi-icon-wrap"><UsersRound size={18} /></span>
              </div>
              <div className="kpi-value-row">
                <strong className="stat-value kpi-value"><AnimatedCounter value={totalStudentsCount} /></strong>
                <span className="kpi-badge positive">100% {t('active', 'نشط')}</span>
              </div>
              <div className="kpi-progress-bar">
                <div className="kpi-progress-fill" style={{ width: '100%' }} />
              </div>
              <span className="kpi-subtext">
                {t(`Distributed across ${data.groups.length} academic groups`, `موزعون على ${data.groups.length} مجموعات تعليمية`)}
              </span>
            </InteractiveItem>

            {can('payments') ? (
              <InteractiveItem className="stat-card analytics-kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">{t('Net collections', 'صافي التحصيلات')}</span>
                  <span className="kpi-icon-wrap"><Wallet size={18} /></span>
                </div>
                <div className="kpi-value-row">
                  <strong className="stat-value kpi-value">{money(report.netMinor)}</strong>
                  <span className="kpi-badge positive">{report.receipts.length} {t('receipts', 'إيصالات')}</span>
                </div>
                <div className="kpi-progress-bar">
                  <div className="kpi-progress-fill" style={{ width: '75%' }} />
                </div>
                <span className="kpi-subtext">
                  {t('Receipts minus adjustments in period', 'إيصالات الفترة ناقص تعديلات الفترة')}
                </span>
              </InteractiveItem>
            ) : (
              <InteractiveItem className="stat-card analytics-kpi-card">
                <div className="kpi-top">
                  <span className="kpi-label">{t('Exam Question Bank', 'بنك أسئلة الاختبارات')}</span>
                  <span className="kpi-icon-wrap"><BookOpen size={18} /></span>
                </div>
                <div className="kpi-value-row">
                  <strong className="stat-value kpi-value"><AnimatedCounter value={examBank.length} /></strong>
                  <span className="kpi-badge positive">{t('Ready', 'جاهزة')}</span>
                </div>
                <div className="kpi-progress-bar">
                  <div className="kpi-progress-fill" style={{ width: '100%' }} />
                </div>
                <span className="kpi-subtext">{t('Verified across 3 physics modules', 'موثقة عبر 3 فصول فيزيائية')}</span>
              </InteractiveItem>
            )}

            <InteractiveItem className="stat-card analytics-kpi-card">
              <div className="kpi-top">
                <span className="kpi-label">{t('Sessions in period', 'الحصص خلال الفترة')}</span>
                <span className="kpi-icon-wrap"><BarChart3 size={18} /></span>
              </div>
              <div className="kpi-value-row">
                <strong className="stat-value kpi-value"><AnimatedCounter value={report.sessions.length} /></strong>
                <span className="kpi-badge neutral">{report.missing} {t('missing', 'غير مسجل')}</span>
              </div>
              <div className="kpi-progress-bar">
                <div className="kpi-progress-fill" style={{ width: report.expected ? `${Math.round((report.recorded / report.expected) * 100)}%` : '0%' }} />
              </div>
              <span className="kpi-subtext">
                {report.recorded} / {report.expected} {t('attendance records', 'سجل حضور')}
              </span>
            </InteractiveItem>
          </div>

          {/* Visual SVG Charts Grid */}
          <div className="analytics-charts-grid">
            <AttendanceTrendChart period={periodPreset} customSessions={report.sessions} />
            <GroupComparisonBars />
          </div>

          {/* Student Retention Gauge & Syllabus Coverage */}
          <div className="analytics-charts-grid">
            <StudentRetentionGauge />
            <SyllabusCoverageCards />
          </div>

          {/* AI Operational Insights & Recommendations */}
          <AiInsightsPanel />

          {/* Session Evidence Table */}
          <section className="panel ledger-panel">
            <h2>{t('Session evidence', 'سجلات الحصص')}</h2>
            {report.sessions.length ? (
              <Table
                caption={t('Session evidence', 'بيانات الحصص')}
                headers={[
                  t('Session', 'الحصة'),
                  t('Recorded', 'المسجل'),
                  t('Present / late', 'حاضر / متأخر'),
                  t('Absent', 'غائب'),
                  t('Excused', 'بعذر'),
                  t('Attendance', 'الحضور'),
                ]}
              >
                {report.sessions.map(s => {
                  const counts = attendanceSummary(report.records.filter(r => r.sessionId === s.id));
                  return (
                    <tr key={s.id}>
                      <td>
                        <a className="text-link" href={`#attendance?sessionId=${s.id}`}>
                          {pick(data.groups.find(g => g.id === s.groupId)?.name)}
                          <small className="cell-detail">{date(s.date)} · {s.startTime}</small>
                        </a>
                      </td>
                      <td data-sort-value={counts.recorded}>{counts.recorded}</td>
                      <td data-sort-value={counts.present}>{counts.present}</td>
                      <td data-sort-value={counts.absent}>{counts.absent}</td>
                      <td data-sort-value={counts.excused}>{counts.excused}</td>
                      <td data-sort-value={counts.rate ?? -1}>{counts.rate === null ? '—' : `${counts.rate}%`}</td>
                    </tr>
                  );
                })}
              </Table>
            ) : (
              <NoRecords filtered action={t('Show this month', 'عرض الشهر الحالي')} onAction={() => { setFrom(`${today.slice(0, 7)}-01`); setTo(today); setPeriodPreset('month'); }} />
            )}
          </section>

          {/* Recorded Absence Follow-up Table */}
          <section className="panel feature-card">
            <h2>{t('Recorded absence follow-up', 'متابعة الغياب المسجّل')}</h2>
            <p className="info-note">{t('An operational list, not a prediction of student risk or learning level.', 'قائمة متابعة من سجلات الغياب، وليست توقعًا لخطر التسرب أو مستوى الطالب.')}</p>
            {absences.length ? (
              <Table
                caption={t('Students with recorded absence', 'طلاب لديهم غياب مسجّل')}
                headers={[t('Student', 'الطالب'), t('Absences', 'مرات الغياب'), t('Attendance', 'الحضور')]}
              >
                {absences.map(({ student, absent, rate }) => (
                  <tr key={student.id}>
                    <td><a className="text-link" href={link(student)}>{pick(student.name)}</a></td>
                    <td data-sort-value={absent}>{absent}</td>
                    <td data-sort-value={rate ?? -1}>{rate}%</td>
                  </tr>
                ))}
              </Table>
            ) : (
              <p>{t('No recorded absences in this period.', 'لا يوجد غياب مسجّل خلال الفترة دي.')}</p>
            )}
          </section>

          {/* Learning evidence card */}
          <section className="panel feature-card">
            <h2>{t('Learning evidence', 'تقييم المستوى الدراسي')}</h2>
            <p>{t('No approved student-linked assessment results are connected yet. Learning levels and syllabus coverage are unavailable.', 'لا توجد نتائج اختبارات معتمدة مرتبطة بالطلاب حاليًا. تقييم المستوى وتغطية المنهج غير متاحين.')}</p>
          </section>
        </>
      )}
    </>
  );
}
