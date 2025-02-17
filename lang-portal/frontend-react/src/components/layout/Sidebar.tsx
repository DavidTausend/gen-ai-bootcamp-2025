
import { Link, useLocation } from 'react-router-dom';
import { Book, BookOpen, LayoutDashboard, List, Settings, Timer } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  const links = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/study-activities', icon: BookOpen, label: 'Study Activities' },
    { path: '/words', icon: Book, label: 'Words' },
    { path: '/groups', icon: List, label: 'Word Groups' },
    { path: '/sessions', icon: Timer, label: 'Sessions' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="w-64 min-h-screen bg-white border-r border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-semibold">LangPortal</h1>
      </div>
      <div className="p-2">
        {links.map(({ path, icon: Icon, label }) => (
          <Link
            key={path}
            to={path}
            className={`flex items-center px-4 py-3 mb-1 rounded-lg transition-colors ${
              isActive(path)
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Icon className="w-5 h-5 mr-3" />
            <span>{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default Sidebar;
