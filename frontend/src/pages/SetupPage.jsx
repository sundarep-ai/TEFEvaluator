import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getQuestions } from '../api/index.js';

// Newest low-cost tier per provider, verified August 2026. The previous
// defaults (gemini-2.5-pro / gpt-4o / openai/gpt-4o) are retired or retiring and
// return 404s. Keep in sync with DEFAULT_MODELS in backend/ai_client.py.
const PROVIDERS = [
  { value: 'google',     label: 'Google Gemini', defaultModel: 'gemini-3.6-flash' },
  { value: 'openai',     label: 'OpenAI',        defaultModel: 'gpt-5.6-luna' },
  { value: 'anthropic',  label: 'Anthropic',     defaultModel: 'claude-haiku-4-5' },
  { value: 'openrouter', label: 'OpenRouter',    defaultModel: 'openai/gpt-5.6-luna' },
];

const DEFAULT_PROVIDER = 'google';
const DEFAULT_MODEL = PROVIDERS[0].defaultModel;

function QuestionPicker({ questions, selectedId, onSelect }) {
  return (
    <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
      {questions.map((q) => {
        const selected = q.id === selectedId;
        return (
          <button
            key={q.id}
            type="button"
            onClick={() => onSelect(q)}
            className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
              selected
                ? 'border-primary bg-primary/10 dark:bg-indigo-900/30'
                : 'border-outline-variant/20 bg-surface-container-low dark:bg-slate-700 hover:border-primary/40'
            }`}
          >
            <p className="text-sm font-semibold text-on-surface dark:text-white">{q.title}</p>
            <p className="text-xs text-on-surface-variant mt-0.5 line-clamp-2">{q.preview}</p>
          </button>
        );
      })}
    </div>
  );
}

function ModeToggle({ mode, onChange }) {
  return (
    <div className="inline-flex rounded-lg bg-surface-container-low dark:bg-slate-700 p-1 text-xs font-medium">
      <button
        type="button"
        onClick={() => onChange('library')}
        className={`px-3 py-1.5 rounded-md transition-colors ${
          mode === 'library'
            ? 'bg-surface-container-lowest dark:bg-slate-800 text-primary shadow-sm'
            : 'text-on-surface-variant hover:text-on-surface dark:hover:text-white'
        }`}
      >
        Sujets proposés
      </button>
      <button
        type="button"
        onClick={() => onChange('custom')}
        className={`px-3 py-1.5 rounded-md transition-colors ${
          mode === 'custom'
            ? 'bg-surface-container-lowest dark:bg-slate-800 text-primary shadow-sm'
            : 'text-on-surface-variant hover:text-on-surface dark:hover:text-white'
        }`}
      >
        Coller mon sujet
      </button>
    </div>
  );
}

export default function SetupPage() {
  const navigate = useNavigate();

  const [questionsA, setQuestionsA] = useState([]);
  const [questionsB, setQuestionsB] = useState([]);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [questionsError, setQuestionsError] = useState('');

  const [selectedA, setSelectedA] = useState(null);
  const [selectedB, setSelectedB] = useState(null);

  // 'library' picks a static question by id; 'custom' lets the user paste their own.
  const [modeA, setModeA] = useState('library');
  const [modeB, setModeB] = useState('library');
  const [customA, setCustomA] = useState('');
  const [customB, setCustomB] = useState('');

  // AI provider settings — persisted in localStorage
  const [aiOpen, setAiOpen] = useState(false);
  const [aiProvider, setAiProvider] = useState(
    () => localStorage.getItem('ai_provider') || DEFAULT_PROVIDER
  );
  const [aiKey, setAiKey] = useState(
    () => localStorage.getItem('ai_api_key') || ''
  );
  // Migrate anyone whose localStorage still holds a retired model id, otherwise
  // they keep hitting 404s with no obvious cause.
  const [aiModel, setAiModel] = useState(() => {
    const stored = localStorage.getItem('ai_model');
    const retired = ['gemini-2.5-pro', 'gpt-4o', 'openai/gpt-4o', 'claude-opus-4-6'];
    if (!stored || retired.includes(stored)) {
      const provider = localStorage.getItem('ai_provider') || DEFAULT_PROVIDER;
      const fresh = PROVIDERS.find((p) => p.value === provider)?.defaultModel || DEFAULT_MODEL;
      localStorage.setItem('ai_model', fresh);
      return fresh;
    }
    return stored;
  });

  useEffect(() => {
    let cancelled = false;
    getQuestions()
      .then(({ taskA, taskB }) => {
        if (cancelled) return;
        setQuestionsA(taskA || []);
        setQuestionsB(taskB || []);
      })
      .catch((err) => {
        if (!cancelled) setQuestionsError(err?.message || 'Impossible de charger les questions.');
      })
      .finally(() => {
        if (!cancelled) setLoadingQuestions(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

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

  const taskAQuestion = modeA === 'custom' ? customA.trim() : selectedA?.prompt;
  const taskBQuestion = modeB === 'custom' ? customB.trim() : selectedB?.prompt;
  const canBegin = Boolean(taskAQuestion && taskBQuestion);

  const handleBegin = () => {
    if (!canBegin) return;
    navigate('/practice/write', {
      state: { taskAQuestion, taskBQuestion },
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
          Choisissez un sujet réel pour chacune des deux tâches d'expression écrite.
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

      {questionsError && (
        <p className="text-sm text-error mb-6">{questionsError}</p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {/* Task A */}
        <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
          <div className="px-8 py-6 border-b border-outline-variant/20 flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-primary-fixed flex items-center justify-center text-primary">
              <span className="material-symbols-outlined">article</span>
            </div>
            <div>
              <h3 className="font-headline font-bold text-on-surface dark:text-white">
                Section A — Fait divers
              </h3>
              <p className="text-xs text-on-surface-variant">80 mots minimum · 25 min</p>
            </div>
          </div>

          <div className="p-8 space-y-4">
            <ModeToggle mode={modeA} onChange={setModeA} />

            {modeA === 'library' ? (
              <>
                {loadingQuestions ? (
                  <p className="text-sm text-on-surface-variant">Chargement des sujets…</p>
                ) : (
                  <QuestionPicker questions={questionsA} selectedId={selectedA?.id} onSelect={setSelectedA} />
                )}

                {selectedA && (
                  <div className="px-4 py-3 bg-surface-container-low dark:bg-slate-700 rounded-lg text-sm leading-relaxed text-on-surface dark:text-white whitespace-pre-line max-h-48 overflow-y-auto">
                    {selectedA.prompt}
                  </div>
                )}
              </>
            ) : (
              <textarea
                value={customA}
                onChange={(e) => setCustomA(e.target.value)}
                rows={8}
                placeholder="Collez ici l'article ou la mise en situation de la Section A (Type de document / Objectif / Consignes)..."
                className="w-full px-4 py-3 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg resize-none text-sm leading-relaxed outline-none focus:ring-2 focus:ring-primary/20 placeholder:text-outline/50"
              />
            )}
          </div>
        </div>

        {/* Task B */}
        <div className="bg-surface-container-lowest dark:bg-slate-800 rounded-xl overflow-hidden canvas-shadow">
          <div className="px-8 py-6 border-b border-outline-variant/20 flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center text-secondary">
              <span className="material-symbols-outlined">mail</span>
            </div>
            <div>
              <h3 className="font-headline font-bold text-on-surface dark:text-white">
                Section B — Point de vue
              </h3>
              <p className="text-xs text-on-surface-variant">200 mots minimum · 35 min</p>
            </div>
          </div>

          <div className="p-8 space-y-4">
            <ModeToggle mode={modeB} onChange={setModeB} />

            {modeB === 'library' ? (
              <>
                {loadingQuestions ? (
                  <p className="text-sm text-on-surface-variant">Chargement des sujets…</p>
                ) : (
                  <QuestionPicker questions={questionsB} selectedId={selectedB?.id} onSelect={setSelectedB} />
                )}

                {selectedB && (
                  <div className="px-4 py-3 bg-surface-container-low dark:bg-slate-700 rounded-lg text-sm leading-relaxed text-on-surface dark:text-white whitespace-pre-line max-h-48 overflow-y-auto">
                    {selectedB.prompt}
                  </div>
                )}
              </>
            ) : (
              <textarea
                value={customB}
                onChange={(e) => setCustomB(e.target.value)}
                rows={8}
                placeholder="Collez ici la mise en situation de la Section B (Type de document / Objectif / Consignes)..."
                className="w-full px-4 py-3 bg-surface-container-low dark:bg-slate-700 text-on-surface dark:text-white rounded-lg resize-none text-sm leading-relaxed outline-none focus:ring-2 focus:ring-primary/20 placeholder:text-outline/50"
              />
            )}
          </div>
        </div>
      </div>

      {/* Info banner */}
      <div className="bg-primary-fixed/30 dark:bg-indigo-900/20 rounded-xl p-5 mb-8 flex items-start gap-3">
        <span className="material-symbols-outlined text-primary text-xl flex-shrink-0 mt-0.5">info</span>
        <div className="text-sm">
          <p className="font-semibold text-primary mb-1">Avant de commencer</p>
          <ul className="text-on-surface-variant space-y-1 list-disc list-inside">
            <li>Vous aurez <strong>60 minutes</strong> au total (Section A : 25 min, Section B : 35 min).</li>
            <li>Section A : minimum <strong>80 mots</strong> (80–120 recommandé) — ne recopiez pas le début de l'article.</li>
            <li>Section B : minimum <strong>200 mots</strong> (200–300 recommandé) — la forme lettre n'est <strong>pas</strong> obligatoire.</li>
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
