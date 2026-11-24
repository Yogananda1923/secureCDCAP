import io
import tokenize
from typing import List, Dict, Any, Tuple
from pygments.lexers import PythonLexer, CLexer, JavaLexer
from pygments.token import Token
from app.schemas.compiler_schemas import TokenItem

def classify_pygments_token(ttype) -> str:
    if ttype in Token.Keyword:
        return "Keyword"
    elif ttype in Token.Name:
        return "Identifier"
    elif ttype in Token.Operator:
        return "Operator"
    elif ttype in Token.Literal.Number:
        return "NumericLiteral"
    elif ttype in Token.Literal.String:
        return "StringLiteral"
    elif ttype in Token.Literal:
        return "Literal"
    elif ttype in Token.Punctuation:
        return "Delimiter"
    elif ttype in Token.Comment:
        return "Comment"
    elif ttype in Token.Text:
        return "Whitespace"
    return "Other"

class LexerEngine:
    """
    Universal Lexical Analysis Engine for Python, C, and Java.
    Generates structured token streams, classifies lexical units,
    and computes lexical metrics.
    """
    
    @staticmethod
    def tokenize(code: str, language: str = "python") -> Tuple[List[TokenItem], Dict[str, Any]]:
        lang = (language or "python").lower()
        tokens: List[TokenItem] = []
        
        # Select appropriate lexer
        if lang == "c":
            lexer = CLexer()
        elif lang == "java":
            lexer = JavaLexer()
        else:
            lexer = PythonLexer()
            
        raw_tokens = list(lexer.get_tokens(code))
        
        line = 1
        col = 1
        
        for ttype, value in raw_tokens:
            classification = classify_pygments_token(ttype)
            
            # Skip pure whitespace unless it contains line breaks
            if classification != "Whitespace":
                clean_val = value.strip()
                if clean_val:
                    tokens.append(TokenItem(
                        value=value,
                        type=str(ttype),
                        line=line,
                        column=col,
                        classification=classification
                    ))
            
            # Update line and column counters
            newlines = value.count('\n')
            if newlines > 0:
                line += newlines
                last_newline_idx = value.rfind('\n')
                col = len(value) - last_newline_idx
            else:
                col += len(value)
                
        # Token metrics
        counts_by_classification: Dict[str, int] = {}
        for t in tokens:
            counts_by_classification[t.classification] = counts_by_classification.get(t.classification, 0) + 1
            
        metrics = {
            "total_tokens": len(tokens),
            "keywords": counts_by_classification.get("Keyword", 0),
            "identifiers": counts_by_classification.get("Identifier", 0),
            "operators": counts_by_classification.get("Operator", 0),
            "literals": (
                counts_by_classification.get("Literal", 0) + 
                counts_by_classification.get("NumericLiteral", 0) + 
                counts_by_classification.get("StringLiteral", 0)
            ),
            "delimiters": counts_by_classification.get("Delimiter", 0),
            "comments": counts_by_classification.get("Comment", 0),
            "classification_breakdown": counts_by_classification
        }
        
        return tokens, metrics

