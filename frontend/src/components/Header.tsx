import React from 'react';
import { Shield, Sparkles, FileCode, CheckCircle2 } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="h-16 bg-[#111827]/80 backdrop-blur border-b border-[#1f2937] px-8 flex items-center justify-between z-10 shrink-0">
      <div>
        <h1 className="text-lg font-bold text-white tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Environment badges */}
        <div className="flex items-center gap-2 bg-[#172033] border border-[#1f2937] px-3 py-1.5 rounded-full text-xs text-gray-300">
          <CheckCircle2 className="w-3.5 h-3.5 text-[#22C55E]" />
          <span>Semantic Verifier: <strong className="text-white">Active</strong></span>
        </div>

        <div className="flex items-center gap-2 bg-[#6366F1]/10 border border-[#6366F1]/20 px-3 py-1.5 rounded-full text-xs text-[#6366F1]">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AST Transformer: <strong className="text-white">Multi-Lang</strong></span>
        </div>
      </div>
    </header>
  );
};

