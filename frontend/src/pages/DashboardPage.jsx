import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { getSubmissions } from '../api/index.js';

function scoreLabel(score) {
  if (score >= 600) return { text: 'Excellence', cls: 'bg-secondary/10 text-secondary' };
  if (score >= 500) return { text: 'Avancé', cls: 'bg-primary-fixed text-on-primary-fixed' };
  if (score >= 400) return { text: 'Intermédiaire', cls: 'bg-tertiary-fixed text-on-tertiary-fixed-variant' };
  return { text: 'À améliorer', cls: 'bg-error-container text-on-error-container' };
}

function formatDate(iso) {
  return new Intl.DateTimeFormat('fr-CA', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Toronto',
  }).format(new Date(iso));
}

function SubmissionItem({ submission, onClick }) {
  const label = scoreLabel(submission.final_score);
  return (
    <div
      className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-5 flex items-center justify-between transition-all hover:translate-x-1 cursor-pointer"
      onClick={() => onClick(submission)}
    >
      <div className="flex items-center space-x-5">
        <div className="w-12 h-12 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-primary">
          <span className="material-symbols-outlined">edit_note</span>
        </div>
        <div>
          <h4 className="font-bold text-primary dark:text-indigo-300">Expression Écrite — Tâche A + B</h4>
          <p className="text-xs text-on-surface-variant">{formatDate(submission.created_at)}</p>
        </div>
      </div>
      <div className="flex items-center space-x-8">
        <div className="text-right">
          <p className="text-sm font-label text-on-surface-variant font-bold uppercase tracking-tighter">Score</p>
          <p className="text-lg font-headline font-bold text-primary dark:text-indigo-300">
            {submission.final_score ?? '—'} <span className="text-xs font-normal text-on-surface-variant">/ 700</span>
          </p>
        </div>
        <div className="w-28 text-right">
          <span className={`px-3 py-1 text-xs font-bold rounded-full ${label.cls}`}>{label.text}</span>
        </div>
      </div>
    </div>
  );
}

