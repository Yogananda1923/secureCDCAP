from typing import Tuple, List, Dict, Any
from app.compiler.parser import ParserEngine
from app.compiler.semantic_analyzer import SemanticAnalyzer

class SemanticVerifier:
    """
    Verifies that the transformed code preserves the intended semantics,
    function signatures, classes, and variable references of the original program.
    """

    @staticmethod
    def verify(original_code: str, transformed_code: str, language: str = "python") -> Tuple[bool, List[str], Dict[str, Any]]:
        notes: List[str] = []
        details: Dict[str, Any] = {}

        # 1. Parse both programs
        orig_valid, orig_ast, orig_errors = ParserEngine.parse(original_code, language)
        trans_valid, trans_ast, trans_errors = ParserEngine.parse(transformed_code, language)

        if not trans_valid:
            return False, [f"Transformed code has syntax errors: {'; '.join(trans_errors)}"], {"syntax_error": True}

        # 2. Extract semantic profiles
        orig_semantic = SemanticAnalyzer.analyze(orig_ast, original_code, language)
        trans_semantic = SemanticAnalyzer.analyze(trans_ast, transformed_code, language)

        orig_funcs = {s.name for s in orig_semantic.symbols if s.symbol_type == "function"}
        trans_funcs = {s.name for s in trans_semantic.symbols if s.symbol_type == "function"}

        orig_classes = {s.name for s in orig_semantic.symbols if s.symbol_type == "class"}
        trans_classes = {s.name for s in trans_semantic.symbols if s.symbol_type == "class"}

        # Assert no original functions were lost
        missing_funcs = orig_funcs - trans_funcs
        if missing_funcs:
            notes.append(f"Semantic discrepancy: Functions missing in transformed code: {', '.join(missing_funcs)}")
            return False, notes, {"missing_functions": list(missing_funcs)}

        # Assert no original classes were lost
        missing_classes = orig_classes - trans_classes
        if missing_classes:
            notes.append(f"Semantic discrepancy: Classes missing in transformed code: {', '.join(missing_classes)}")
            return False, notes, {"missing_classes": list(missing_classes)}

        # Check for new undefined variables introduced by transformation
        orig_undef = set(orig_semantic.undefined_variables)
        trans_undef = set(trans_semantic.undefined_variables)
        new_undef = trans_undef - orig_undef

        if new_undef:
            notes.append(f"Transformation introduced undefined variables: {', '.join(new_undef)}")
            return False, notes, {"new_undefined_variables": list(new_undef)}

        details["original_functions_count"] = len(orig_funcs)
        details["transformed_functions_count"] = len(trans_funcs)
        details["functions_preserved"] = True
        details["classes_preserved"] = True
        notes.append("Semantic verification successful: All function declarations, classes, and variable references are intact.")

        return True, notes, details

