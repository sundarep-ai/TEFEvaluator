import { useAuth } from '../../context/AuthContext.jsx';
import { useTheme } from '../../context/ThemeContext.jsx';

export default function TopNav() {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const initials = user?.username?.slice(0, 2)?.toUpperCase() ?? '??';

  return (
    <header className="fixed top-0 right-0 left-64 h-20 flex justify-between items-center px-12 z-40 bg-white/70 dark:bg-slate-950/70 backdrop-blur-xl shadow-[0_12px_32px_-4px_rgba(0,6,102,0.06)]">
      {/* Search bar */}
      <div className="flex items-center bg-slate-50 dark:bg-slate-900 rounded-full px-4 py-2 w-80">
        <span className="material-symbols-outlined text-slate-400 mr-2 text-xl">search</span>
        <input
          className="bg-transparent border-none focus:outline-none text-sm w-full font-body text-slate-600 dark:text-slate-300 placeholder:text-slate-400"
          placeholder="Rechercher une session..."
          type="text"
          readOnly
        />
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-4">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="text-slate-600 dark:text-slate-400 hover:text-indigo-700 dark:hover:text-indigo-200 transition-all"
          title={theme === 'dark' ? 'Mode clair' : 'Mode sombre'}
        >
          <span className="material-symbols-outlined text-xl">
            {theme === 'dark' ? 'light_mode' : 'dark_mode'}
          </span>
        </button>

        <div className="h-8 w-px bg-outline-variant/20" />

        {/* Profile */}
        <div className="flex items-center space-x-3">
          <span className="text-indigo-900 dark:text-indigo-200 font-bold text-sm font-body">
            {user?.username}
          </span>
          <div className="w-8 h-8 rounded-full primary-gradient flex items-center justify-center text-white text-xs font-bold">
            {initials}
          </div>
        </div>
      </div>
    </header>
  );
}