function SubmissionModal({ submission, onClose }) {
  if (!submission) return null;

  const renderPairs = (originals, corrections) => {
    if (!Array.isArray(originals) || originals.length === 0) return null;
    return (
      <div className="mt-3 space-y-1">
        {originals.map((orig, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            <span className="text-error line-through">{orig}</span>
            <span className="material-symbols-outlined text-on-surface-variant text-base">arrow_forward</span>
            <span className="text-secondary font-medium">{corrections?.[i] ?? ''}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div
        className="bg-surface-container-lowest dark:bg-slate-900 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto canvas-shadow"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-surface-container-lowest dark:bg-slate-900 px-8 py-6 border-b border-outline-variant/20 flex items-center justify-between">
          <div>
            <h3 className="font-headline font-extrabold text-xl text-primary">Détails de la session</h3>
            <p className="text-xs text-on-surface-variant mt-1">{formatDate(submission.created_at)}</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-3xl font-headline font-extrabold text-primary">{submission.final_score}<span className="text-base font-normal text-on-surface-variant"> / 700</span></span>
            <button onClick={onClose} className="text-on-surface-variant hover:text-primary transition-colors">
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        <div className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Task A */}
          <div className="space-y-4">
            <h4 className="font-headline font-bold text-lg text-primary flex items-center gap-2">
              <span className="material-symbols-outlined text-xl">article</span>
              Tâche A — Récit
            </h4>
            <div className="bg-surface-container-low dark:bg-slate-800 rounded-xl p-5 space-y-3 text-sm">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-1">Question</p>
                <p className="text-on-surface dark:text-slate-200 leading-relaxed">{submission.task_a_question}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-1">Votre réponse</p>
                <p className="text-on-surface dark:text-slate-300 leading-relaxed whitespace-pre-wrap">{submission.task_a_response}</p>
              </div>
              {submission.justification_a && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-primary mb-1">Analyse</p>
                  <p className="text-on-surface-variant leading-relaxed">{submission.justification_a}</p>
                </div>
              )}
              {submission.recommendation_a && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-secondary mb-1">Recommandation</p>
                  <p className="text-on-surface-variant leading-relaxed">{submission.recommendation_a}</p>
                </div>
              )}
              {renderPairs(submission.originals_a, submission.corrections_a)}
              {submission.ai_improved_answer_taskA && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-on-primary-container mb-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">auto_awesome</span>Version améliorée par l'IA
                  </p>
                  <p className="text-on-surface dark:text-slate-200 leading-relaxed whitespace-pre-wrap bg-primary-fixed/30 rounded-lg p-3">{submission.ai_improved_answer_taskA}</p>
                </div>
              )}
            </div>
          </div>

          {/* Task B */}
          <div className="space-y-4">
            <h4 className="font-headline font-bold text-lg text-primary flex items-center gap-2">
              <span className="material-symbols-outlined text-xl">mail</span>
              Tâche B — Lettre formelle
            </h4>
            <div className="bg-surface-container-low dark:bg-slate-800 rounded-xl p-5 space-y-3 text-sm">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-1">Question</p>
                <p className="text-on-surface dark:text-slate-200 leading-relaxed">{submission.task_b_question}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-1">Votre réponse</p>
                <p className="text-on-surface dark:text-slate-300 leading-relaxed whitespace-pre-wrap">{submission.task_b_response}</p>
              </div>
              {submission.justification_b && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-primary mb-1">Analyse</p>
                  <p className="text-on-surface-variant leading-relaxed">{submission.justification_b}</p>
                </div>
              )}
              {submission.recommendation_b && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-secondary mb-1">Recommandation</p>
                  <p className="text-on-surface-variant leading-relaxed">{submission.recommendation_b}</p>
                </div>
              )}
              {renderPairs(submission.originals_b, submission.corrections_b)}
              {submission.ai_improved_answer_taskB && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-on-primary-container mb-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">auto_awesome</span>Version améliorée par l'IA
                  </p>
                  <p className="text-on-surface dark:text-slate-200 leading-relaxed whitespace-pre-wrap bg-primary-fixed/30 rounded-lg p-3">{submission.ai_improved_answer_taskB}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    getSubmissions()
      .then(setSubmissions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const latest = submissions[0];
  const avgScore = submissions.length
    ? Math.round(submissions.reduce((sum, s) => sum + (s.final_score ?? 0), 0) / submissions.length)
    : 0;
  const bestScore = submissions.length ? Math.max(...submissions.map((s) => s.final_score ?? 0)) : 0;
  const progressPct = submissions.length
    ? Math.round(((avgScore - 150) / (700 - 150)) * 100)
    : 0;
  const gaugeOffset = 552.9 - (552.9 * Math.max(0, Math.min(100, progressPct))) / 100;

  return (
    <>
      {/* Hero */}
      <section className="mb-12">
        <h2 className="text-4xl font-headline font-extrabold text-primary dark:text-indigo-300 tracking-tight mb-2">
          Bienvenue, {user?.username}
        </h2>
        <p className="text-on-surface-variant max-w-2xl leading-relaxed">
          Prêt à poursuivre votre préparation au TEF ? Chaque session vous rapproche de votre objectif.
        </p>
      </section>

      {/* Bento grid */}
      <div className="grid grid-cols-12 gap-8">
        {/* Performance gauge */}
        <div className="col-span-12 lg:col-span-8 bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-10 canvas-shadow flex flex-col md:flex-row items-center gap-12">
          {submissions.length > 0 ? (
            <>
              <div className="relative w-48 h-48 flex items-center justify-center flex-shrink-0">
                <svg className="w-full h-full transform -rotate-90">
                  <circle className="text-surface-container-high dark:text-slate-700" cx="96" cy="96" fill="transparent" r="88" stroke="currentColor" strokeWidth="12" />
                  <circle
                    className="text-secondary"
                    cx="96" cy="96" fill="transparent" r="88"
                    stroke="currentColor"
                    strokeDasharray="552.9"
                    strokeDashoffset={gaugeOffset}
                    strokeLinecap="round"
                    strokeWidth="12"
                  />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-4xl font-headline font-extrabold text-primary dark:text-indigo-300">
                    {progressPct}%
                  </span>
                  <span className="text-xs font-label uppercase tracking-widest text-on-surface-variant font-bold">
                    Progression
                  </span>
                </div>
              </div>

              <div className="flex-1 grid grid-cols-2 gap-6">
                <div className="bg-surface-container-low dark:bg-slate-700/50 p-6 rounded-lg">
                  <p className="text-xs font-label uppercase tracking-widest text-on-surface-variant font-bold mb-2">Meilleur score</p>
                  <p className="text-3xl font-headline font-bold text-primary dark:text-indigo-300">{bestScore}</p>
                  <p className="text-xs text-on-surface-variant mt-1">sur 700 points</p>
                </div>
                <div className="bg-surface-container-low dark:bg-slate-700/50 p-6 rounded-lg">
                  <p className="text-xs font-label uppercase tracking-widest text-on-surface-variant font-bold mb-2">Sessions</p>
                  <p className="text-3xl font-headline font-bold text-primary dark:text-indigo-300">{submissions.length}</p>
                  <div className="w-full bg-outline-variant/20 h-1.5 rounded-full mt-3 overflow-hidden">
                    <div className="bg-secondary h-full rounded-full" style={{ width: `${Math.min(100, (submissions.length / 20) * 100)}%` }} />
                  </div>
                </div>
                <div className="bg-surface-container-low dark:bg-slate-700/50 p-6 rounded-lg">
                  <p className="text-xs font-label uppercase tracking-widest text-on-surface-variant font-bold mb-2">Score moyen</p>
                  <p className="text-3xl font-headline font-bold text-primary dark:text-indigo-300">{avgScore}</p>
                  <p className="text-xs text-on-surface-variant mt-1">sur 700 points</p>
                </div>
                <div className="bg-surface-container-low dark:bg-slate-700/50 p-6 rounded-lg">
                  <p className="text-xs font-label uppercase tracking-widest text-on-surface-variant font-bold mb-2">Objectif</p>
                  <p className="text-3xl font-headline font-bold text-primary dark:text-indigo-300">700</p>
                  <p className="text-xs text-on-surface-variant mt-1">Score maximum TEF</p>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-8">
              <span className="material-symbols-outlined text-6xl text-outline-variant mb-4">analytics</span>
              <p className="font-headline font-bold text-xl text-on-surface-variant mb-2">Aucune donnée encore</p>
              <p className="text-on-surface-variant text-sm">Commencez votre première session pour voir vos statistiques.</p>
            </div>
          )}
        </div>

        {/* Latest submission spotlight */}
        <div className="col-span-12 lg:col-span-4 primary-gradient rounded-xl p-8 text-white flex flex-col justify-between overflow-hidden relative">
          <div className="relative z-10">
            <div className="bg-white/20 backdrop-blur-md rounded-full px-4 py-1 inline-block mb-6">
              <span className="text-[10px] font-bold uppercase tracking-wider">Dernière Soumission</span>
            </div>
            {latest ? (
              <>
                <h3 className="text-2xl font-headline font-bold mb-2">Expression Écrite</h3>
                <p className="text-indigo-200 text-sm leading-relaxed mb-6 line-clamp-3">
                  {latest.task_b_question || latest.task_a_question || '—'}
                </p>
                <div className="flex items-end space-x-2">
                  <span className="text-5xl font-headline font-extrabold">{latest.final_score}</span>
                  <span className="text-xl text-indigo-300 font-medium mb-1">/ 700</span>
                </div>
              </>
            ) : (
              <div className="py-8 text-center">
                <span className="material-symbols-outlined text-5xl text-white/30 mb-4 block">inbox</span>
                <p className="text-indigo-200 text-sm">Aucune soumission encore. Lancez votre première session !</p>
              </div>
            )}
          </div>
          {latest && (
            <button
              className="relative z-10 mt-8 bg-white text-primary font-bold py-3 px-6 rounded-lg hover:bg-indigo-50 transition-colors flex items-center justify-center space-x-2"
              onClick={() => setSelected(latest)}
            >
              <span>Voir l'analyse détaillée</span>
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          )}
          <div className="absolute -right-12 -bottom-12 w-48 h-48 bg-white/5 rounded-full blur-3xl" />
        </div>

        {/* History list */}
        <div className="col-span-12 bg-surface-container-low dark:bg-slate-800/60 rounded-xl p-10">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h3 className="text-2xl font-headline font-extrabold text-primary dark:text-indigo-300 mb-1">
                Historique des Soumissions
              </h3>
              <p className="text-on-surface-variant text-sm">Consultez le détail de chaque session d'écriture</p>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : submissions.length === 0 ? (
            <div className="text-center py-12">
              <span className="material-symbols-outlined text-5xl text-outline-variant mb-3 block">inbox</span>
              <p className="text-on-surface-variant">Aucune soumission. Commencez une session de pratique !</p>
            </div>
          ) : (
            <div className="space-y-4">
              {submissions.map((s) => (
                <SubmissionItem key={s.id} submission={s} onClick={setSelected} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-16 flex items-center justify-between border-t border-outline-variant/10 pt-8">
        <div className="flex items-center space-x-8 text-sm text-on-surface-variant font-medium">
          <span className="hover:text-primary transition-colors cursor-default">Conditions d'utilisation</span>
          <span className="hover:text-primary transition-colors cursor-default">Centre d'aide</span>
        </div>
        <p className="text-xs text-on-surface-variant italic">© 2025 L'Atelier — Excellence en Français</p>
      </footer>

      {/* FAB */}
      <button
        className="fixed bottom-10 right-10 primary-gradient text-white w-16 h-16 rounded-full shadow-2xl flex items-center justify-center hover:scale-105 transition-transform active:scale-95 group z-50"
        onClick={() => navigate('/practice')}
        title="Nouvelle session"
      >
        <span
          className="material-symbols-outlined text-3xl group-hover:rotate-12 transition-transform"
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          add_task
        </span>
        <div className="absolute right-20 bg-primary-container text-white px-4 py-2 rounded-lg text-sm font-bold opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
          Nouvelle Session
        </div>
      </button>

      {/* Modal */}
      {selected && <SubmissionModal submission={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
