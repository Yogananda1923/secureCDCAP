import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Filter,
  Search,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  AlertOctagon,
  Lock,
  Wand2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCompiler } from '../context/CompilerContext';

const SEVERITY_BADGES: Record<string, { bg: string; text: string; border: string }> = {
  Critical: { bg: 'bg-[#EF4444]/10', text: 'text-[#EF4444]', border: 'border-[#EF4444]/30' },
  High: { bg: 'bg-[#F97316]/10', text: 'text-[#F97316]', border: 'border-[#F97316]/30' },
  Medium: { bg: 'bg-[#F59E0B]/10', text: 'text-[#F59E0B]', border: 'border-[#F59E0B]/30' },
  Low: { bg: 'bg-[#3B82F6]/10', text: 'text-[#3B82F6]', border: 'border-[#3B82F6]/30' },
  Informational: { bg: 'bg-[#10B981]/10', text: 'text-[#10B981]', border: 'border-[#10B981]/30' },
};

export const SecurityAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const { securityScan, currentFileName } = useCompiler();

  const [selectedSeverity, setSelectedSeverity] = useState<string>('All');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedVuln, setExpandedVuln] = useState<string | null>(null);

  const vulns = securityScan?.vulnerabilities || [];

  const filteredVulns = vulns.filter((v) => {
    const matchesSev = selectedSeverity === 'All' || v.severity.toLowerCase() === selectedSeverity.toLowerCase();
    const matchesCat = selectedCategory === 'All' || v.category.toLowerCase().includes(selectedCategory.toLowerCase());
    const matchesSearch =
      v.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.vulnerable_snippet.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (v.cwe_id && v.cwe_id.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesSev && matchesCat && matchesSearch;
  });

  const score = securityScan?.security_score ?? 100;
  const scoreColor = score >= 80 ? '#22C55E' : score >= 50 ? '#F59E0B' : '#EF4444';

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Security Overview Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3 rounded-xl bg-[#6366F1]/10 text-[#6366F1]">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-gray-400">Security Score</div>
            <div className="text-3xl font-black mt-1" style={{ color: scoreColor }}>
              {score} <span className="text-sm font-normal text-gray-400">/ 100</span>
            </div>
          </div>
        </div>

        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl">
          <div className="text-xs uppercase tracking-wider text-gray-400">Total Vulnerabilities</div>
          <div className="text-3xl font-black text-white mt-1">
            {securityScan?.total_vulnerabilities ?? 0}
          </div>
          <div className="text-xs text-gray-400 mt-1">Found in {currentFileName}</div>
        </div>

        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl">
          <div className="text-xs uppercase tracking-wider text-[#EF4444]">Critical / High Risk</div>
          <div className="text-3xl font-black text-[#EF4444] mt-1">
            {(securityScan?.critical_count ?? 0) + (securityScan?.high_count ?? 0)}
          </div>
          <div className="text-xs text-gray-400 mt-1">Requires immediate remediation</div>
        </div>

        <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex flex-col justify-between">
          <div className="text-xs uppercase tracking-wider text-gray-400">Automated Fixes</div>
          <button
            onClick={() => navigate('/transform')}
            className="flex items-center justify-center gap-2 bg-[#6366F1] hover:bg-[#4F46E5] text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-lg shadow-[#6366F1]/20 transition-all cursor-pointer"
          >
            <Wand2 className="w-3.5 h-3.5" />
            Apply Verified Fixes
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#172033] border border-[#1f2937] p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by vulnerability name, snippet, or CWE..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#111827] border border-[#1f2937] rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-500 outline-none focus:border-[#6366F1]"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Severity filter */}
          <div className="flex items-center gap-2 text-xs">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="bg-[#111827] border border-[#1f2937] text-white rounded-lg px-3 py-1.5 outline-none text-xs"
            >
              <option value="All">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          {/* Category filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-[#111827] border border-[#1f2937] text-white rounded-lg px-3 py-1.5 outline-none text-xs"
          >
            <option value="All">All Categories</option>
            <option value="Injection">Injection</option>
            <option value="Memory">Memory Safety</option>
            <option value="Authentication">Auth & Crypto</option>
            <option value="Input Validation">Input Validation</option>
            <option value="General">General Security</option>
          </select>
        </div>
      </div>

      {/* Vulnerabilities List */}
      <div className="space-y-4">
        {filteredVulns.length > 0 ? (
          filteredVulns.map((v, i) => {
            const isExpanded = expandedVuln === `${v.vuln_id}-${i}`;
            const badge = SEVERITY_BADGES[v.severity] || SEVERITY_BADGES['Medium'];

            return (
              <div
                key={i}
                className="bg-[#172033] border border-[#1f2937] rounded-2xl overflow-hidden transition-all"
              >
                {/* Header row */}
                <div
                  onClick={() => setExpandedVuln(isExpanded ? null : `${v.vuln_id}-${i}`)}
                  className="p-5 flex items-center justify-between cursor-pointer hover:bg-[#111827]/40 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span
                      className={`px-2.5 py-1 rounded-md text-xs font-bold border ${badge.bg} ${badge.text} ${badge.border}`}
                    >
                      {v.severity.toUpperCase()}
                    </span>
                    <div>
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        {v.name}
                        {v.cwe_id && (
                          <span className="text-[11px] font-mono text-gray-400 font-normal">
                            ({v.cwe_id})
                          </span>
                        )}
                      </h4>
                      <div className="text-xs text-gray-400 mt-0.5 flex items-center gap-3">
                        <span>Category: <strong>{v.category}</strong></span>
                        <span>•</span>
                        <span>Line: <strong className="font-mono text-gray-200">{v.line_number}</strong></span>
                        <span>•</span>
                        <span>Confidence: <strong>{v.confidence}</strong></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-gray-400">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-6 bg-[#111827]/50 border-t border-[#1f2937] space-y-4 text-xs">
                    {/* Vulnerable Snippet */}
                    <div>
                      <div className="text-gray-400 font-semibold mb-1">Vulnerable Code Snippet:</div>
                      <pre className="p-3 bg-[#0B1020] border border-[#1f2937] rounded-xl text-[#EF4444] font-mono text-[11px] overflow-x-auto">
                        Line {v.line_number}: {v.vulnerable_snippet}
                      </pre>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-[#172033] border border-[#1f2937] rounded-xl space-y-1">
                        <div className="font-semibold text-gray-200">Root Cause Analysis</div>
                        <p className="text-gray-400 leading-relaxed">{v.root_cause}</p>
                      </div>

                      <div className="p-4 bg-[#172033] border border-[#1f2937] rounded-xl space-y-1">
                        <div className="font-semibold text-[#EF4444]">Attack Scenario</div>
                        <p className="text-gray-400 leading-relaxed">{v.attack_scenario}</p>
                      </div>
                    </div>

                    <div className="p-4 bg-[#172033] border border-[#1f2937] rounded-xl space-y-1">
                      <div className="font-semibold text-[#22C55E]">Recommended Remediation</div>
                      <p className="text-gray-300 leading-relaxed">{v.recommended_solution}</p>
                    </div>

                    {v.suggested_fix && (
                      <div>
                        <div className="text-gray-400 font-semibold mb-1">Suggested Secure Implementation:</div>
                        <pre className="p-3 bg-[#0B1020] border border-[#22C55E]/30 rounded-xl text-[#22C55E] font-mono text-[11px] overflow-x-auto">
                          {v.suggested_fix}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="p-12 text-center bg-[#172033] border border-[#1f2937] rounded-2xl space-y-2">
            <ShieldCheck className="w-12 h-12 text-[#22C55E] mx-auto" />
            <h3 className="text-base font-bold text-white">No Vulnerabilities Detected</h3>
            <p className="text-xs text-gray-400 max-w-md mx-auto">
              The current source code passed all static AST and data-flow security rules without triggering critical or high severity alerts.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

