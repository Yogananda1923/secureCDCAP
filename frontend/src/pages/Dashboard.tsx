import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  ShieldAlert,
  FileCode,
  Layers,
  Activity,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  CheckCircle2,
  Clock,
  ExternalLink,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { api, DashboardStats } from '../services/api';
import { useCompiler } from '../context/CompilerContext';

const SEVERITY_COLORS: Record<string, string> = {
  Critical: '#EF4444',
  High: '#F97316',
  Medium: '#F59E0B',
  Low: '#3B82F6',
  Informational: '#10B981',
};

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { securityScan } = useCompiler();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const res = await api.getDashboard();
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const severityData = stats
    ? Object.entries(stats.severity_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const languageData = stats
    ? Object.entries(stats.language_distribution).map(([name, value]) => ({
        name: name.toUpperCase(),
        files: value,
      }))
    : [];

  const score = securityScan ? securityScan.security_score : (stats?.average_security_score ?? 100);
  const scoreColor = score >= 80 ? '#22C55E' : score >= 50 ? '#F59E0B' : '#EF4444';

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-r from-[#172033] to-[#111827] border border-[#1f2937] p-6 rounded-2xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#6366F1]">
            <Activity className="w-3.5 h-3.5" />
            <span>Semantic Verification & Security Audit</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">
            SecureCompiler<span className="text-[#6366F1]">AI</span> Overview
          </h2>
          <p className="text-sm text-gray-400">
            Intelligent AST-level vulnerability detection, semantic verification, and explainable optimization.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/analyzer')}
            className="flex items-center gap-2 bg-[#6366F1] hover:bg-[#4F46E5] text-white px-4 py-2.5 rounded-xl font-medium text-sm transition-all shadow-lg shadow-[#6366F1]/20 cursor-pointer"
          >
            <FileCode className="w-4 h-4" />
            Analyze New Code
          </button>
          <button
            onClick={() => navigate('/tests')}
            className="flex items-center gap-2 bg-[#172033] hover:bg-[#1f2937] border border-[#1f2937] text-gray-300 hover:text-white px-4 py-2.5 rounded-xl font-medium text-sm transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
            Run Test Suite
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Security Score Card */}
        <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Security Score</span>
            <div className="p-2 rounded-lg bg-[#6366F1]/10 text-[#6366F1]">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold tracking-tight" style={{ color: scoreColor }}>
              {score}
            </span>
            <span className="text-gray-400 text-sm font-medium">/ 100</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-gray-400">
            <TrendingUp className="w-3.5 h-3.5 text-[#22C55E]" />
            <span>AST semantic verification rating</span>
          </div>
        </div>

        {/* Total Vulnerabilities */}
        <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Vulnerabilities</span>
            <div className="p-2 rounded-lg bg-[#EF4444]/10 text-[#EF4444]">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-white tracking-tight">
              {stats?.total_vulnerabilities ?? 0}
            </span>
            <span className="text-xs text-gray-400 font-normal">detected</span>
          </div>
          <div className="mt-3 flex items-center gap-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-[#EF4444]/20 text-[#EF4444] font-semibold">
              {stats?.critical_vulns_count ?? 0} Critical
            </span>
            <span className="px-2 py-0.5 rounded bg-[#F97316]/20 text-[#F97316] font-semibold">
              {stats?.high_vulns_count ?? 0} High
            </span>
          </div>
        </div>

        {/* Total Files Analyzed */}
        <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Source Files</span>
            <div className="p-2 rounded-lg bg-[#6366F1]/10 text-[#6366F1]">
              <FileCode className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-white tracking-tight">
              {stats?.total_source_files ?? 0}
            </span>
            <span className="text-xs text-gray-400">analyzed</span>
          </div>
          <div className="mt-3 text-xs text-gray-400">
            Python, C, & Java pipelines
          </div>
        </div>

        {/* Predefined Test Suite */}
        <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Test Suite</span>
            <div className="p-2 rounded-lg bg-[#22C55E]/10 text-[#22C55E]">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-[#22C55E] tracking-tight">
              {stats?.tests_summary?.total_test_cases ?? 31}
            </span>
            <span className="text-xs text-gray-400">test cases</span>
          </div>
          <div className="mt-3 text-xs text-gray-400">
            100% genuine compiler execution
          </div>
        </div>
      </div>

      {/* Visual Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Severity Distribution Chart */}
        <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Vulnerability Severity Distribution</h3>
              <p className="text-xs text-gray-400">Breakdown by CVSS/CWE risk tiers</p>
            </div>
            <ShieldAlert className="w-5 h-5 text-gray-400" />
          </div>

          <div className="h-64 flex items-center justify-center">
            {severityData.length > 0 && severityData.some((d) => d.value > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {severityData.map((entry) => (
                      <Cell
                        key={entry.name}
                        fill={SEVERITY_COLORS[entry.name] || '#6366F1'}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#111827',
                      borderColor: '#1f2937',
                      borderRadius: '8px',
                      color: '#fff',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 text-sm">
                No active vulnerabilities logged.
              </div>
            )}
          </div>

          <div className="grid grid-cols-4 gap-2 pt-2 border-t border-[#1f2937] text-xs">
            {['Critical', 'High', 'Medium', 'Low'].map((sev) => (
              <div key={sev} className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: SEVERITY_COLORS[sev] }}
                ></span>
                <span className="text-gray-400">{sev}:</span>
                <span className="font-bold text-white">
                  {stats?.severity_distribution[sev] ?? 0}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Language Distribution Chart */}
        <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Languages Analyzed</h3>
              <p className="text-xs text-gray-400">Source files parsed across compiler modules</p>
            </div>
            <Layers className="w-5 h-5 text-gray-400" />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={languageData}>
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    borderColor: '#1f2937',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                />
                <Bar dataKey="files" fill="#6366F1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[#1f2937] text-xs text-center">
            <div>
              <span className="text-gray-400">Python: </span>
              <strong className="text-white">{stats?.language_distribution?.python ?? 0}</strong>
            </div>
            <div>
              <span className="text-gray-400">C: </span>
              <strong className="text-white">{stats?.language_distribution?.c ?? 0}</strong>
            </div>
            <div>
              <span className="text-gray-400">Java: </span>
              <strong className="text-white">{stats?.language_distribution?.java ?? 0}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Module Status & Architecture Pipelines */}
      <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6 space-y-4">
        <h3 className="text-base font-bold text-white">Compiler & Verification Pipeline Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-[#111827] border border-[#1f2937] rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-300">Module 1: Parsing & AST</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#22C55E]/20 text-[#22C55E]">OPERATIONAL</span>
            </div>
            <p className="text-xs text-gray-400">
              Universal Pygments Lexer, Python AST, pycparser C, and javalang AST with IR generation.
            </p>
          </div>

          <div className="p-4 bg-[#111827] border border-[#1f2937] rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-300">Module 2: Verification Engine</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#22C55E]/20 text-[#22C55E]">OPERATIONAL</span>
            </div>
            <p className="text-xs text-gray-400">
              AST & CFG taint analysis across Injection, Memory Safety, Cryptography, and Deserialization.
            </p>
          </div>

          <div className="p-4 bg-[#111827] border border-[#1f2937] rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-300">Module 3: Transformation</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#22C55E]/20 text-[#22C55E]">OPERATIONAL</span>
            </div>
            <p className="text-xs text-gray-400">
              Verified automatic security fixes, constant folding, dead code elimination, and side-by-side diffs.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Analysis History Table */}
      <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Recent Compiler Analyses</h3>
            <p className="text-xs text-gray-400">Latest source files submitted for security compilation</p>
          </div>
          <button
            onClick={() => navigate('/history')}
            className="text-xs text-[#6366F1] hover:underline flex items-center gap-1 cursor-pointer"
          >
            View all history <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#1f2937] text-gray-400 uppercase">
                <th className="pb-3 font-semibold">File Name</th>
                <th className="pb-3 font-semibold">Language</th>
                <th className="pb-3 font-semibold">Security Score</th>
                <th className="pb-3 font-semibold">Vulnerabilities</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f2937]">
              {stats?.recent_analyses && stats.recent_analyses.length > 0 ? (
                stats.recent_analyses.map((item) => (
                  <tr key={item.id} className="hover:bg-[#111827]/50 transition-colors">
                    <td className="py-3 font-mono text-gray-200">{item.file_name}</td>
                    <td className="py-3 uppercase text-gray-400">{item.language}</td>
                    <td className="py-3 font-bold" style={{ color: item.security_score >= 80 ? '#22C55E' : '#EF4444' }}>
                      {item.security_score} / 100
                    </td>
                    <td className="py-3 text-gray-300">{item.vulnerabilities_count} flaws</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20">
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => navigate('/history')}
                        className="text-[#6366F1] hover:text-white cursor-pointer"
                      >
                        <ExternalLink className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-gray-500">
                    No recent analyses recorded. Use the Code Analyzer to start.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

