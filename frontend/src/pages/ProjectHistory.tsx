import React, { useState, useEffect } from 'react';
import {
  History,
  Trash2,
  ExternalLink,
  ShieldAlert,
  FileCode,
  Calendar,
  Clock,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useCompiler } from '../context/CompilerContext';

export const ProjectHistory: React.FC = () => {
  const navigate = useNavigate();
  const { runAnalysis } = useCompiler();
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const res = await api.getHistory();
      setHistoryItems(res.data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this analysis history record?')) return;
    try {
      await api.deleteHistory(id);
      setHistoryItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleOpenDetail = async (id: number) => {
    try {
      const res = await api.getHistoryDetail(id);
      if (res.data?.source_code) {
        runAnalysis(res.data.source_code, res.data.language, res.data.file_name);
        navigate('/analyzer');
      }
    } catch (err) {
      console.error('Failed to load detail:', err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-[#6366F1] uppercase tracking-wider">
            Persistent Audit Logs
          </span>
          <h2 className="text-2xl font-black text-white mt-0.5">Analysis History</h2>
          <p className="text-xs text-gray-400 mt-1">
            Historical records of parsed files, AST structures, and semantic security verifications.
          </p>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-[#172033] border border-[#1f2937] rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-[#111827] border-b border-[#1f2937] text-gray-400 uppercase">
                <th className="py-3.5 px-4 font-semibold">ID</th>
                <th className="py-3.5 px-4 font-semibold">File Name</th>
                <th className="py-3.5 px-4 font-semibold">Language</th>
                <th className="py-3.5 px-4 font-semibold">Security Score</th>
                <th className="py-3.5 px-4 font-semibold">Vulnerabilities</th>
                <th className="py-3.5 px-4 font-semibold">Lines / Tokens</th>
                <th className="py-3.5 px-4 font-semibold">Timestamp</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f2937]">
              {historyItems.length > 0 ? (
                historyItems.map((item) => (
                  <tr key={item.id} className="hover:bg-[#111827]/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-gray-400">#{item.id}</td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-white">
                      {item.file_name}
                    </td>
                    <td className="py-3.5 px-4 uppercase font-semibold text-gray-300">
                      {item.language}
                    </td>
                    <td className="py-3.5 px-4 font-bold" style={{ color: item.security_score >= 80 ? '#22C55E' : '#EF4444' }}>
                      {item.security_score} / 100
                    </td>
                    <td className="py-3.5 px-4 text-gray-300">
                      {item.vulnerabilities_count} flaws
                    </td>
                    <td className="py-3.5 px-4 text-gray-400 font-mono">
                      {item.total_lines} lines / {item.total_tokens} toks
                    </td>
                    <td className="py-3.5 px-4 text-gray-400">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : '-'}
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-3">
                      <button
                        onClick={() => handleOpenDetail(item.id)}
                        className="text-[#6366F1] hover:text-white cursor-pointer"
                        title="Open in Code Analyzer"
                      >
                        <ExternalLink className="w-4 h-4 inline" />
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="text-gray-500 hover:text-[#EF4444] cursor-pointer"
                        title="Delete record"
                      >
                        <Trash2 className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-500">
                    No history records found in database.
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

