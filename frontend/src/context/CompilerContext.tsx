import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  api,
  CodeAnalysisResponse,
  SecurityScanResponse,
  TransformationResponse,
} from '../services/api';

interface CompilerContextType {
  currentCode: string;
  setCurrentCode: (code: string) => void;
  currentLanguage: string;
  setCurrentLanguage: (lang: string) => void;
  currentFileName: string;
  setCurrentFileName: (name: string) => void;
  analysisResult: CodeAnalysisResponse | null;
  securityScan: SecurityScanResponse | null;
  transformationResult: TransformationResponse | null;
  isAnalyzing: boolean;
  isTransforming: boolean;
  error: string | null;
  runAnalysis: (code?: string, lang?: string, fileName?: string) => Promise<void>;
  runTransformation: (vulnIds?: string[], enableOpts?: boolean) => Promise<void>;
  loadSampleCode: (sample: any) => void;
  resetAll: () => void;
}

const DEFAULT_PYTHON_CODE = `import sqlite3
import os

DATABASE_PASSWORD = "HardcodedAdminPassword2026!"

def login_user(username, user_password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL Injection via string interpolation
    query = f"SELECT id, role FROM accounts WHERE user = '{username}' AND pass = '{user_password}'"
    cursor.execute(query)
    record = cursor.fetchone()
    conn.close()
    return record
`;

const CompilerContext = createContext<CompilerContextType | undefined>(undefined);

export const CompilerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentCode, setCurrentCode] = useState<string>(DEFAULT_PYTHON_CODE);
  const [currentLanguage, setCurrentLanguage] = useState<string>('python');
  const [currentFileName, setCurrentFileName] = useState<string>('auth_service.py');
  const [analysisResult, setAnalysisResult] = useState<CodeAnalysisResponse | null>(null);
  const [securityScan, setSecurityScan] = useState<SecurityScanResponse | null>(null);
  const [transformationResult, setTransformationResult] = useState<TransformationResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isTransforming, setIsTransforming] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (codeToRun?: string, langToRun?: string, fileToRun?: string) => {
    const code = codeToRun || currentCode;
    const lang = langToRun || currentLanguage;
    const fName = fileToRun || currentFileName;

    if (!code.trim()) {
      setError('Source code cannot be empty.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Run analysis and security scan concurrently
      const [analysisRes, scanRes] = await Promise.all([
        api.analyzeCode(code, lang, fName),
        api.scanSecurity(code, lang, fName),
      ]);

      setAnalysisResult(analysisRes.data);
      setSecurityScan(scanRes.data);
    } catch (err: any) {
      console.error('Analysis failed:', err);
      setError(err?.response?.data?.detail || err.message || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const runTransformation = async (vulnIds?: string[], enableOpts: boolean = true) => {
    setIsTransforming(true);
    setError(null);
    try {
      const res = await api.transformCode(currentCode, currentLanguage, vulnIds, enableOpts);
      setTransformationResult(res.data);
    } catch (err: any) {
      console.error('Transformation failed:', err);
      setError(err?.response?.data?.detail || err.message || 'Transformation failed');
    } finally {
      setIsTransforming(false);
    }
  };

  const loadSampleCode = (sample: any) => {
    setCurrentCode(sample.code);
    setCurrentLanguage(sample.language);
    const ext = sample.language === 'python' ? '.py' : sample.language === 'c' ? '.c' : '.java';
    setCurrentFileName(`${sample.id}${ext}`);
    setAnalysisResult(null);
    setSecurityScan(null);
    setTransformationResult(null);
  };

  const resetAll = () => {
    setCurrentCode('');
    setAnalysisResult(null);
    setSecurityScan(null);
    setTransformationResult(null);
    setError(null);
  };

  // Run initial analysis on first mount
  useEffect(() => {
    runAnalysis(DEFAULT_PYTHON_CODE, 'python', 'auth_service.py');
  }, []);

  return (
    <CompilerContext.Provider
      value={{
        currentCode,
        setCurrentCode,
        currentLanguage,
        setCurrentLanguage,
        currentFileName,
        setCurrentFileName,
        analysisResult,
        securityScan,
        transformationResult,
        isAnalyzing,
        isTransforming,
        error,
        runAnalysis,
        runTransformation,
        loadSampleCode,
        resetAll,
      }}
    >
      {children}
    </CompilerContext.Provider>
  );
};

export const useCompiler = () => {
  const context = useContext(CompilerContext);
  if (!context) {
    throw new Error('useCompiler must be used within a CompilerProvider');
  }
  return context;
};

