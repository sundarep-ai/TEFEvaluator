import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import TopNav from './TopNav.jsx';

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-background dark:bg-slate-950 text-on-surface dark:text-slate-100">
      <Sidebar />
      <TopNav />
      <main className="ml-64 mt-20 p-12 max-w-[1600px]">
        <Outlet />
      </main>
    </div>
  );
}
