import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

const navItems = [
  { icon: 'dashboard', label: 'Tableau de bord', to: '/dashboard' },
  { icon: 'school', label: 'Pratique', to: '/practice' },
  { icon: 'history', label: 'Historique', to: '/dashboard' },
  { icon: 'settings', label: 'Paramètres', to: '/settings' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const initials = user?.username?.slice(0, 2)?.toUpperCase() ?? '??';

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col py-8 bg-slate-50 dark:bg-slate-900 z-50 border-r border-slate-100 dark:border-slate-800">
      {/* Logo */}
      <div className="px-8 mb-12">
        <h1 className="text-2xl font-bold text-indigo-950 dark:text-indigo-100 tracking-wider font-headline">
          L'Atelier
        </h1>
        <p className="text-xs font-headline font-bold tracking-tight text-indigo-900 dark:text-indigo-300 opacity-60">
          TEF Preparation
        </p>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1">
        {navItems.map(({ icon, label, to }) => {
          const isActive =
            to === '/practice'
              ? location.pathname.startsWith('/practice')
              : location.pathname === to && to !== '/dashboard'
              ? true
              : to === '/dashboard' && !location.pathname.startsWith('/practice') && location.pathname !== '/settings';

          return (
            <NavLink
              key={`${to}-${label}`}
              to={to}
              className={
                isActive
                  ? 'flex items-center px-8 py-4 text-indigo-900 dark:text-indigo-200 border-r-4 border-indigo-900 dark:border-indigo-400 font-bold bg-indigo-50/50 dark:bg-indigo-900/20 transition-colors duration-150'
                  : 'flex items-center px-8 py-4 text-slate-500 dark:text-slate-400 font-medium hover:bg-slate-200/50 dark:hover:bg-slate-800 transition-colors duration-150'
              }
            >
              <span className="material-symbols-outlined mr-4 text-xl">{icon}</span>
              <span className="font-headline font-bold tracking-tight">{label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User card */}
      <div className="px-8 mt-auto">
        <div className="p-4 rounded-xl bg-slate-100 dark:bg-slate-800/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full primary-gradient flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-indigo-950 dark:text-indigo-100 truncate">
                {user?.username}
              </p>
              <button
                onClick={logout}
                className="text-[10px] text-slate-500 hover:text-error transition-colors"
              >
                Se déconnecter
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
