import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import AnalysisHistory, Vulnerability
from app.schemas.compiler_schemas import CodeAnalysisRequest, CodeAnalysisResponse
from app.compiler.lexer import LexerEngine
from app.compiler.parser import ParserEngine
from app.compiler.ast_analyzer import ASTAnalyzer
from app.compiler.semantic_analyzer import SemanticAnalyzer
from app.compiler.intermediate_representation import IRGenerator
from app.compiler.control_flow import CFGBuilder
from app.security.vulnerability_engine import VulnerabilityEngine

router = APIRouter(prefix="", tags=["Analysis"])

@router.post("/analyze", response_model=CodeAnalysisResponse)
def analyze_code(request: CodeAnalysisRequest, db: Session = Depends(get_db)):
    start_time = time.perf_counter()
    code = request.code
    lang = request.language.lower()
    file_name = request.file_name or f"untitled.{'py' if lang=='python' else ('c' if lang=='c' else 'java')}"

    if not code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    # 1. Lexical Analysis
    tokens, lex_metrics = LexerEngine.tokenize(code, lang)

    # 2. Syntax Analysis & AST Generation
    is_valid, raw_ast, syntax_errors = ParserEngine.parse(code, lang)
    ast_tree, ast_node_count = ASTAnalyzer.to_tree(raw_ast, lang)

    # 3. Semantic Analysis
    semantic_result = SemanticAnalyzer.analyze(raw_ast, code, lang)

    # 4. Intermediate Representation & CFG
    ir_instructions = IRGenerator.generate(raw_ast, code, lang)
    cfg = CFGBuilder.build(ir_instructions)

    # 5. Security Vulnerability Scan for Score Calculation
    scan_result = VulnerabilityEngine.scan(raw_ast, code, lang, file_name)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    lines_count = len(code.splitlines())

    # Count functions and variables
    funcs_count = len([s for s in semantic_result.symbols if s.symbol_type == "function"])
    vars_count = len([s for s in semantic_result.symbols if s.symbol_type == "variable"])

    # Persist in DB
    history_entry = AnalysisHistory(
        project_id=request.project_id,
        file_name=file_name,
        language=lang,
        source_code=code,
        total_lines=lines_count,
        total_tokens=len(tokens),
        ast_nodes_count=ast_node_count,
        functions_count=funcs_count,
        variables_count=vars_count,
        syntax_valid=is_valid,
        security_score=scan_result.security_score,
        parsing_time_ms=elapsed_ms,
        status="Analyzed" if is_valid else "Syntax Error",
        tokens_data=[t.model_dump() for t in tokens[:300]],  # Store first 300 tokens
        ast_data=ast_tree.model_dump() if ast_tree else None,
        semantic_data=semantic_result.model_dump(),
        ir_data=[i.model_dump() for i in ir_instructions],
        cfg_data=cfg.model_dump()
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    # Save vulnerabilities to database
    for v in scan_result.vulnerabilities:
        db_vuln = Vulnerability(
            analysis_id=history_entry.id,
            vuln_id=v.vuln_id,
            name=v.name,
            category=v.category,
            cwe_id=v.cwe_id,
            cwe_name=v.cwe_name,
            severity=v.severity,
            confidence=v.confidence,
            line_number=v.line_number,
            end_line_number=v.end_line_number,
            vulnerable_snippet=v.vulnerable_snippet,
            root_cause=v.root_cause,
            attack_scenario=v.attack_scenario,
            security_impact=v.security_impact,
            recommended_solution=v.recommended_solution,
            suggested_fix=v.suggested_fix
        )
        db.add(db_vuln)
    db.commit()

    return CodeAnalysisResponse(
        analysis_id=history_entry.id,
        file_name=file_name,
        language=lang,
        total_lines=lines_count,
        total_tokens=len(tokens),
        ast_nodes_count=ast_node_count,
        functions_count=funcs_count,
        variables_count=vars_count,
        syntax_valid=is_valid,
        syntax_errors=syntax_errors,
        parsing_time_ms=elapsed_ms,
        status=history_entry.status,
        tokens=tokens,
        ast=ast_tree,
        semantic=semantic_result,
        ir_instructions=ir_instructions,
        basic_blocks=cfg.blocks,
        cfg=cfg
    )

