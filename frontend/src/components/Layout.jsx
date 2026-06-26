
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { 
  LayoutDashboard, 
  FileUp, 
  FileCode, 
  Sparkles, 
  LogOut, 
  User as UserIcon
} from "lucide-react";

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Resumes", path: "/resumes", icon: FileUp },
    { name: "Job Profiles", path: "/job-descriptions", icon: FileCode },
    { name: "ATS Scanner", path: "/ats-scanner", icon: Sparkles },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-[#080c14] text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 glass-card border-r border-slate-800/60 flex flex-col justify-between p-4">
        <div>
          {/* Logo */}
          <div className="flex items-center gap-2 px-2 py-4 mb-6">
            <Sparkles className="w-8 h-8 text-blue-500 animate-pulse" />
            <span className="text-xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
              ResumeATS
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1.5">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-250 ${
                    isActive
                      ? "bg-indigo-600/90 text-white shadow-md shadow-indigo-600/20"
                      : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Profile / Logout footer */}
        <div className="border-t border-slate-800/60 pt-4 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
              <UserIcon className="w-4 h-4 text-slate-400" />
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold text-slate-200 truncate">{user?.name}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-rose-400 hover:bg-rose-950/20 transition-all duration-200"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <header className="h-16 border-b border-slate-800/40 flex items-center justify-between px-8 bg-[#080c14]/40 backdrop-blur-md sticky top-0 z-10">
          <h1 className="text-lg font-semibold text-slate-200">
            {menuItems.find((item) => item.path === location.pathname)?.name || "Workspace"}
          </h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 bg-slate-900/80 border border-slate-800/60 px-3 py-1.5 rounded-full text-xs text-emerald-400">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
              Engine Online
            </div>
          </div>
        </header>

        <div className="p-8 max-w-7xl w-full mx-auto flex-1">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
