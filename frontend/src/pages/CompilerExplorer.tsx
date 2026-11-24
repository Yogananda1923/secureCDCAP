import React, { useState } from 'react';
import {
  Cpu,
  Layers,
  Terminal,
  ArrowRight,
  GitCommit,
  CheckCircle2,
  Code2,
  ListOrdered,
} from 'lucide-react';
import { useCompiler } from '../context/CompilerContext';

export const CompilerExplorer: React.FC = () => {
  const { analysisResult, currentFileName, currentLanguage } = useCompiler();
  const [activeStage, setActiveStage] = useState<'tokens' | 'ast' | 'symbols' | 'ir' | 'cfg'>('ir');

  const pipelineStages = [
    { id: 'tokens', title: '1. Lexical Analysis', desc: 'Token Stream & Classification' },
    { id: 'ast', title: '2. Syntax Analysis', desc: 'Abstract Syntax Tree' },
    { id: 'symbols', title: '3. Semantic Analysis', desc: 'Symbol Table & Scopes' },
    { id: 'ir', title: '4. Intermediate Code', desc: 'Three-Address Code (TAC)' },
    { id: 'cfg', title: '5. Control Flow Graph', desc: 'Basic Blocks & Branches' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Compiler Pipeline Breadcrumb / Stage Tracker */}
      <div className="bg-[#172033] border border-[#1f2937] p-6 rounded-2xl space-y-4">
        <div>
          <span className="text-xs font-semibold text-[#6366F1] uppercase tracking-wider">
            Deep Compiler Internals
          </span>
          <h2 className="text-xl font-black text-white mt-0.5">
            Compiler Pipeline Explorer: <span className="font-mono text-[#6366F1]">{currentFileName}</span>
          </h2>
        </div>

        {/* Pipeline stage cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {pipelineStages.map((stage) => {
            const isActive = activeStage === stage.id;
            return (
              <button
                key={stage.id}
                onClick={() => setActiveStage(stage.id as any)}
                className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#6366F1] border-[#6366F1] text-white shadow-lg shadow-[#6366F1]/20'
                    : 'bg-[#111827] border-[#1f2937] text-gray-400 hover:text-white hover:border-gray-700'
                }`}
              >
                <div className="text-xs font-bold">{stage.title}</div>
                <div className={`text-[11px] mt-1 ${isActive ? 'text-white/80' : 'text-gray-500'}`}>
                  {stage.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Explorer Stage Viewport */}
      <div className="bg-[#172033] border border-[#1f2937] rounded-2xl p-6 min-h-[500px]">
        {/* Stage 1: Tokens */}
        {activeStage === 'tokens' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Terminal className="w-4 h-4 text-[#6366F1]" />
                Lexical Token Stream ({analysisResult?.total_tokens ?? 0} tokens)
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-[550px] overflow-y-auto">
              {analysisResult?.tokens?.map((tok, i) => (
                <div
                  key={i}
                  className="p-2.5 bg-[#111827] border border-[#1f2937] rounded-xl flex items-center justify-between text-xs font-mono"
                >
                  <span className="font-bold text-white">{tok.value}</span>
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#6366F1]/10 text-[#6366F1] border border-[#6366F1]/20">
                      {tok.classification}
                    </span>
                    <span className="text-gray-500 text-[10px]">L{tok.line}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stage 2: AST Tree JSON / Structure */}
        {activeStage === 'ast' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#A855F7]" />
              Abstract Syntax Tree Hierarchy ({analysisResult?.ast_nodes_count ?? 0} nodes)
            </h3>
            <pre className="p-4 bg-[#111827] border border-[#1f2937] rounded-xl font-mono text-xs text-gray-300 max-h-[550px] overflow-auto">
              {JSON.stringify(analysisResult?.ast, null, 2)}
            </pre>
          </div>
        )}

        {/* Stage 3: Symbol Table */}
        {activeStage === 'symbols' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
              Semantic Symbol Table & Scopes
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-[#111827] border-b border-[#1f2937] text-gray-400 uppercase">
                    <th className="py-3 px-4 font-semibold">Identifier</th>
                    <th className="py-3 px-4 font-semibold">Symbol Type</th>
                    <th className="py-3 px-4 font-semibold">Inferred Type</th>
                    <th className="py-3 px-4 font-semibold">Scope</th>
                    <th className="py-3 px-4 font-semibold">Declared Line</th>
                    <th className="py-3 px-4 font-semibold">Is Used</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1f2937]">
                  {analysisResult?.semantic?.symbols?.map((sym, i) => (
                    <tr key={i} className="hover:bg-[#111827]/40">
                      <td className="py-3 px-4 font-mono font-bold text-white">{sym.name}</td>
                      <td className="py-3 px-4 text-gray-300">{sym.symbol_type}</td>
                      <td className="py-3 px-4 font-mono text-[#6366F1]">{sym.data_type}</td>
                      <td className="py-3 px-4 text-gray-300">{sym.scope}</td>
                      <td className="py-3 px-4 font-mono text-gray-400">Line {sym.declared_line}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            sym.is_used
                              ? 'bg-[#22C55E]/10 text-[#22C55E]'
                              : 'bg-[#EF4444]/10 text-[#EF4444]'
                          }`}
                        >
                          {sym.is_used ? 'TRUE' : 'UNUSED'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Stage 4: Intermediate Representation (TAC) */}
        {activeStage === 'ir' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Code2 className="w-4 h-4 text-[#6366F1]" />
              Three-Address Code (TAC) Quadruples
            </h3>

            <div className="bg-[#111827] p-4 rounded-xl border border-[#1f2937] font-mono text-xs space-y-1.5 max-h-[550px] overflow-y-auto">
              {analysisResult?.ir_instructions?.map((inst) => (
                <div key={inst.index} className="flex items-center gap-4 py-1 border-b border-[#1f2937]/50">
                  <span className="text-gray-500 w-8 text-right font-bold">{inst.index}:</span>
                  <span className="text-[#6366F1] font-extrabold w-32">{inst.opcode}</span>
                  <span className="text-white flex-1">
                    {inst.result ? `${inst.result} = ` : ''}
                    {inst.arg1 || ''} {inst.arg2 ? `, ${inst.arg2}` : ''}
                  </span>
                  {inst.line && <span className="text-gray-500 text-[10px]">line {inst.line}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stage 5: Control Flow Graph (CFG) */}
        {activeStage === 'cfg' && (
          <div className="space-y-6">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <GitCommit className="w-4 h-4 text-[#F59E0B]" />
              Control Flow Graph & Basic Blocks
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisResult?.cfg?.blocks?.map((bb) => (
                <div
                  key={bb.id}
                  className="bg-[#111827] border border-[#1f2937] p-4 rounded-xl space-y-3"
                >
                  <div className="flex items-center justify-between border-b border-[#1f2937] pb-2">
                    <span className="font-mono font-bold text-[#6366F1]">{bb.id}</span>
                    <span className="text-[11px] text-gray-400 font-semibold">{bb.label}</span>
                  </div>

                  <div className="space-y-1 font-mono text-[11px] text-gray-300">
                    {bb.instructions.map((inst, idx) => (
                      <div key={idx} className="line-clamp-1">
                        {inst.opcode} {inst.result || inst.arg1 || ''}
                      </div>
                    ))}
                  </div>

                  <div className="pt-2 border-t border-[#1f2937] text-[10px] text-gray-400 flex items-center justify-between">
                    <div>
                      Preds: <strong className="text-gray-200">{bb.predecessors.join(', ') || 'None'}</strong>
                    </div>
                    <div>
                      Succs: <strong className="text-gray-200">{bb.successors.join(', ') || 'Exit'}</strong>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

