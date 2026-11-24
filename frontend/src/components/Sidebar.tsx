import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Code2,
  ShieldAlert,
  Wand2,
  CheckSquare,
  Cpu,
  History,
  FileText,
  Terminal,
  ShieldCheck,
} from 'lucide-react';

interface SidebarProps {
  currentStatus?: string;
}

export const Sidebar: React.FC<SidebarProps> = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Code Analyzer', path: '/analyzer', icon: Code2 },
    { name: 'Security Analysis', path: '/security', icon: ShieldAlert },
    { name: 'Secure Transformation', path: '/transform', icon: Wand2 },
    { name: 'Test Cases', path: '/tests', icon: CheckSquare },
    { name: 'Compiler Explorer', path: '/compiler', icon: Cpu },
    { name: 'Project History', path: '/history', icon: History },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  return (
    <aside className="w-64 bg-[#111827] border-r border-[#1f2937] flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Logo */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-[#1f2937]">
          <div className="p-2 rounded-lg bg-[#6366F1]/10 text-[#6366F1] border border-[#6366F1]/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="font-extrabold text-base tracking-wide text-white">
              SecureCompiler<span className="text-[#6366F1]">AI</span>
            </div>
            <div className="text-[10px] text-gray-400 font-mono tracking-wider uppercase">
              Semantic Compiler v1.0
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#6366F1] text-white shadow-lg shadow-[#6366F1]/20'
                      : 'text-gray-300 hover:bg-[#172033] hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Engine Status Footer */}
      <div className="p-4 m-3 bg-[#172033] border border-[#1f2937] rounded-xl text-xs space-y-2">
        <div className="flex items-center justify-between text-gray-400">
          <span className="flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-[#6366F1]" />
            Compiler Engine
          </span>
          <span className="flex items-center gap-1.5 text-[#22C55E] font-medium">
            <span className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse"></span>
            Online
          </span>
        </div>
        <div className="text-[11px] text-gray-400 font-mono">
          Backend: <span className="text-gray-200">127.0.0.1:8000</span>
        </div>
        <div className="text-[10px] text-gray-500">
          AST & Verification Pipeline Active
        </div>
      </div>
    </aside>
  );
};

