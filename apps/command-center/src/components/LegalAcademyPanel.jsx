import React from 'react';
import { Award, Bell, BookOpen, CalendarClock, CheckCircle2, GraduationCap, Play, ShieldCheck } from 'lucide-react';

const STATUS_BADGES = {
  POR_INICIAR: { label: 'POR INICIAR', className: 'acad-badge-upcoming' },
  EN_CURSO: { label: 'EN CURSO', className: 'acad-badge-active' },
  EVALUACION_PENDIENTE: { label: 'EVALUACIÓN', className: 'acad-badge-eval' },
  CERTIFICADO: { label: 'CERTIFICADO', className: 'acad-badge-done' },
};

export default function LegalAcademyPanel({ courses, onAdvanceCourse }) {
  const startingSoonCount = courses.filter(
    (c) => c.status === 'POR_INICIAR' && c.daysUntil <= 7
  ).length;
  const inProgressCount = courses.filter(
    (c) => c.status === 'EN_CURSO' || c.status === 'EVALUACION_PENDIENTE'
  ).length;
  const certificatesEarnedCount = courses.filter((c) => c.status === 'CERTIFICADO').length;
  const completedCreditHours = courses
    .filter((c) => c.status === 'CERTIFICADO')
    .reduce((acc, c) => acc + c.creditHours, 0);

  const activeReminders = courses
    .filter((c) => c.status !== 'CERTIFICADO')
    .sort((a, b) => a.daysUntil - b.daysUntil);

  return (
    <section
      id="legal-academy-section"
      className="panel-card legal-academy-panel"
      aria-labelledby="legal-academy-heading"
    >
      <div className="panel-header">
        <div>
          <div className="panel-eyebrow">
            <GraduationCap size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>Educación Jurídica Continua (Irnerio · Especializado en Práctica Legal)</span>
          </div>
          <h2 id="legal-academy-heading" className="panel-title">
            Academia Legal, Diplomados y Certificaciones
          </h2>
        </div>

        <span className="academy-isolation-badge" title="Aislado de suscripciones o cursos ajenos al Derecho">
          <ShieldCheck size={13} strokeWidth={1.75} aria-hidden="true" />
          <span>Exclusivo Práctica Legal</span>
        </span>
      </div>

      {/* KPI Strip */}
      <div className="academy-kpi-grid" role="region" aria-label="Resumen anual de educación continua">
        <div className="academy-kpi-card">
          <span className="academy-kpi-label">Inicios Próximos</span>
          <strong className="academy-kpi-value">{startingSoonCount}</strong>
          <span className="academy-kpi-sub">Con alerta temprana activa</span>
        </div>
        <div className="academy-kpi-card">
          <span className="academy-kpi-label">Diplomados Activos</span>
          <strong className="academy-kpi-value">{inProgressCount}</strong>
          <span className="academy-kpi-sub">Seguimiento modular</span>
        </div>
        <div className="academy-kpi-card">
          <span className="academy-kpi-label">Certificados del Año</span>
          <strong className="academy-kpi-value is-sage">{certificatesEarnedCount}</strong>
          <span className="academy-kpi-sub">Diplomas legales logrados</span>
        </div>
        <div className="academy-kpi-card">
          <span className="academy-kpi-label">Horas Acreditadas</span>
          <strong className="academy-kpi-value">{completedCreditHours} h</strong>
          <span className="academy-kpi-sub">Educación continua verificada</span>
        </div>
      </div>

      {/* Early Reminders Banner */}
      {activeReminders.length > 0 && (
        <div className="academy-reminders-box" role="region" aria-label="Recordatorios de inicio y evaluación">
          <div className="academy-reminders-title">
            <Bell size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>Recordatorios Próximos de Irnerio ({activeReminders.length} pendientes)</span>
          </div>
          <ul className="academy-reminder-list">
            {activeReminders.map((rem) => (
              <li key={rem.id} className={`academy-reminder-item urgency-${rem.urgency}`}>
                <span className="acad-rem-days mono-inline">T-{rem.daysUntil}d</span>
                <span className="acad-rem-text">
                  <strong>{rem.title}</strong> ({rem.startDate}) — {rem.nextMilestoneLabel}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Course Cards */}
      <div className="academy-course-list">
        {courses.map((course) => {
          const badge = STATUS_BADGES[course.status] || STATUS_BADGES.POR_INICIAR;
          const isCertified = course.status === 'CERTIFICADO';
          const isNotStarted = course.status === 'POR_INICIAR';
          return (
            <article key={course.id} className={`academy-course-card status-${course.status.toLowerCase()}`}>
              <div className="academy-course-top">
                <div className="academy-course-badges">
                  <span className="acad-kind-chip">{course.kind}</span>
                  <span className="acad-area-chip">{course.practiceArea}</span>
                </div>
                <span className={`acad-status-pill ${badge.className}`}>{badge.label}</span>
              </div>

              <h3 className="academy-course-title">{course.title}</h3>
              <p className="academy-course-inst">{course.institution}</p>

              <div className="academy-course-meta">
                <span>
                  <CalendarClock size={12} strokeWidth={1.75} aria-hidden="true" />
                  <span>
                    {course.startDate} &rarr; {course.endDate} ({course.creditHours} h)
                  </span>
                </span>
                <span>
                  <BookOpen size={12} strokeWidth={1.75} aria-hidden="true" />
                  <span>Enlace Consejo: {course.linkedCouncilAgent}</span>
                </span>
              </div>

              <div className="academy-progress-row">
                <div className="academy-progress-track" aria-hidden="true">
                  <div className="academy-progress-fill" style={{ width: `${course.progressPct}%` }} />
                </div>
                <span className="academy-progress-pct mono-inline">{course.progressPct}%</span>
              </div>

              <div className="academy-course-footer">
                {isCertified ? (
                  <span className="academy-cert-folio">
                    <Award size={14} strokeWidth={1.75} aria-hidden="true" />
                    <span>Folio Certificado: {course.certificateFolio}</span>
                  </span>
                ) : (
                  <span className="academy-milestone-note">{course.nextMilestoneLabel}</span>
                )}

                {!isCertified && (
                  <button
                    type="button"
                    className={`btn btn-sm ${isNotStarted ? 'btn-primary' : 'btn-sage'}`}
                    onClick={() => onAdvanceCourse(course.id)}
                  >
                    {isNotStarted ? (
                      <>
                        <Play size={13} strokeWidth={1.75} aria-hidden="true" />
                        <span>Iniciar Curso</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 size={13} strokeWidth={1.75} aria-hidden="true" />
                        <span>Registrar Certificado</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
