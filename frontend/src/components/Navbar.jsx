
import { useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { User as UserIcon } from "lucide-react";

const Navbar = () => {
  const location = useLocation();
  const { user } = useAuth();

  const getPageTitle = () => {
    switch (location.pathname) {
      case "/dashboard":
        return "Dashboard";
      case "/resumes":
        return "Manage Resumes";
      case "/job-descriptions":
        return "Job Profiles";
      case "/ats-analysis":
        return "ATS Scan Assessment";
      case "/profile":
        return "My Profile";
      default:
        return "Workspace";
    }
  };

  return (
    <header className="h-16 border-b border-slate-800/40 flex items-center justify-between px-8 bg-[#080c14]/40 backdrop-blur-md sticky top-0 z-10 w-full">
      <h1 className="text-lg font-semibold text-slate-200">{getPageTitle()}</h1>
      
      <div className="flex items-center gap-6">
        {/* Connection status indicator */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800/80 px-3 py-1.5 rounded-full text-xs text-emerald-400 font-semibold select-none">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
          ATS Core Active
        </div>

        {/* User Badge */}
        <div className="flex items-center gap-3">
          <div className="w-8.5 h-8.5 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
            <UserIcon className="w-4 h-4 text-slate-400" />
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-200">{user?.name}</p>
            <p className="text-[10px] text-slate-500">{user?.email}</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
