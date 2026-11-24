import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface TokenItem {
  value: string;
  type: string;
  line: number;
  column: number;
  classification: string;
}

export interface ASTNodeItem {
  id: string;
  type: string;
  label: string;
  line?: number;
  column?: number;
  children: ASTNodeItem[];
  properties: Record<string, any>;
}

export interface SymbolItem {
  name: string;
  symbol_type: string;
  scope: string;
  declared_line: number;
  data_type: string;
  is_used: boolean;
  is_initialized: boolean;
}

export interface ScopeItem {
  id: string;
  name: string;
  level: number;
  parent_id?: string;
  symbols: string[];
}

export interface SemanticIssueItem {
  issue_type: string;
  severity: string;
  message: string;
  line: number;
  column?: number;
}

export interface SemanticResult {
  symbols: SymbolItem[];
  scopes: ScopeItem[];
  undefined_variables: string[];
  unused_variables: string[];
  unreachable_lines: number[];
  type_warnings: string[];
  issues: SemanticIssueItem[];
}

export interface IRInstructionItem {
  index: number;
  opcode: string;
  arg1?: string;
  arg2?: string;
  result?: string;
  line?: number;
  comment?: string;
}

export interface BasicBlockItem {
  id: string;
  label: string;
  instructions: IRInstructionItem[];
  predecessors: string[];
  successors: string[];
}

export interface CFGEdgeItem {
  from_block: string;
  to_block: string;
  label?: string;
}

export interface CFGResult {
  entry_block: string;
  exit_blocks: string[];
  blocks: BasicBlockItem[];
  edges: CFGEdgeItem[];
}

export interface VulnerabilityItem {
  id?: number;
  vuln_id: string;
  name: string;
  category: string;
  cwe_id?: string;
  cwe_name?: string;
  severity: string;
  confidence: string;
  line_number: number;
  end_line_number?: number;
  vulnerable_snippet: string;
  root_cause: string;
  attack_scenario: string;
  security_impact: string;
  recommended_solution: string;
  suggested_fix: string;
  is_transformed: boolean;
}

export interface CodeAnalysisResponse {
  analysis_id?: number;
  file_name: string;
  language: string;
  total_lines: number;
  total_tokens: number;
  ast_nodes_count: number;
  functions_count: number;
  variables_count: number;
  syntax_valid: boolean;
  syntax_errors: string[];
  parsing_time_ms: number;
  status: string;
  tokens: TokenItem[];
  ast?: ASTNodeItem;
  semantic: SemanticResult;
  ir_instructions: IRInstructionItem[];
  basic_blocks: BasicBlockItem[];
  cfg: CFGResult;
}

export interface SecurityScanResponse {
  analysis_id?: number;
  security_score: number;
  total_vulnerabilities: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  informational_count: number;
  vulnerabilities: VulnerabilityItem[];
  severity_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  limitations_disclaimer: string;
}

export interface DiffLine {
  type: 'same' | 'add' | 'remove' | 'modify';
  original_line_num?: number;
  modified_line_num?: number;
  content: string;
}

export interface TransformationResponse {
  transformation_id?: number;
  original_code: string;
  transformed_code: string;
  diff_lines: DiffLine[];
  transformations_applied: string[];
  optimizations_applied: string[];
  is_verified: boolean;
  verification_status: string;
  explanation: {
    what_changed: string;
    why_changed: string;
    original_problem: string;
    new_implementation: string;
    security_benefit: string;
    performance_benefit: string;
    semantic_verified: boolean;
    regression_tests_passed: string[];
  };
  verification_details: Record<string, any>;
}

export interface TestCaseItem {
  id?: number;
  test_id: string;
  name: string;
  language: string;
  category: string;
  description?: string;
  source_code: string;
  expected_detection?: string;
  expected_severity?: string;
  expected_verification?: string;
}

export interface TestRunResult {
  test_id: string;
  name: string;
  language: string;
  category: string;
  status: string;
  expected_detection?: string;
  actual_detection?: string;
  expected_severity?: string;
  actual_severity?: string;
  execution_time_ms: number;
  error_message?: string;
  passed: boolean;
}

export interface TestSuiteSummary {
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  success_percentage: number;
  average_execution_time_ms: number;
  results: TestRunResult[];
}

export interface DashboardStats {
  total_analyzed_projects: number;
  total_source_files: number;
  total_vulnerabilities: number;
  average_security_score: number;
  critical_vulns_count: number;
  high_vulns_count: number;
  medium_vulns_count: number;
  low_vulns_count: number;
  tests_summary: Record<string, any>;
  language_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  recent_analyses: any[];
}

// API functions
export const api = {
  analyzeCode: (code: string, language: string = 'python', file_name?: string) =>
    apiClient.post<CodeAnalysisResponse>('/analyze', { code, language, file_name }),

  scanSecurity: (code: string, language: string = 'python', file_name?: string) =>
    apiClient.post<SecurityScanResponse>('/security/scan', { code, language, file_name }),

  transformCode: (code: string, language: string = 'python', vuln_ids?: string[], enable_optimizations: boolean = true) =>
    apiClient.post<TransformationResponse>('/transform', {
      code,
      language,
      vulnerability_ids: vuln_ids,
      enable_optimizations,
    }),

  verifyCode: (original_code: string, transformed_code: string, language: string = 'python') =>
    apiClient.post('/verify', { original_code, transformed_code, language }),

  optimizeCode: (code: string, language: string = 'python') =>
    apiClient.post<TransformationResponse>('/optimize', { code, language }),

  getDashboard: () => apiClient.get<DashboardStats>('/dashboard'),

  getTestCases: () => apiClient.get<TestCaseItem[]>('/tests'),

  runSingleTest: (test_id: string) => apiClient.post<TestRunResult>('/tests/run', { test_id }),

  runAllTests: (language?: string, category?: string) =>
    apiClient.post<TestSuiteSummary>('/tests/run-all', { language, category }),

  getHistory: () => apiClient.get<any[]>('/history'),

  getHistoryDetail: (id: number) => apiClient.get<any>(`/history/${id}`),

  deleteHistory: (id: number) => apiClient.delete(`/history/${id}`),

  getSamples: () => apiClient.get<any[]>('/samples'),

  getReportDownloadUrl: (id: number, format: 'pdf' | 'json' | 'html') =>
    `${API_BASE_URL}/reports/download/${id}?format=${format}`,
};

