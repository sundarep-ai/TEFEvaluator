import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateQuestion } from '../api/index.js';

const PROVIDERS = [
  { value: 'google',     label: 'Google Gemini',  defaultModel: 'gemini-2.5-pro' },
  { value: 'openai',     label: 'OpenAI',          defaultModel: 'gpt-4o' },
  { value: 'anthropic',  label: 'Anthropic',       defaultModel: 'claude-opus-4-6' },
  { value: 'openrouter', label: 'OpenRouter',      defaultModel: 'openai/gpt-4o' },
];

export default function SetupPage() {
  const navigate = useNavigate();
  const [taskAQuestion, setTaskAQuestion] = useState('');
  const [taskBQuestion, setTaskBQuestion] = useState('');
  const [loadingA, setLoadingA] = useState(false);
  const [loadingB, setLoadingB] = useState(false);
  const [errorA, setErrorA] = useState('');
  const [errorB, setErrorB] = useState('');

  // AI provider settings — persisted in localStorage
  const [aiOpen, setAiOpen] = useState(false);
  const [aiProvider, setAiProvider] = useState(
    () => localStorage.getItem('ai_provider') || 'google'
  );
  const [aiKey, setAiKey] = useState(
    () => localStorage.getItem('ai_api_key') || ''
  );
  const [aiModel, setAiModel] = useState(
    () => localStorage.getItem('ai_model') || 'gemini-2.5-pro'
  );

  const handleProviderChange = (value) => {
    const defaultModel = PROVIDERS.find((p) => p.value === value)?.defaultModel || '';
    setAiProvider(value);
    setAiModel(defaultModel);
    localStorage.setItem('ai_provider', value);
    localStorage.setItem('ai_model', defaultModel);
  };

  const handleKeyChange = (value) => {
    setAiKey(value);
    localStorage.setItem('ai_api_key', value);
  };

  const handleModelChange = (value) => {
    setAiModel(value);
    localStorage.setItem('ai_model', value);
  };

  const canBegin = taskAQuestion.trim().length > 0 && taskBQuestion.trim().length > 0;

  const handleGenerateA = async () => {
    setLoadingA(true);
    setErrorA('');
    try {
      const { question } = await generateQuestion('A');
      setTaskAQuestion(question);
    } catch (err) {
      setErrorA('Erreur lors de la génération. Réessayez.');
    } finally {
      setLoadingA(false);
    }
  };

  const handleGenerateB = async () => {
    setLoadingB(true);
    setErrorB('');
    try {
      const { question } = await generateQuestion('B');
      setTaskBQuestion(question);
    } catch (err) {
      setErrorB('Erreur lors de la génération. Réessayez.');
    } finally {
      setLoadingB(false);
    }
  };

  const handleBegin = () => {
    if (!canBegin) return;
    navigate('/practice/write', {
      state: { taskAQuestion: taskAQuestion.trim(), taskBQuestion: taskBQuestion.trim() },
    });
  };

  return (
    <>
      {/* Header */}
      <section className="mb-10">
        <h2 className="text-4xl font-headline font-extrabold text-primary dark:text-indigo-300 tracking-tight mb-2">
          Configurer votre session
        </h2>
        <p className="text-on-surface-variant max-w-2xl leading-relaxed">
          Générez des questions avec l'IA ou saisissez les vôtres pour les deux tâches d'expression écrite.
        </p>
      </section>

      {/* AI Provider Settings */}
      <div className="mb-8 bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
        <button
          onClick={() => setAiOpen((v) => !v)}
          className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-surface-container-low dark:hover:bg-slate-700 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary text-lg">key</span>
            <span className="font-semibold text-on-surface dark:text-white text-sm">
              Configuration du fournisseur IA
            </span>
            {aiKey && (
              <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
                {PROVIDERS.find((p) => p.value === aiProvider)?.label ?? aiProvider}
              </span>
            )}
          </div>
          <span className={`material-symbols-outlined text-on-surface-variant transition-transform ${aiOpen ? 'rotate-180' : ''}`}>
            expand_more
          </span>
        </button>

        {aiOpen && (
          <div className="px-6 pb-6 pt-2 grid grid-cols-1 sm:grid-cols-3 gap-4 border-t border-outline-variant/20">
            {/* Provider */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-on-surface-variant">Fournisseur</label>
              <select
                value={aiProvider}
                onChange={(e) => handleProviderChange(e.target.value)}
                className="px-3 py-2 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary/20"
              >
                {PROVIDERS.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>

            {/* API Key */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-on-surface-variant">Clé API</label>
              <input
                type="password"
                placeholder="sk-... / AIza... / sk-ant-..."
                value={aiKey}
                onChange={(e) => handleKeyChange(e.target.value)}
                className="px-3 py-2 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary/20 placeholder:text-outline/50"
              />
            </div>

            {/* Model */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-on-surface-variant">Modèle</label>
              <input
                type="text"
                value={aiModel}
                onChange={(e) => handleModelChange(e.target.value)}
                className="px-3 py-2 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>

            <p className="sm:col-span-3 text-xs text-on-surface-variant">
              La clé API est stockée uniquement dans votre navigateur (localStorage) et n'est jamais enregistrée sur le serveur.
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {/* Task A */}
        <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
          <div className="px-8 py-6 border-b border-outline-variant/20 flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-primary-fixed flex items-center justify-center text-primary">
              <span className="material-symbols-outlined">article</span>
            </div>
            <div>
              <h3 className="font-headline font-bold text-on-surface dark:text-white">Tâche A — Récit</h3>
              <p className="text-xs text-on-surface-variant">Environ 80–120 mots</p>
            </div>
          </div>

          <div className="p-8 space-y-4">
            <div className="flex items-center gap-3">
              <button
                onClick={handleGenerateA}
                disabled={loadingA}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-primary/20 rounded-lg text-primary font-semibold text-sm hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingA ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <span>Génération...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-lg">auto_awesome</span>
                    <span>Générer avec l'IA</span>
                  </>
                )}
              </button>
              <button
                onClick={() => { setTaskAQuestion(''); setErrorA(''); }}
                disabled={loadingA}
                className="w-10 h-10 flex items-center justify-center rounded-lg bg-surface-container-low dark:bg-slate-700 text-on-surface-variant hover:text-error hover:bg-error-container transition-colors disabled:opacity-50"
                title="Effacer"
              >
                <span className="material-symbols-outlined text-lg">delete</span>
              </button>
            </div>

            {errorA && (
              <p className="text-xs text-error">{errorA}</p>
            )}

            <textarea
              className="w-full px-4 py-3 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg resize-none text-sm leading-relaxed outline-none focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline/50 min-h-[160px]"
              placeholder="Générez une question ou saisissez votre propre sujet de Tâche A ici..."
              value={taskAQuestion}
              onChange={(e) => setTaskAQuestion(e.target.value)}
            />
          </div>
        </div>

        {/* Task B */}
        <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
          <div className="px-8 py-6 border-b border-outline-variant/20 flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center text-secondary">
              <span className="material-symbols-outlined">mail</span>
            </div>
            <div>
              <h3 className="font-headline font-bold text-on-surface dark:text-white">Tâche B — Lettre formelle</h3>
              <p className="text-xs text-on-surface-variant">Environ 200–250 mots</p>
            </div>
          </div>

          <div className="p-8 space-y-4">
            <div className="flex items-center gap-3">
              <button
                onClick={handleGenerateB}
                disabled={loadingB}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-primary/20 rounded-lg text-primary font-semibold text-sm hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingB ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <span>Génération...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-lg">auto_awesome</span>
                    <span>Générer avec l'IA</span>
                  </>
                )}
              </button>
              <button
                onClick={() => { setTaskBQuestion(''); setErrorB(''); }}
                disabled={loadingB}
                className="w-10 h-10 flex items-center justify-center rounded-lg bg-surface-container-low dark:bg-slate-700 text-on-surface-variant hover:text-error hover:bg-error-container transition-colors disabled:opacity-50"
                title="Effacer"
              >
                <span className="material-symbols-outlined text-lg">delete</span>
              </button>
            </div>

            {errorB && (
              <p className="text-xs text-error">{errorB}</p>
            )}

            <textarea
              className="w-full px-4 py-3 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg resize-none text-sm leading-relaxed outline-none focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline/50 min-h-[160px]"
              placeholder="Générez une question ou saisissez votre propre sujet de Tâche B ici..."
              value={taskBQuestion}
              onChange={(e) => setTaskBQuestion(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Info banner */}
      <div className="bg-primary-fixed/30 dark:bg-indigo-900/20 rounded-xl p-5 mb-8 flex items-start gap-3">
        <span className="material-symbols-outlined text-primary text-xl flex-shrink-0 mt-0.5">info</span>
        <div className="text-sm">
          <p className="font-semibold text-primary mb-1">Avant de commencer</p>
          <ul className="text-on-surface-variant space-y-1 list-disc list-inside">
            <li>Vous aurez <strong>60 minutes</strong> pour compléter les deux tâches.</li>
            <li>Tâche A : minimum <strong>80 mots</strong> — Tâche B : minimum <strong>200 mots</strong>.</li>
            <li>Évitez de quitter la page pendant la session d'écriture.</li>
          </ul>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 px-6 py-3 rounded-lg text-on-surface-variant hover:bg-surface-container-low dark:hover:bg-slate-700 transition-colors font-medium text-sm"
        >
          <span className="material-symbols-outlined text-lg">arrow_back</span>
          Retour
        </button>

        <button
          onClick={handleBegin}
          disabled={!canBegin}
          className="flex items-center gap-2 px-8 py-3.5 primary-gradient text-white rounded-lg font-bold text-sm shadow-lg shadow-primary/20 hover:shadow-primary/30 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
        >
          <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>play_circle</span>
          Commencer la session d'écriture
        </button>
      </div>
    </>
  );
}
