import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import {
  Play,
  RotateCcw,
  Upload,
  BookOpen,
  Code,
  Layers,
  Terminal,
  AlertTriangle,
  CheckCircle,
  FileText,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { useCompiler } from '../context/CompilerContext';
import { ASTNodeItem } from '../services/api';

export const CodeAnalyzer: React.FC = () => {
  const {
    currentCode,
    setCurrentCode,
    currentLanguage,
    setCurrentLanguage,
    currentFileName,
    setCurrentFileName,
    analysisResult,
    isAnalyzing,
    error,
    runAnalysis,
    resetAll,
  } = useCompiler();

  const [activeTab, setActiveTab] = useState<'metrics' | 'tokens' | 'ast' | 'semantic' | 'ir'>('metrics');
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({ 'node-1': true });

  const toggleNode = (nodeId: string) => {
    setExpandedNodes((prev) => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setCurrentFileName(file.name);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'py') setCurrentLanguage('python');
    else if (ext === 'c' || ext === 'h') setCurrentLanguage('c');
    else if (ext === 'java') setCurrentLanguage('java');

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setCurrentCode(content);
      runAnalysis(content);
    };
    reader.readAsText(file);
  };

  const renderASTNode = (node: ASTNodeItem, depth = 0) => {
    const isExpanded = expandedNodes[node.id] ?? (depth < 2);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div key={node.id} className="text-xs select-none font-mono">
        <div
          onClick={() => hasChildren && toggleNode(node.id)}
          className={`flex items-center gap-1.5 py-1 px-2 rounded hover:bg-[#1f2937] transition-colors cursor-pointer ${
            depth === 0 ? 'bg-[#172033] font-semibold text-[#6366F1]' : 'text-gray-300'
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 shrink-0" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
            )
          ) : (
            <span className="w-3.5 h-3.5 inline-block shrink-0">•</span>
          )}

          <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#6366F1]/10 text-[#6366F1] border border-[#6366F1]/20">
            {node.type}
          </span>
          <span className="text-gray-200">{node.label}</span>
          {node.line && <span className="text-[10px] text-gray-500">L{node.line}</span>}
        </div>

        {hasChildren && isExpanded && (
          <div>
            {node.children.map((child) => renderASTNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Editor Controls Bar */}
      <div className="bg-[#172033] border border-[#1f2937] p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Language:</span>
            <select
              value={currentLanguage}
              onChange={(e) => setCurrentLanguage(e.target.value)}
              className="bg-[#111827] border border-[#1f2937] text-white text-xs rounded-lg px-3 py-1.5 outline-none focus:border-[#6366F1]"
            >
              <option value="python">Python (AST Native)</option>
              <option value="c">C (pycparser / C99)</option>
              <option value="java">Java (javalang AST)</option>
            </select>
          </div>

          <div className="text-xs font-mono text-gray-400">
            File: <span className="text-gray-200">{currentFileName}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 bg-[#111827] hover:bg-[#1f2937] border border-[#1f2937] text-gray-300 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors">
            <Upload className="w-3.5 h-3.5" />
            Upload File
            <input type="file" onChange={handleFileUpload} className="hidden" accept=".py,.c,.h,.java,.txt" />
          </label>

          <button
            onClick={resetAll}
            className="flex items-center gap-1.5 bg-[#111827] hover:bg-[#1f2937] border border-[#1f2937] text-gray-300 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Clear
          </button>

          <button
            onClick={() => runAnalysis()}
            disabled={isAnalyzing}
            className="flex items-center gap-2 bg-[#6366F1] hover:bg-[#4F46E5] text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-lg shadow-[#6366F1]/20 transition-all disabled:opacity-50 cursor-pointer"
          >
            <Play className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
            {isAnalyzing ? 'Parsing & Analyzing...' : 'Analyze Source'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-xl text-xs text-[#EF4444] flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Analysis Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Monaco Code Editor */}
        <div className="lg:col-span-7 bg-[#172033] border border-[#1f2937] rounded-2xl overflow-hidden flex flex-col h-[650px]">
          <div className="h-10 bg-[#111827] border-b border-[#1f2937] px-4 flex items-center justify-between text-xs text-gray-400">
            <span className="flex items-center gap-2 font-mono">
              <Code className="w-4 h-4 text-[#6366F1]" />
              {currentFileName}
            </span>
            <span>Lines: {currentCode.split('\n').length}</span>
          </div>

          <div className="flex-1">
            <Editor
              height="100%"
              language={currentLanguage === 'c' ? 'c' : currentLanguage === 'java' ? 'java' : 'python'}
              theme="vs-dark"
              value={currentCode}
              onChange={(val) => setCurrentCode(val || '')}
              options={{
                fontSize: 13,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                automaticLayout: true,
              }}
            />
          </div>
        </div>

        {/* Right: Compiler Inspection Tabs */}
        <div className="lg:col-span-5 bg-[#172033] border border-[#1f2937] rounded-2xl overflow-hidden flex flex-col h-[650px]">
          {/* Tabs navigation */}
          <div className="flex bg-[#111827] border-b border-[#1f2937] text-xs overflow-x-auto">
            {[
              { id: 'metrics', label: 'Report', icon: FileText },
              { id: 'tokens', label: 'Tokens', icon: Terminal },
              { id: 'ast', label: 'AST Visualizer', icon: Layers },
              { id: 'semantic', label: 'Semantic', icon: CheckCircle },
              { id: 'ir', label: 'IR Code', icon: Code },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-4 py-2.5 font-medium transition-colors border-b-2 cursor-pointer ${
                  activeTab === tab.id
                    ? 'border-[#6366F1] text-white bg-[#172033]'
                    : 'border-transparent text-gray-400 hover:text-gray-200'
                }`}
              >
                <tab.icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {activeTab === 'metrics' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-[#111827] rounded-xl border border-[#1f2937]">
                    <span className="text-gray-400 text-[11px]">Parsing Status</span>
                    <div className="text-base font-bold text-white mt-1 flex items-center gap-1.5">
                      {analysisResult?.syntax_valid ? (
                        <>
                          <CheckCircle className="w-4 h-4 text-[#22C55E]" />
                          <span>Syntax Valid</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-4 h-4 text-[#EF4444]" />
                          <span>Syntax Error</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="p-3 bg-[#111827] rounded-xl border border-[#1f2937]">
                    <span className="text-gray-400 text-[11px]">Analysis Time</span>
                    <div className="text-base font-bold text-white mt-1">
                      {analysisResult?.parsing_time_ms ?? 0} ms
                    </div>
                  </div>

                  <div className="p-3 bg-[#111827] rounded-xl border border-[#1f2937]">
                    <span className="text-gray-400 text-[11px]">Total Tokens</span>
                    <div className="text-base font-bold text-white mt-1">
                      {analysisResult?.total_tokens ?? 0}
                    </div>
                  </div>

                  <div className="p-3 bg-[#111827] rounded-xl border border-[#1f2937]">
                    <span className="text-gray-400 text-[11px]">AST Nodes</span>
                    <div className="text-base font-bold text-[#A855F7] mt-1">
                      {analysisResult?.ast_nodes_count ?? 0}
                    </div>
                  </div>

                  <div className="p-3 bg-[#111827] rounded-xl border border-[#1f2937]">
                    <span className="text-gray-400 text-[11px]">Functions</span>
                    <div className="text-base font-bold text-[#6366F1] mt-1">
                      {analysisResult?.functions_count ?? 0}
                    </div>
                  </div>

                  <div className="p-3 bg-[#111827] rounded-xl border border-[#1f2937]">
                    <span className="text-gray-400 text-[11px]">Variables</span>
                    <div className="text-base font-bold text-[#22C55E] mt-1">
                      {analysisResult?.variables_count ?? 0}
                    </div>
                  </div>
                </div>

                {analysisResult?.syntax_errors && analysisResult.syntax_errors.length > 0 && (
                  <div className="p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-xl space-y-1">
                    <span className="font-semibold text-[#EF4444]">Syntax Errors:</span>
                    {analysisResult.syntax_errors.map((err, i) => (
                      <div key={i} className="text-gray-300 font-mono text-[11px]">
                        {err}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'tokens' && (
              <div className="space-y-2">
                <div className="text-gray-400 text-[11px] mb-2">
                  Showing first 100 classified tokens from lexical analyzer:
                </div>
                <div className="space-y-1">
                  {analysisResult?.tokens?.slice(0, 100).map((tok, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-1.5 rounded bg-[#111827] border border-[#1f2937] font-mono text-[11px]"
                    >
                      <span className="text-white font-medium">{tok.value}</span>
                      <div className="flex items-center gap-2">
                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#6366F1]/10 text-[#6366F1]">
                          {tok.classification}
                        </span>
                        <span className="text-gray-500 text-[10px]">
                          L{tok.line}:{tok.column}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'ast' && (
              <div className="space-y-1 bg-[#111827] p-2 rounded-xl border border-[#1f2937] overflow-x-auto">
                {analysisResult?.ast ? (
                  renderASTNode(analysisResult.ast)
                ) : (
                  <div className="p-4 text-center text-gray-500">AST not generated yet.</div>
                )}
              </div>
            )}

            {activeTab === 'semantic' && (
              <div className="space-y-3">
                <div>
                  <h4 className="font-semibold text-gray-200 mb-1.5">Symbol Table:</h4>
                  <div className="space-y-1">
                    {analysisResult?.semantic?.symbols?.map((sym, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-1.5 rounded bg-[#111827] border border-[#1f2937] text-[11px]"
                      >
                        <span className="font-mono text-white">{sym.name}</span>
                        <div className="flex items-center gap-2 text-gray-400">
                          <span className="text-[10px] px-1 bg-[#1f2937] rounded">
                            {sym.symbol_type} ({sym.data_type})
                          </span>
                          <span className="text-[10px]">Scope: {sym.scope}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {analysisResult?.semantic?.issues && analysisResult.semantic.issues.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-200 mb-1.5">Semantic Issues:</h4>
                    <div className="space-y-1">
                      {analysisResult.semantic.issues.map((iss, i) => (
                        <div
                          key={i}
                          className="p-2 rounded bg-[#EF4444]/10 border border-[#EF4444]/20 text-[11px] text-gray-300"
                        >
                          <span className="font-bold text-[#EF4444] mr-2">[{iss.issue_type}]</span>
                          {iss.message}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'ir' && (
              <div className="space-y-1 font-mono text-[11px] bg-[#111827] p-3 rounded-xl border border-[#1f2937]">
                <div className="text-gray-400 text-[10px] mb-2 font-sans">
                  Three-Address Code (TAC) Quadruples:
                </div>
                {analysisResult?.ir_instructions?.map((inst) => (
                  <div key={inst.index} className="flex items-center gap-2 text-gray-300 py-0.5">
                    <span className="text-gray-600 w-6 text-right">{inst.index}:</span>
                    <span className="text-[#6366F1] font-bold w-24">{inst.opcode}</span>
                    <span className="text-white">
                      {inst.result ? `${inst.result} = ` : ''}
                      {inst.arg1 || ''} {inst.arg2 ? `, ${inst.arg2}` : ''}
                    </span>
                    {inst.comment && (
                      <span className="text-gray-500 italic text-[10px]"># {inst.comment}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

