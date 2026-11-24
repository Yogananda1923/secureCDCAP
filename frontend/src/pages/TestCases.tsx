import React, { useState, useEffect } from 'react';
import {
  Play,
  RotateCw,
  CheckCircle2,
  XCircle,
  Clock,
  Filter,
  CheckSquare,
  Search,
  ExternalLink,
  Code2,
} from 'lucide-react';
import { api, TestCaseItem, TestRunResult, TestSuiteSummary } from '../services/api';
import { useCompiler } from '../context/CompilerContext';

export const TestCases: React.FC = () => {
  const { loadSampleCode } = useCompiler();
  const [testCases, setTestCases] = useState<TestCaseItem[]>([]);
  const [results, setResults] = useState<Record<string, TestRunResult>>({});
  const [summary, setSummary] = useState<TestSuiteSummary | null>(null);
  const [isRunningAll, setIsRunningAll] = useState<boolean>(false);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('All');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    loadTestCases();
  }, []);

  const loadTestCases = async () => {
    try {
      const res = await api.getTestCases();
      setTestCases(res.data);
    } catch (err) {
      console.error('Failed to load test cases:', err);
    }
  };

  const runSingle = async (testId: string) => {
    setRunningId(testId);
    try {
      const res = await api.runSingleTest(testId);
      setResults((prev) => ({ ...prev, [testId]: res.data }));
    } catch (err) {
      console.error('Error running test:', err);
    } finally {
      setRunningId(null);
    }
  };

  const runAll = async () => {
    setIsRunningAll(true);
    try {
      const langParam = selectedLanguage === 'All' ? undefined : selectedLanguage.toLowerCase();
      const catParam = selectedCategory === 'All' ? undefined : selectedCategory;
      const res = await api.runAllTests(langParam, catParam);
      setSummary(res.data);
      const resMap: Record<string, TestRunResult> = {};
      res.data.results.forEach((r) => {
        resMap[r.test_id] = r;
      });
      setResults(resMap);
    } catch (err) {
      console.error('Failed to run all tests:', err);
    } finally {
      setIsRunningAll(false);
    }
  };

  const filteredTests = testCases.filter((tc) => {
    const matchesLang = selectedLanguage === 'All' || tc.language.toLowerCase() === selectedLanguage.toLowerCase();
    const matchesCat = selectedCategory === 'All' || tc.category.toLowerCase().includes(selectedCategory.toLowerCase());
    const matchesSearch =
      tc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tc.test_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesLang && matchesCat && matchesSearch;
  });

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Test Execution Summary Banner */}
      <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl flex flex-wrap items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#6366F1]">
            <CheckSquare className="w-4 h-4" />
            <span>Automated Regression Test Suite</span>
          </div>
          <h2 className="text-xl font-black text-white mt-1">Compiler Verification Benchmarks</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Real static analysis & security engine verification ({testCases.length} predefined test cases)
          </p>
        </div>

        <div className="flex items-center gap-4">
          {summary && (
            <div className="flex items-center gap-6 text-xs border-r border-[#1f2937] pr-6">
              <div>
                <span className="text-gray-400">Passed:</span>
                <span className="font-bold text-[#22C55E] ml-1.5">{summary.passed}</span>
              </div>
              <div>
                <span className="text-gray-400">Failed:</span>
                <span className="font-bold text-[#EF4444] ml-1.5">{summary.failed}</span>
              </div>
              <div>
                <span className="text-gray-400">Success Rate:</span>
                <span className="font-bold text-white ml-1.5">{summary.success_percentage}%</span>
              </div>
              <div>
                <span className="text-gray-400">Avg Time:</span>
                <span className="font-bold text-white ml-1.5">{summary.average_execution_time_ms} ms</span>
              </div>
            </div>
          )}

          <button
            onClick={runAll}
            disabled={isRunningAll}
            className="flex items-center gap-2 bg-[#6366F1] hover:bg-[#4F46E5] text-white px-5 py-2.5 rounded-xl text-xs font-semibold shadow-lg shadow-[#6366F1]/20 transition-all cursor-pointer disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isRunningAll ? 'animate-spin' : ''}`} />
            {isRunningAll ? 'Executing Engine Tests...' : 'Execute All Tests'}
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
              placeholder="Filter by test ID or benchmark name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#111827] border border-[#1f2937] rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-gray-500 outline-none focus:border-[#6366F1]"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="bg-[#111827] border border-[#1f2937] text-white rounded-lg px-3 py-1.5 outline-none text-xs"
            >
              <option value="All">All Languages</option>
              <option value="Python">Python (11 tests)</option>
              <option value="C">C (10 tests)</option>
              <option value="Java">Java (10 tests)</option>
            </select>
          </div>

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
            <option value="Optimization">Optimization</option>
            <option value="Clean">Clean Code</option>
          </select>
        </div>
      </div>

      {/* Tests Table */}
      <div className="bg-[#172033] border border-[#1f2937] rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-[#111827] border-b border-[#1f2937] text-gray-400 uppercase">
                <th className="py-3.5 px-4 font-semibold">Test ID</th>
                <th className="py-3.5 px-4 font-semibold">Language</th>
                <th className="py-3.5 px-4 font-semibold">Benchmark Name</th>
                <th className="py-3.5 px-4 font-semibold">Category</th>
                <th className="py-3.5 px-4 font-semibold">Expected Detection</th>
                <th className="py-3.5 px-4 font-semibold">Actual Detection</th>
                <th className="py-3.5 px-4 font-semibold">Result</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f2937]">
              {filteredTests.map((tc) => {
                const res = results[tc.test_id];
                const isRunning = runningId === tc.test_id;

                return (
                  <tr key={tc.test_id} className="hover:bg-[#111827]/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-[#6366F1]">
                      {tc.test_id}
                    </td>
                    <td className="py-3.5 px-4 uppercase font-semibold text-gray-300">
                      {tc.language}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-white">{tc.name}</div>
                      <div className="text-[11px] text-gray-400 line-clamp-1">{tc.description}</div>
                    </td>
                    <td className="py-3.5 px-4 text-gray-300">{tc.category}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-[#111827] border border-[#1f2937] text-gray-300">
                        {tc.expected_detection || 'Clean'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {res ? (
                        <span className="font-medium text-gray-200">
                          {res.actual_detection || 'Clean'}
                        </span>
                      ) : (
                        <span className="text-gray-500 italic">Not run</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {res ? (
                        res.passed ? (
                          <span className="flex items-center gap-1 text-[#22C55E] font-bold">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            PASSED
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-[#EF4444] font-bold">
                            <XCircle className="w-3.5 h-3.5" />
                            FAILED
                          </span>
                        )
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => runSingle(tc.test_id)}
                        disabled={isRunning || isRunningAll}
                        className="px-2.5 py-1 bg-[#6366F1]/10 hover:bg-[#6366F1] text-[#6366F1] hover:text-white border border-[#6366F1]/20 rounded-md transition-all cursor-pointer font-medium"
                      >
                        {isRunning ? 'Running...' : 'Run'}
                      </button>
                      <button
                        onClick={() => {
                          loadSampleCode({
                            id: tc.test_id,
                            language: tc.language,
                            code: tc.source_code,
                          });
                        }}
                        title="Load in Code Analyzer"
                        className="p-1 hover:text-[#6366F1] text-gray-400 cursor-pointer"
                      >
                        <Code2 className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

