import { useState } from 'react';
import { ArrowLeft, ArrowUpRight } from 'lucide-react';
import { useWorkspace } from '../../data/WorkspaceProvider';
import { chargeBalance, eligible, outstanding } from '../../domain/workspace';
import { attendanceSummary } from '../../domain/reports';
import { StudentForm } from '../../features/Operations';
import { Heading, Status, Table } from '../ui/FeatureUi';
import { Button, Modal } from '../ui/Base';
import { AcademicRiskCard } from './AcademicRiskCard';

export function StudentProfile({ student }) {
  const { data, t, pick, date, money, can, grade } = useWorkspace(), [edit, setEdit] = useState(false);
  const enrollments = data.enrollments.filter(e => e.studentId === student.id);
  const sessions = data.sessions.filter(s => eligible(data, student.id, s));
  const records = data.attendance.filter(a => a.studentId === student.id), summary = attendanceSummary(records);
  const payments = data.payments.filter(p => p.studentId === student.id), charges = data.charges.filter(c => c.studentId === student.id);
  const rawGrades = student.grade ? [student.grade] : [...new Set(enrollments.map(e => data.groups.find(g => g.id === e.groupId)?.grade).filter(Boolean))];
  const displayGrade = rawGrades.length ? rawGrades.map(g => grade(g)).join(' / ') : t('Not provided', 'غير مضاف');
  return <><a className="text-link profile-back" href="#students"><ArrowLeft size={16} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineEnd: '6px' }} />{t('Student directory', 'دليل الطلاب')}</a><Heading title={pick(student.name)} description={student.code}>{can('roster.write') && <Button onClick={()=>setEdit(true)}>{t('Edit profile','تعديل الملف')}</Button>}</Heading>
    <section className="panel feature-card"><Status value={student.status}/><dl className="profile-facts">{[[t('Phone','التليفون'),student.phone],[t('Guardian','ولي الأمر'),student.guardianName],[t('Guardian phone','تليفون ولي الأمر'),student.guardianPhone],[t('Grade','الصف'),displayGrade]].map(([label,value])=><div key={label}><dt>{label}</dt><dd><bdi>{value || t('Not provided','غير مضاف')}</bdi></dd></div>)}</dl><p className="profile-notes">{student.notes || t('No notes saved.','لا توجد ملاحظات محفوظة.')}</p></section>
    <div className="stats-grid"><section className="stat-card"><span>{t('Attendance','الحضور')}</span><strong className="stat-value">{summary.rate === null ? '—' : `${summary.rate}%`}</strong><p>{summary.present} / {summary.denominator} · {t('Excused excluded','باستثناء بعذر')}</p></section><section className="stat-card"><span>{t('Absence','الغياب')}</span><strong className="stat-value">{summary.absent}</strong><p>{t('Saved records only','السجلات المحفوظة فقط')}</p></section>{can('payments') && <a className="stat-card metric-link" href={`#payments?studentId=${student.id}`}><span>{t('Outstanding','المتبقي')}</span><strong className="stat-value">{money(outstanding(data,student.id))}</strong><p>{t('Open financial records','فتح السجلات المالية')} <ArrowUpRight size={13} className="directional" style={{ display: 'inline', verticalAlign: 'middle', marginInlineStart: '4px' }} /></p></a>}</div>
    <AcademicRiskCard student={student} summary={summary} />
    <section className="panel feature-card"><h2>{t('Enrollments','الاشتراكات')}</h2>{enrollments.length ? enrollments.map(e=><a className="session-link" key={e.id} href={`#students?groupId=${e.groupId}&status=all`}>{pick(data.groups.find(g=>g.id===e.groupId)?.name)} · {date(e.startDate)} — {e.endDate ? date(e.endDate) : t('Open-ended','مفتوح')}</a>) : <p>{t('No enrollments','لا توجد اشتراكات')}</p>}</section>

    <section className="panel ledger-panel"><h2>{t('Attendance history','سجل الحضور')}</h2><Table caption={t('Student sessions','حصص الطالب')} headers={[t('Session','الحصة'),t('Date','التاريخ'),t('Status','الحالة')]}>{sessions.map(s=><tr key={s.id}><td><a className="text-link" href={`#attendance?sessionId=${s.id}`}>{pick(s.title)}</a></td><td>{date(s.date)} · {s.startTime}</td><td><Status value={records.find(a=>a.sessionId===s.id)?.status || 'unrecorded'}/></td></tr>)}</Table></section>
    {can('payments') && <><section className="panel ledger-panel"><h2>{t('Charges','الرسوم')}</h2><Table caption={t('Student charges','رسوم الطالب')} headers={[t('Description','الوصف'),t('Due date','الاستحقاق'),t('Outstanding','المتبقي')]}>{charges.map(c=><tr key={c.id}><td><a className="text-link" href={`#payments?studentId=${student.id}`}>{pick(c.description)}</a></td><td>{date(c.dueDate)}</td><td>{money(chargeBalance(data,c))}</td></tr>)}</Table></section><section className="panel ledger-panel"><h2>{t('Payments','التحصيلات')}</h2><Table caption={t('Student receipts','إيصالات الطالب')} headers={[t('Reference','المرجع'),t('Date','التاريخ'),t('Original amount','المبلغ الأصلي')]}>{payments.map(p=><tr key={p.id}><td><a className="text-link" href={`#payments?studentId=${student.id}`}><bdi>{p.reference}</bdi></a></td><td>{date(p.createdAt,true)}</td><td>{money(p.amountMinor)}</td></tr>)}</Table></section></>}
    <section className="panel feature-card"><h2>{t('Assessment results','نتائج الاختبارات')}</h2><p>{t('No approved student-linked grades are available. Essay demo suggestions are not final grades.','لا توجد درجات معتمدة مرتبطة بالطالب. اقتراحات تجربة المقالي ليست درجات نهائية.')}</p></section>
    <Modal open={edit} onClose={()=>setEdit(false)} title={t('Edit student','تعديل بيانات الطالب')} description={t('Details stay linked to the same student record.','البيانات تظل مرتبطة بنفس سجل الطالب.')}><StudentForm student={student} onDone={()=>setEdit(false)}/></Modal>
  </>;
}
