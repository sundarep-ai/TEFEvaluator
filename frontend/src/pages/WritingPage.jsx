import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { evaluateBoth } from '../api/index.js';

const WRITING_TIME_MINUTES = 60;
const MIN_WORDS_A = 80;
const MIN_WORDS_B = 200;

function countWords(text) {
  return (text.trim().match(/\b\w+\b/g) || []).length;
}

function formatTime(ms) {
  const total = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function WritingPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const taskAQuestion = location.state?.taskAQuestion ?? '';
  const taskBQuestion = location.state?.taskBQuestion ?? '';

  const [responseA, setResponseA] = useState('');
  const [responseB, setResponseB] = useState('');
  const [timeLeft, setTimeLeft] = useState(WRITING_TIME_MINUTES * 60 * 1000);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const endAtRef = useRef(Date.now() + WRITING_TIME_MINUTES * 60 * 1000);
  const timerRef = useRef(null);

  // Redirect if no questions passed
  useEffect(() => {
    if (!taskAQuestion || !taskBQuestion) {
      navigate('/practice', { replace: true });
    }
  }, [taskAQuestion, taskBQuestion, navigate]);

  // Timer
  useEffect(() => {
    timerRef.current = setInterval(() => {
      const remaining = endAtRef.current - Date.now();
      setTimeLeft(remaining);
      if (remaining <= 0) clearInterval(timerRef.current);
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, []);

  const wordsA = countWords(responseA);
  const wordsB = countWords(responseB);
  const canSubmit = responseA.trim().length > 0 && responseB.trim().length > 0 && !submitting;

  const timePct = Math.max(0, (timeLeft / (WRITING_TIME_MINUTES * 60 * 1000)) * 100);
  const isUrgent = timeLeft < 10 * 60 * 1000;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setSubmitError('');
    clearInterval(timerRef.current);

    try {
      const result = await evaluateBoth({
        task_a_question: taskAQuestion,
        task_a_response: responseA,
        task_b_question: taskBQuestion,
        task_b_response: responseB,
      });

      navigate('/practice/results', {
        state: {
          evaluation: result,
          taskAQuestion,
          taskBQuestion,
          responseA,
          responseB,
        },
      });
    } catch (err) {
      setSubmitError("Échec de l'évaluation. Veuillez réessayer.");
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* Timer banner */}
      <div className={`mb-8 rounded-xl p-4 flex items-center justify-between ${isUrgent ? 'bg-error-container' : 'bg-primary-fixed/30 dark:bg-indigo-900/20'}`}>
        <div className="flex items-center gap-3">
          <span className={`material-symbols-outlined text-xl ${isUrgent ? 'text-error' : 'text-primary'}`}>timer</span>
          <span className={`text-sm font-semibold ${isUrgent ? 'text-error' : 'text-primary dark:text-indigo-300'}`}>
            Temps restant
          </span>
        </div>
        <span className={`text-2xl font-headline font-extrabold tabular-nums ${isUrgent ? 'text-error animate-pulse' : 'text-primary dark:text-indigo-300'}`}>
          {formatTime(timeLeft)}
        </span>
        <div className="w-48 h-2 bg-outline-variant/20 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ${isUrgent ? 'bg-error' : 'bg-secondary'}`}
            style={{ width: `${timePct}%` }}
          />
        </div>
      </div>

      {/* Page header */}
      <section className="mb-8">
        <h2 className="text-3xl font-headline font-extrabold text-primary dark:text-indigo-300 tracking-tight mb-1">
          Session d'écriture
        </h2>
        <p className="text-on-surface-variant text-sm">
          Rédigez vos réponses aux deux tâches. Cliquez sur "Soumettre" lorsque vous avez terminé.
        </p>
      </section>

      <div className="space-y-8">
        {/* Task A */}
        <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
          <div className="px-8 py-5 border-b border-outline-variant/20 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-primary-fixed flex items-center justify-center text-primary flex-shrink-0">
                <span className="material-symbols-outlined">article</span>
              </div>
              <div>
                <h3 className="font-headline font-bold text-on-surface dark:text-white">
                  Tâche A — Récit
                </h3>
                <p className="text-xs text-on-surface-variant">Minimum {MIN_WORDS_A} mots</p>
              </div>
            </div>
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-bold ${wordsA >= MIN_WORDS_A ? 'bg-secondary/10 text-secondary' : 'bg-surface-container-low dark:bg-slate-700 text-on-surface-variant'}`}>
              <span className="material-symbols-outlined text-base">format_size</span>
              {wordsA} mots
            </div>
          </div>

          <div className="p-8 space-y-4">
            <div className="bg-primary-fixed/20 dark:bg-indigo-900/20 rounded-lg p-4 text-sm text-on-surface dark:text-indigo-100 leading-relaxed border-l-4 border-primary/30">
              {taskAQuestion}
            </div>
            <textarea
              className="w-full px-4 py-3 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg resize-none text-sm leading-relaxed outline-none focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline/50"
              rows={8}
              placeholder="Commencez votre réponse à la Tâche A ici..."
              value={responseA}
              onChange={(e) => setResponseA(e.target.value)}
              disabled={submitting}
            />
            <div className="flex justify-between text-xs text-on-surface-variant">
              <button
                onClick={() => setResponseA('')}
                disabled={submitting}
                className="flex items-center gap-1 hover:text-error transition-colors disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-sm">restart_alt</span>
                Réinitialiser
              </button>
              <span className={wordsA >= MIN_WORDS_A ? 'text-secondary font-semibold' : ''}>
                {wordsA >= MIN_WORDS_A ? '✓ Minimum atteint' : `${MIN_WORDS_A - wordsA} mots restants`}
              </span>
            </div>
          </div>
        </div>

        {/* Task B */}
        <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
          <div className="px-8 py-5 border-b border-outline-variant/20 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center text-secondary flex-shrink-0">
                <span className="material-symbols-outlined">mail</span>
              </div>
              <div>
                <h3 className="font-headline font-bold text-on-surface dark:text-white">
                  Tâche B — Lettre formelle
                </h3>
                <p className="text-xs text-on-surface-variant">Minimum {MIN_WORDS_B} mots</p>
              </div>
            </div>
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-bold ${wordsB >= MIN_WORDS_B ? 'bg-secondary/10 text-secondary' : 'bg-surface-container-low dark:bg-slate-700 text-on-surface-variant'}`}>
              <span className="material-symbols-outlined text-base">format_size</span>
              {wordsB} mots
            </div>
          </div>

          <div className="p-8 space-y-4">
            <div className="bg-secondary-container/30 dark:bg-teal-900/20 rounded-lg p-4 text-sm text-on-surface dark:text-teal-100 leading-relaxed border-l-4 border-secondary/30">
              {taskBQuestion}
            </div>
            <textarea
              className="w-full px-4 py-3 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg resize-none text-sm leading-relaxed outline-none focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline/50"
              rows={12}
              placeholder="Commencez votre réponse à la Tâche B ici..."
              value={responseB}
              onChange={(e) => setResponseB(e.target.value)}
              disabled={submitting}
            />
            <div className="flex justify-between text-xs text-on-surface-variant">
              <button
                onClick={() => setResponseB('')}
                disabled={submitting}
                className="flex items-center gap-1 hover:text-error transition-colors disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-sm">restart_alt</span>
                Réinitialiser
              </button>
              <span className={wordsB >= MIN_WORDS_B ? 'text-secondary font-semibold' : ''}>
                {wordsB >= MIN_WORDS_B ? '✓ Minimum atteint' : `${MIN_WORDS_B - wordsB} mots restants`}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Submit area */}
      {submitError && (
        <div className="mt-6 bg-error-container text-on-error-container rounded-lg px-5 py-4 flex items-center gap-3 text-sm">
          <span className="material-symbols-outlined text-xl">error</span>
          {submitError}
        </div>
      )}

      <div className="mt-8 flex items-center justify-between">
        <p className="text-xs text-on-surface-variant">
          {!canSubmit && !submitting && 'Rédigez vos deux réponses avant de soumettre.'}
        </p>
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="flex items-center gap-2 px-10 py-4 primary-gradient text-white rounded-xl font-bold text-sm shadow-lg shadow-primary/20 hover:shadow-primary/30 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
        >
          {submitting ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Évaluation en cours... (peut prendre jusqu'à 5 min)</span>
            </>
          ) : (
            <>
              <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
              <span>Soumettre pour évaluation</span>
            </>
          )}
        </button>
      </div>

      {/* Evaluation loading overlay */}
      {submitting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-2xl p-12 text-center max-w-md w-full mx-4 canvas-shadow">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
            <h3 className="font-headline font-extrabold text-xl text-primary dark:text-indigo-300 mb-3">
              Évaluation en cours
            </h3>
            <p className="text-on-surface-variant text-sm leading-relaxed">
              Votre texte est analysé par notre système d'IA avancé. Ce processus peut prendre jusqu'à 5 minutes.
              Veuillez patienter.
            </p>
          </div>
        </div>
      )}
    </>
  );
}
