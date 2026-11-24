from typing import Tuple, List
from app.compiler.parser import ParserEngine

class SyntaxVerifier:
    """
    Verifies that generated or transformed source code parses cleanly
    without syntax errors in the target language.
    """

    @staticmethod
    def verify(code: str, language: str = "python") -> Tuple[bool, List[str]]:
        is_valid, ast_tree, errors = ParserEngine.parse(code, language)
        return is_valid, errors

