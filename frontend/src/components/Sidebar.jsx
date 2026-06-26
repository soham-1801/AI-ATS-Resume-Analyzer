
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  FileUp, 
  FileCode, 
  Sparkles, 
  User,
  LogOut
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const Sidebar = () => {
  const location = useLocation();
  const { logout } = useAuth();

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Resumes", path: "/resumes", icon: FileUp },
    { name: "Job Descriptions", path: "/job-descriptions", icon: FileCode },
    { name: "ATS Analysis", path: "/ats-analysis", icon: Sparkles },
    { name: "Profile", path: "/profile", icon: User },
  ];

  return (
    <aside className="w-64 glass-card border-r border-slate-800/60 flex flex-col justify-between p-4 h-full">
      <div>
        {/* Brand Logo */}
        <div className="flex items-center gap-2 px-2 py-4 mb-6">
          <Sparkles className="w-8 h-8 text-blue-500 animate-pulse" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
            ResumeATS
          </span>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-indigo-600/90 text-white shadow-md shadow-indigo-600/20"
                    : "text-slate-400 hover:bg-slate-855 hover:text-slate-100"
                }`}
              >
                <Icon className={`w-4.5 h-4.5 ${isActive ? "text-white" : "text-slate-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer logout trigger */}
      <div className="border-t border-slate-800/60 pt-4">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-rose-450 hover:bg-rose-950/20 transition-all duration-150"
        >
          <LogOut className="w-4.5 h-4.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
