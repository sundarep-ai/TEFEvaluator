import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function LoginPage() {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const clearFields = () => {
    setUsername('');
    setPassword('');
    setPassword2('');
    setError('');
    setSuccessMsg('');
  };

  const switchMode = (newMode) => {
    clearFields();
    setMode(newMode);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError("Le nom d'utilisateur et le mot de passe sont requis.");
      return;
    }
    setError('');
    setLoading(true);
    try {
      await login(username.trim(), password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Connexion échouée. Vérifiez vos identifiants.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError("Le nom d'utilisateur et le mot de passe sont requis.");
      return;
    }
    if (password !== password2) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await register(username.trim(), password);
      setSuccessMsg('Compte créé avec succès ! Connectez-vous maintenant.');
      switchMode('login');
    } catch (err) {
      setError(err.message || "Échec de la création du compte.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-6 overflow-hidden bg-surface font-body text-on-surface antialiased">
      {/* Background decorations */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-primary-fixed/30 via-transparent to-transparent" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[60%] bg-secondary/5 rounded-full blur-[120px]" />
      </div>

      {/* Card */}
      <main className="relative z-10 w-full max-w-[1100px] grid grid-cols-1 md:grid-cols-2 bg-surface-container-lowest rounded-xl overflow-hidden canvas-shadow">
        {/* Left panel */}
        <div className="hidden md:flex flex-col justify-between p-12 bg-surface-container-low border-r border-outline-variant/10 relative overflow-hidden">
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-12">
              <div className="w-10 h-10 primary-gradient rounded-lg flex items-center justify-center">
                <span className="material-symbols-outlined text-white" style={{ fontVariationSettings: "'FILL' 1" }}>
                  auto_stories
                </span>
              </div>
              <span className="font-headline font-extrabold text-2xl tracking-tight text-primary">L'Atelier</span>
            </div>
            <h1 className="font-headline text-4xl font-extrabold text-primary leading-tight mb-6">
              Maîtrisez la langue, <br />réussissez le TEF.
            </h1>
            <p className="text-on-surface-variant text-lg max-w-md leading-relaxed">
              Accédez à une préparation éditoriale de haut niveau conçue pour les candidats exigeants.
              Pratiquez avec des outils de précision académique.
            </p>
          </div>

          <div className="relative z-10 space-y-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full primary-gradient flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                JP
              </div>
              <div>
                <p className="text-sm font-semibold italic text-primary">
                  "Le meilleur compagnon pour mon examen."
                </p>
                <p className="text-xs text-on-surface-variant">Jean-Pierre L., Candidat TEF 2024</p>
              </div>
            </div>
          </div>

          <div className="absolute -bottom-24 -right-24 w-64 h-64 primary-gradient rounded-full opacity-5 blur-3xl" />
        </div>

        {/* Right panel */}
        <div className="p-8 md:p-16 flex flex-col justify-center">
          <div className="max-w-sm mx-auto w-full">
            {/* Mobile logo */}
            <div className="md:hidden flex items-center gap-2 mb-8">
              <span className="font-headline font-extrabold text-xl tracking-tight text-primary">L'Atelier</span>
            </div>

            {mode === 'login' ? (
              <>
                <header className="mb-8">
                  <h2 className="font-headline text-2xl font-bold text-on-surface mb-2">Bon retour parmi nous</h2>
                  <p className="text-on-surface-variant text-sm">
                    Entrez vos coordonnées pour accéder à votre espace de travail.
                  </p>
                </header>

                <form className="space-y-5" onSubmit={handleLogin}>
                  {successMsg && (
                    <div className="bg-secondary-container text-on-secondary-container text-sm px-4 py-3 rounded-lg">
                      {successMsg}
                    </div>
                  )}
                  {error && (
                    <div className="bg-error-container text-on-error-container text-sm px-4 py-3 rounded-lg">
                      {error}
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant ml-1">
                      Nom d'utilisateur
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 bg-surface-container-low border-transparent rounded-lg focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-200 text-sm outline-none placeholder:text-outline/50"
                        placeholder="nom_utilisateur"
                        type="text"
                        autoComplete="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                      />
                      <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-outline/40 text-lg">
                        person
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant ml-1">
                      Mot de passe
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 bg-surface-container-low border-transparent rounded-lg focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-200 text-sm outline-none placeholder:text-outline/50"
                        placeholder="••••••••"
                        type="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                      <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-outline/40 text-lg">
                        lock
                      </span>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full primary-gradient text-white font-semibold py-3.5 rounded-lg shadow-lg shadow-primary/10 hover:shadow-primary/20 active:scale-[0.98] transition-all duration-150 text-sm mt-4 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Connexion en cours...' : "S'identifier"}
                  </button>
                </form>

                <footer className="mt-10 text-center">
                  <p className="text-sm text-on-surface-variant">
                    Nouveau ici ?{' '}
                    <button
                      onClick={() => switchMode('register')}
                      className="text-primary font-bold hover:underline ml-1"
                    >
                      Créer un compte
                    </button>
                  </p>
                </footer>
              </>
            ) : (
              <>
                <header className="mb-8">
                  <h2 className="font-headline text-2xl font-bold text-on-surface mb-2">Créer un compte</h2>
                  <p className="text-on-surface-variant text-sm">
                    Rejoignez L'Atelier et commencez votre préparation au TEF.
                  </p>
                </header>

                <form className="space-y-5" onSubmit={handleRegister}>
                  {error && (
                    <div className="bg-error-container text-on-error-container text-sm px-4 py-3 rounded-lg">
                      {error}
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant ml-1">
                      Nom d'utilisateur
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 bg-surface-container-low border-transparent rounded-lg focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-200 text-sm outline-none placeholder:text-outline/50"
                        placeholder="choisir_un_nom"
                        type="text"
                        autoComplete="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                      />
                      <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-outline/40 text-lg">
                        person
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant ml-1">
                      Mot de passe
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 bg-surface-container-low border-transparent rounded-lg focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-200 text-sm outline-none placeholder:text-outline/50"
                        placeholder="••••••••"
                        type="password"
                        autoComplete="new-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                      <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-outline/40 text-lg">
                        lock
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant ml-1">
                      Confirmer le mot de passe
                    </label>
                    <div className="relative">
                      <input
                        className="w-full px-4 py-3 bg-surface-container-low border-transparent rounded-lg focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-200 text-sm outline-none placeholder:text-outline/50"
                        placeholder="••••••••"
                        type="password"
                        autoComplete="new-password"
                        value={password2}
                        onChange={(e) => setPassword2(e.target.value)}
                      />
                      <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-outline/40 text-lg">
                        shield
                      </span>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full primary-gradient text-white font-semibold py-3.5 rounded-lg shadow-lg shadow-primary/10 hover:shadow-primary/20 active:scale-[0.98] transition-all duration-150 text-sm mt-4 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Création en cours...' : 'Créer mon compte'}
                  </button>
                </form>

                <footer className="mt-10 text-center">
                  <p className="text-sm text-on-surface-variant">
                    Déjà inscrit ?{' '}
                    <button
                      onClick={() => switchMode('login')}
                      className="text-primary font-bold hover:underline ml-1"
                    >
                      Se connecter
                    </button>
                  </p>
                </footer>
              </>
            )}
          </div>
        </div>
      </main>

      {/* Footer nav */}
      <div className="fixed bottom-8 text-center w-full left-0 z-10">
        <nav className="inline-flex items-center gap-6 px-6 py-2 bg-surface-container-highest/20 backdrop-blur-md rounded-full text-[11px] uppercase tracking-widest font-semibold text-on-surface-variant/60">
          <span className="hover:text-primary transition-colors cursor-default">Confidentialité</span>
          <span className="hover:text-primary transition-colors cursor-default">Conditions</span>
          <span className="hover:text-primary transition-colors cursor-default">Aide</span>
        </nav>
      </div>
    </div>
  );
}
