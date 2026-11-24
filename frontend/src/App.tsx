import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { CompilerProvider } from './context/CompilerContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { CodeAnalyzer } from './pages/CodeAnalyzer';
import { SecurityAnalysis } from './pages/SecurityAnalysis';
import { SecureTransformation } from './pages/SecureTransformation';
import { TestCases } from './pages/TestCases';
import { CompilerExplorer } from './pages/CompilerExplorer';
import { ProjectHistory } from './pages/ProjectHistory';
import { Reports } from './pages/Reports';

const AppLayout: React.FC = () => {
  const location = useLocation();

  const getPageInfo = () => {
    switch (location.pathname) {
      case '/':
        return { title: 'Dashboard', subtitle: 'Real-time Security Verification & Compiler Metrics' };
      case '/analyzer':
        return { title: 'Code Analyzer', subtitle: 'Source Code Input, Lexical, Syntax, AST & Semantic Analysis' };
      case '/security':
        return { title: 'Security Analysis', subtitle: 'Vulnerability Detection, CWE Diagnostics & Attack Scenarios' };
      case '/transform':
        return { title: 'Secure Transformation', subtitle: 'Verified Code Hardening, Side-by-Side Diff & Optimization' };
      case '/tests':
        return { title: 'Test Cases & Benchmarks', subtitle: 'Multi-Language Automated Test Suite Execution' };
      case '/compiler':
        return { title: 'Compiler Explorer', subtitle: 'Tokens, AST Hierarchy, Symbol Table & Control Flow Graph' };
      case '/history':
        return { title: 'Project History', subtitle: 'Database of Past Compilations & Historical Audit Runs' };
      case '/reports':
        return { title: 'Audit Reports', subtitle: 'Downloadable PDF, JSON, and HTML Security Certificates' };
      default:
        return { title: 'SecureCompilerAI', subtitle: 'Intelligent Semantic Compiler' };
    }
  };

  const { title, subtitle } = getPageInfo();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0B1020] text-[#E5E7EB]">
      {/* Permanent Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header title={title} subtitle={subtitle} />

        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyzer" element={<CodeAnalyzer />} />
            <Route path="/security" element={<SecurityAnalysis />} />
            <Route path="/transform" element={<SecureTransformation />} />
            <Route path="/tests" element={<TestCases />} />
            <Route path="/compiler" element={<CompilerExplorer />} />
            <Route path="/history" element={<ProjectHistory />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <CompilerProvider>
      <Router>
        <AppLayout />
      </Router>
    </CompilerProvider>
  );
}

export default App;
