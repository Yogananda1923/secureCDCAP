# SecureCompilerAI
### A Semantic Compiler for Intelligent Vulnerability Detection and Verified Code Optimization

SecureCompilerAI is an end-to-end intelligent semantic compiler platform designed for deep static program analysis, automated vulnerability detection, semantic verification, and explainable optimization across **Python**, **C**, and **Java**.

---

## Architecture Overview

```
                      Source Code Input
                             ↓
                      Lexical Analysis (Tokens & Classification)
                             ↓
                      Syntax Analysis (AST Generation)
                             ↓
                      Semantic Analysis (Symbol Table, Scopes, Types)
                             ↓
                 Intermediate Representation (TAC Quadruples)
                             ↓
                    Control Flow Graph (Basic Blocks)
                             ↓
             Semantic Security Verification Engine (CWE Rules)
                             ↓
             Verified Secure Transformation & Optimization Passes
                             ↓
                 Automated Regression & Semantic Verification
                             ↓
                      Hardened Source Code Output
```

---

## Tech Stack

- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS, Monaco Editor, Lucide React, Recharts, Axios, React Router.
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite, Uvicorn.
- **Compiler Engine**: Native Python `ast`, `pycparser` C parser, `javalang` Java AST parser, Pygments lexer, custom Three-Address Code (TAC) Intermediate Representation, Control Flow Graph builder.
- **Security Engine**: AST taint analysis, control flow heuristics, and semantic rule engines for CWE-89, CWE-78, CWE-94, CWE-120, CWE-134, CWE-416, CWE-502, CWE-798, CWE-328, CWE-330, CWE-22, CWE-377, CWE-732, and CWE-391.
- **Reporting**: ReportLab PDF generator, interactive HTML generator, structured JSON export.

---

## Quick Start: Host Locally

### Option 1: One-Click Startup Scripts (Recommended)

#### On Windows:
Double-click `start_all.bat` (or run it from CMD/PowerShell):
```cmd
start_all.bat
```
*Alternatively, run in two separate terminals:*
```cmd
start_backend.bat
start_frontend.bat
```

#### On Linux / macOS:
```bash
chmod +x start_*.sh
./start_all.sh
```

---

### Option 2: Manual Terminal Startup

#### 1. Backend Server
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 2. Frontend Development Server
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
- **Web Dashboard**: [http://localhost:5173](http://localhost:5173)

---

## Core Pages & Features

1. **Dashboard (`/`)**: Real-time KPI metrics, overall security scores, severity breakdown pie chart, language distribution, and recent compilation runs.
2. **Code Analyzer (`/analyzer`)**: Monaco code editor with syntax highlighting, token stream analysis, expandable AST hierarchy tree, symbol table with scopes, and Three-Address Code (TAC) generation.
3. **Security Analysis (`/security`)**: Categorized vulnerability findings with CWE references, line numbers, root cause explanations, attack scenarios, and remediation guides.
4. **Secure Transformation (`/transform`)**: Side-by-side Monaco Diff comparison of original code vs. secure hardened code, interactive fix applicator, and explainability notes.
5. **Test Cases & Benchmarks (`/tests`)**: 31 pre-built multi-language benchmarks executed against the genuine compiler engine with detailed pass/fail verification.
6. **Compiler Explorer (`/compiler`)**: Deep pipeline inspection displaying tokens, AST nodes, symbol tables, TAC instructions, and Control Flow Graph basic blocks.
7. **Project History (`/history`)**: Persistent SQLite database storing past compilation records, security scores, and full code artifacts.
8. **Reports & Certification (`/reports`)**: Downloadable security audit certificates available in formal PDF, interactive HTML, and structured JSON formats.

---

## Running Automated Tests

Run backend unit tests, compiler tests, and security regression suites:
```bash
cd backend
python -m pytest tests/test_compiler.py -v
```

All 9 test suites validate:
- Lexer tokenization and classification
- AST generation and tree conversion
- Semantic analysis and unreachable code detection
- IR (TAC) and Control Flow Graph construction
- Semantic vulnerability detection
- Verified code transformations
- Regression safety gate verification
- 31 predefined test benchmarks execution

