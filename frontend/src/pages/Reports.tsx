import React, { useState } from 'react';
import {
  FileText,
  Download,
  FileCode,
  FileSpreadsheet,
  ShieldCheck,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';
import { useCompiler } from '../context/CompilerContext';
import { api } from '../services/api';

export const Reports: React.FC = () => {
  const { analysisResult, securityScan, currentFileName, currentLanguage } = useCompiler();
  const [downloading, setDownloading] = useState<string | null>(null);

  const analysisId = analysisResult?.analysis_id;

  const triggerDownload = (format: 'pdf' | 'json' | 'html') => {
    if (!analysisId) {
      alert('Please analyze code first to generate a persistent report ID.');
      return;
    }
    const url = api.getReportDownloadUrl(analysisId, format);
    window.open(url, '_blank');
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <span className="text-xs font-semibold text-[#6366F1] uppercase tracking-wider">
          Compliance & Academic Export
        </span>
        <h2 className="text-2xl font-black text-white mt-0.5">Audit Reports & Certification</h2>
        <p className="text-xs text-gray-400 mt-1">
          Export full compiler security audit reports with AST traces, CVE/CWE references, and verified transformations.
        </p>
      </div>

      {/* Target File Info Card */}
      <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="text-xs text-gray-400">Current Analysis Target:</div>
          <div className="text-base font-bold text-white font-mono mt-0.5">
            {currentFileName} ({currentLanguage.toUpperCase()})
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Analysis ID: <strong className="text-gray-200">#{analysisId || 'Draft'}</strong> • Security Score:{' '}
            <strong className="text-[#22C55E]">{securityScan?.security_score ?? 100} / 100</strong>
          </div>
        </div>

        <div className="text-xs text-gray-400">
          Detected Flaws:{' '}
          <span className="font-bold text-white">{securityScan?.total_vulnerabilities ?? 0}</span>
        </div>
      </div>

      {/* Download Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* PDF Card */}
        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="p-3 w-fit rounded-xl bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">PDF Formal Audit Report</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Professional document with executive summary, vulnerability tables, CWE classification, and transformation proof.
            </p>
          </div>

          <button
            onClick={() => triggerDownload('pdf')}
            className="flex items-center justify-center gap-2 bg-[#6366F1] hover:bg-[#4F46E5] text-white py-2.5 px-4 rounded-xl text-xs font-semibold shadow-lg shadow-[#6366F1]/20 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" />
            Download PDF Report
          </button>
        </div>

        {/* HTML Card */}
        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="p-3 w-fit rounded-xl bg-[#6366F1]/10 text-[#6366F1] border border-[#6366F1]/20">
              <FileCode className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Interactive HTML Report</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Self-contained responsive HTML report with styled metrics, vulnerability cards, and compliance badges.
            </p>
          </div>

          <button
            onClick={() => triggerDownload('html')}
            className="flex items-center justify-center gap-2 bg-[#111827] hover:bg-[#1f2937] border border-[#1f2937] text-white py-2.5 px-4 rounded-xl text-xs font-semibold transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" />
            Download HTML Report
          </button>
        </div>

        {/* JSON Card */}
        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="p-3 w-fit rounded-xl bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Machine-Readable JSON</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Standard JSON format containing full AST telemetry, raw token streams, symbol tables, and vulnerability payloads.
            </p>
          </div>

          <button
            onClick={() => triggerDownload('json')}
            className="flex items-center justify-center gap-2 bg-[#111827] hover:bg-[#1f2937] border border-[#1f2937] text-white py-2.5 px-4 rounded-xl text-xs font-semibold transition-all cursor-pointer"
          >
            <Download className="w-4 h-4" />
            Download JSON Report
          </button>
        </div>
      </div>
    </div>
  );
};

