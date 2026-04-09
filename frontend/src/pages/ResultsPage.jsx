import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { generateImprovedAnswer } from '../api/index.js';

function ScoreRing({ score, max = 700 }) {
  const pct = Math.max(0, Math.min(1, (score - 150) / (max - 150)));
  const circumference = 2 * Math.PI * 80;
  const offset = circumference - pct * circumference;
  return (
    <div className="relative w-48 h-48 flex-shrink-0">
      <svg className="w-full h-full transform -rotate-90">
        <circle className="text-white/10" cx="96" cy="96" fill="transparent" r="80" stroke="currentColor" strokeWidth="12" />
        <circle
          className="text-secondary-fixed"
          cx="96" cy="96" fill="transparent" r="80"
          stroke="currentColor"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          strokeWidth="12"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">
          {score >= 600 ? 'C2' : score >= 500 ? 'C1' : score >= 400 ? 'B2' : score >= 300 ? 'B1' : 'A2'}
        </span>
        <span className="text-xs text-indigo-200">
          {score >= 600 ? 'Maîtrise' : score >= 500 ? 'Avancé' : score >= 400 ? 'Intermédiaire sup.' : 'Intermédiaire'}
        </span>
      </div>
    </div>
  );
}

function ErrorCard({ type, color, title, items }) {
  const borderColor = {
    error: 'border-error',
    warning: 'border-tertiary-fixed-dim',
    primary: 'border-primary',
    secondary: 'border-secondary',
  }[color] ?? 'border-outline-variant';

  const badgeColor = {
    error: 'bg-error-container text-on-error-container',
    warning: 'bg-tertiary-fixed text-on-tertiary-container',
    primary: 'bg-primary-fixed text-on-primary-fixed',
    secondary: 'bg-secondary-container text-on-secondary-container',
  }[color] ?? 'bg-surface-container text-on-surface';

  return (
    <div className={`bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-6 canvas-shadow border-l-4 ${borderColor}`}>
      <div className="flex justify-between items-start mb-3">
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${badgeColor}`}>{type}</span>
      </div>
      <p className="text-sm font-semibold mb-2 text-on-surface dark:text-white">{title}</p>
      <div className="space-y-1">
        {items.map((item, i) => (
          <div key={i} className="flex items-center gap-2 text-xs text-on-surface-variant">
            <span className="text-error line-through">{item.original}</span>
            <span className="material-symbols-outlined text-xs text-on-surface-variant">arrow_forward</span>
            <span className="text-secondary font-semibold">{item.correction}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { evaluation, taskAQuestion, taskBQuestion, responseA, responseB } =
    location.state ?? {};

  const [improvedA, setImprovedA] = useState('');
  const [improvedB, setImprovedB] = useState('');
  const [loadingImproved, setLoadingImproved] = useState(false);
  const [improvedLoaded, setImprovedLoaded] = useState(false);
  const [improvedError, setImprovedError] = useState('');
  const [draftView, setDraftView] = useState('A');

  if (!evaluation) {
    navigate('/practice', { replace: true });
    return null;
  }

  const finalScore = evaluation.finalScore ?? 0;
  const judgeA = evaluation.taskA?.judge ?? {};
  const judgeB = evaluation.taskB?.judge ?? {};

  const originalsA = Array.isArray(judgeA.originals) ? judgeA.originals : [];
  const correctionsA = Array.isArray(judgeA.corrections) ? judgeA.corrections : [];
  const originalsB = Array.isArray(judgeB.originals) ? judgeB.originals : [];
  const correctionsB = Array.isArray(judgeB.corrections) ? judgeB.corrections : [];

  const allCorrections = [
    ...originalsA.slice(0, 2).map((o, i) => ({
      type: 'Tâche A', color: 'primary', title: 'Correction', original: o, correction: correctionsA[i] ?? '',
    })),
    ...originalsB.slice(0, 2).map((o, i) => ({
      type: 'Tâche B', color: 'secondary', title: 'Correction', original: o, correction: correctionsB[i] ?? '',
    })),
  ];

  const scoreStatus = finalScore >= 500 ? 'Admissible (Pass)' : 'En progression';
  const progressPct = Math.round(((finalScore - 150) / (700 - 150)) * 100);

  const handleGenerateImproved = async () => {
    if (loadingImproved || improvedLoaded) return;
    setLoadingImproved(true);
    setImprovedError('');
    try {
      const [resA, resB] = await Promise.all([
        generateImprovedAnswer('A', taskAQuestion, responseA),
        generateImprovedAnswer('B', taskBQuestion, responseB),
      ]);
      setImprovedA(resA.improvedAnswer);
      setImprovedB(resB.improvedAnswer);
      setImprovedLoaded(true);
    } catch {
      setImprovedError("Erreur lors de la génération. Veuillez réessayer.");
    } finally {
      setLoadingImproved(false);
    }
  };

  return (
    <>
      {/* Page header */}
      <header className="mb-10">
        <h2 className="text-3xl font-headline font-extrabold text-primary dark:text-indigo-300 tracking-tight mb-2">
          {finalScore >= 500 ? 'Excellent travail — votre niveau TEF progresse !' : 'Continuez vos efforts — vous progressez !'}
        </h2>
        <p className="text-on-surface-variant font-body text-sm">
          Analyse IA détaillée pour votre session d'expression écrite
        </p>
      </header>

      {/* Score banner */}
      <section className="grid grid-cols-12 gap-8 mb-12">
        <div className="col-span-12 lg:col-span-8 primary-gradient rounded-xl p-8 flex flex-col md:flex-row items-center justify-between text-white overflow-hidden relative">
          <div className="relative z-10">
            <span className="text-indigo-200 font-label text-xs tracking-widest uppercase mb-2 block">
              Score Global
            </span>
            <div className="flex items-baseline space-x-2">
              <span className="text-7xl font-headline font-extrabold">{finalScore}</span>
              <span className="text-2xl text-indigo-300 font-medium">/ 700</span>
            </div>
            <div className="mt-6 flex items-center bg-white/10 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 w-fit">
              <span className="material-symbols-outlined text-secondary-fixed mr-2 text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>
                verified
              </span>
              <span className="font-bold text-sm">{scoreStatus}</span>
            </div>
          </div>
          <div className="mt-8 md:mt-0 relative z-10">
            <ScoreRing score={finalScore} />
          </div>
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-indigo-400/10 rounded-full blur-3xl" />
          <div className="absolute -left-10 -bottom-10 w-48 h-48 bg-indigo-900/40 rounded-full blur-2xl" />
        </div>

        <div className="col-span-12 lg:col-span-4 bg-surface-container-low dark:bg-slate-800 rounded-xl p-8 flex flex-col justify-center">
          <h3 className="font-headline font-bold text-xl mb-4 text-on-surface dark:text-white">
            Points d'attention
          </h3>
          <div className="space-y-4 text-sm">
            {judgeA.recommendation && (
              <div className="flex items-start space-x-3">
                <span className="w-2 h-2 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                <span className="text-on-surface-variant leading-relaxed italic line-clamp-2">
                  {judgeA.recommendation}
                </span>
              </div>
            )}
            {judgeB.recommendation && (
              <div className="flex items-start space-x-3">
                <span className="w-2 h-2 rounded-full bg-secondary mt-1.5 flex-shrink-0" />
                <span className="text-on-surface-variant leading-relaxed italic line-clamp-2">
                  {judgeB.recommendation}
                </span>
              </div>
            )}
            {!judgeA.recommendation && !judgeB.recommendation && (
              <p className="text-on-surface-variant text-sm italic">Aucun point d'attention particulier.</p>
            )}
          </div>
        </div>
      </section>

      {/* Analysis grid */}
      <div className="grid grid-cols-12 gap-8 mb-12">
        {/* AI analysis column */}
        <section className="col-span-12 lg:col-span-8 space-y-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xl font-headline font-bold flex items-center text-on-surface dark:text-white">
              <span className="material-symbols-outlined mr-2 text-primary text-2xl">psychology</span>
              Analyse Linguistique IA
            </h3>
            {allCorrections.length > 0 && (
              <span className="text-sm text-slate-500">{allCorrections.length + originalsA.length + originalsB.length} corrections identifiées</span>
            )}
          </div>

          {/* Feedback cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {judgeA.justification && (
              <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-6 canvas-shadow border-l-4 border-primary">
                <div className="flex justify-between items-start mb-4">
                  <span className="bg-primary-fixed text-on-primary-fixed px-3 py-1 rounded-full text-xs font-bold">Tâche A</span>
                  <span className="text-xs text-slate-400">Analyse</span>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-5">
                  {judgeA.justification}
                </p>
              </div>
            )}
            {judgeB.justification && (
              <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-6 canvas-shadow border-l-4 border-secondary">
                <div className="flex justify-between items-start mb-4">
                  <span className="bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full text-xs font-bold">Tâche B</span>
                  <span className="text-xs text-slate-400">Analyse</span>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-5">
                  {judgeB.justification}
                </p>
              </div>
            )}
            {allCorrections.slice(0, 2).map((c, i) => (
              <div key={i} className={`bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-6 canvas-shadow border-l-4 ${c.color === 'primary' ? 'border-primary' : 'border-secondary'}`}>
                <div className="flex justify-between items-start mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${c.color === 'primary' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-secondary-container text-on-secondary-container'}`}>
                    {c.type}
                  </span>
                  <span className="text-xs text-slate-400">Correction</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-error line-through">{c.original}</span>
                  <span className="material-symbols-outlined text-xs text-on-surface-variant">arrow_forward</span>
                  <span className="text-secondary font-semibold">{c.correction}</span>
                </div>
              </div>
            ))}
          </div>

          {/* All corrections expanded */}
          {(originalsA.length > 2 || originalsB.length > 2) && (
            <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-6 canvas-shadow">
              <h4 className="font-bold text-sm text-on-surface dark:text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-tertiary-fixed-dim">format_list_bulleted</span>
                Toutes les corrections
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {originalsA.length > 0 && (
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-primary mb-2">Tâche A</p>
                    <div className="space-y-1.5">
                      {originalsA.map((o, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs">
                          <span className="text-error line-through flex-shrink-0">{o}</span>
                          <span className="material-symbols-outlined text-xs text-on-surface-variant">arrow_forward</span>
                          <span className="text-secondary font-semibold">{correctionsA[i] ?? ''}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {originalsB.length > 0 && (
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-secondary mb-2">Tâche B</p>
                    <div className="space-y-1.5">
                      {originalsB.map((o, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs">
                          <span className="text-error line-through flex-shrink-0">{o}</span>
                          <span className="material-symbols-outlined text-xs text-on-surface-variant">arrow_forward</span>
                          <span className="text-secondary font-semibold">{correctionsB[i] ?? ''}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        {/* Recommendations column */}
        <section className="col-span-12 lg:col-span-4 bg-surface-container dark:bg-slate-800/60 rounded-xl p-8">
          <h3 className="text-xl font-headline font-bold mb-6 flex items-center text-on-surface dark:text-white">
            <span className="material-symbols-outlined mr-2 text-secondary text-2xl">trending_up</span>
            Recommandations
          </h3>
          <div className="space-y-6">
            {[
              { num: '1', title: 'Tâche A', text: judgeA.recommendation },
              { num: '2', title: 'Tâche B', text: judgeB.recommendation },
            ]
              .filter((r) => r.text)
              .map((r) => (
                <div key={r.num} className="flex space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white dark:bg-slate-700 flex items-center justify-center font-bold text-primary dark:text-indigo-300 shadow-sm text-sm">
                    {r.num}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-on-surface dark:text-white">{r.title}</p>
                    <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">{r.text}</p>
                  </div>
                </div>
              ))}
          </div>

          <div className="mt-10 p-6 bg-primary-container rounded-xl text-white relative overflow-hidden">
            <p className="text-sm font-bold relative z-10">Conseil TEF</p>
            <p className="text-xs mt-2 text-indigo-100 relative z-10 leading-relaxed italic">
              Variez vos connecteurs logiques : "Cependant", "En revanche", "Par ailleurs",
              "Néanmoins" pour enrichir votre registre.
            </p>
            <span
              className="material-symbols-outlined absolute -bottom-2 -right-2 text-white/10 text-6xl"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              lightbulb
            </span>
          </div>
        </section>
      </div>

      {/* Refined draft */}
      <section className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl p-8 canvas-shadow mb-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-2xl font-headline font-bold text-on-surface dark:text-white">
              Version améliorée par l'IA
            </h3>
            <p className="text-sm text-on-surface-variant">Comparez votre texte original avec la version optimisée.</p>
          </div>
          <div className="flex bg-surface-container-low dark:bg-slate-700 p-1 rounded-lg">
            <button
              className={`px-5 py-2 rounded-md text-sm font-bold transition-colors ${draftView === 'A' ? 'bg-white dark:bg-slate-600 shadow-sm text-primary dark:text-indigo-300' : 'text-on-surface-variant hover:text-primary'}`}
              onClick={() => setDraftView('A')}
            >
              Tâche A
            </button>
            <button
              className={`px-5 py-2 rounded-md text-sm font-bold transition-colors ${draftView === 'B' ? 'bg-white dark:bg-slate-600 shadow-sm text-primary dark:text-indigo-300' : 'text-on-surface-variant hover:text-primary'}`}
              onClick={() => setDraftView('B')}
            >
              Tâche B
            </button>
          </div>
        </div>

        {!improvedLoaded ? (
          <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
            <span className="material-symbols-outlined text-5xl text-outline-variant">auto_awesome</span>
            <p className="text-on-surface-variant text-sm">
              Générez la version améliorée pour comparer votre texte avec une rédaction optimisée.
            </p>
            {improvedError && <p className="text-error text-sm">{improvedError}</p>}
            <button
              onClick={handleGenerateImproved}
              disabled={loadingImproved}
              className="flex items-center gap-2 px-8 py-3 primary-gradient text-white rounded-lg font-bold text-sm shadow-lg hover:shadow-indigo-900/20 transition-all disabled:opacity-50"
            >
              {loadingImproved ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Génération en cours...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
                  Générer la version améliorée
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-px bg-outline-variant/20 rounded-xl overflow-hidden">
            <div className="bg-white dark:bg-slate-900 p-8">
              <div className="flex items-center justify-between mb-6">
                <span className="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Votre texte original</span>
                <span className="text-xs text-slate-400">
                  {countWords(draftView === 'A' ? responseA : responseB)} mots
                </span>
              </div>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-sm whitespace-pre-wrap">
                {draftView === 'A' ? responseA : responseB}
              </p>
            </div>
            <div className="bg-indigo-50/30 dark:bg-indigo-900/10 p-8 border-l-0 lg:border-l border-outline-variant/20">
              <div className="flex items-center justify-between mb-6">
                <span className="text-xs font-bold text-primary dark:text-indigo-300 uppercase tracking-widest">Version IA optimisée</span>
                <span className="text-xs text-indigo-400">
                  {countWords(draftView === 'A' ? improvedA : improvedB)} mots
                </span>
              </div>
              <p className="text-indigo-950 dark:text-indigo-100 leading-relaxed text-sm whitespace-pre-wrap">
                {draftView === 'A' ? improvedA : improvedB}
              </p>
            </div>
          </div>
        )}

        <div className="mt-8 flex justify-end space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 text-sm font-bold text-primary hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors rounded-lg flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-base">dashboard</span>
            Tableau de bord
          </button>
          <button
            onClick={() => navigate('/practice')}
            className="px-8 py-3 primary-gradient text-white text-sm font-bold rounded-lg shadow-lg hover:shadow-indigo-900/20 transition-all flex items-center gap-2"
          >
            Nouvelle session
            <span className="material-symbols-outlined text-base">arrow_forward</span>
          </button>
        </div>
      </section>

      {/* Floating progress indicator */}
      <div className="fixed bottom-8 right-12 z-50 flex items-center space-x-6 glass-effect p-4 rounded-2xl shadow-2xl border border-white/40">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold text-sm">
            {progressPct}%
          </div>
          <div>
            <p className="text-xs font-bold text-primary">Progression TEF</p>
            <div className="w-32 h-1.5 bg-slate-200 rounded-full mt-1 overflow-hidden">
              <div className="h-full bg-secondary rounded-full" style={{ width: `${progressPct}%` }} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function countWords(text) {
  return (text?.trim().match(/\b\w+\b/g) || []).length;
}
