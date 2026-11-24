from typing import Dict, List, Optional
from app.schemas.compiler_schemas import SymbolItem, ScopeItem

class Scope:
    def __init__(self, name: str, level: int = 0, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, SymbolItem] = {}
        self.children: List['Scope'] = []
        self.id = f"scope_{name}_{level}_{id(self)}"

    def define(self, symbol: SymbolItem):
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str, recursive: bool = True) -> Optional[SymbolItem]:
        if name in self.symbols:
            return self.symbols[name]
        if recursive and self.parent:
            return self.parent.lookup(name, recursive=True)
        return None

    def to_schema(self) -> ScopeItem:
        return ScopeItem(
            id=self.id,
            name=self.name,
            level=self.level,
            parent_id=self.parent.id if self.parent else None,
            symbols=list(self.symbols.keys())
        )

class SymbolTable:
    def __init__(self):
        self.global_scope = Scope(name="global", level=0, parent=None)
        self.current_scope = self.global_scope
        self.all_scopes: List[Scope] = [self.global_scope]

    def enter_scope(self, name: str) -> Scope:
        new_scope = Scope(
            name=name,
            level=self.current_scope.level + 1,
            parent=self.current_scope
        )
        self.current_scope.children.append(new_scope)
        self.all_scopes.append(new_scope)
        self.current_scope = new_scope
        return new_scope

    def exit_scope(self) -> Scope:
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
        return self.current_scope

    def define(self, name: str, symbol_type: str, line: int, data_type: str = "unknown", is_initialized: bool = True):
        sym = SymbolItem(
            name=name,
            symbol_type=symbol_type,
            scope=self.current_scope.name,
            declared_line=line,
            data_type=data_type,
            is_used=False,
            is_initialized=is_initialized
        )
        self.current_scope.define(sym)
        return sym

    def mark_used(self, name: str) -> bool:
        sym = self.current_scope.lookup(name)
        if sym:
            sym.is_used = True
            return True
        return False

    def is_defined(self, name: str) -> bool:
        return self.current_scope.lookup(name) is not None

    def get_all_symbols(self) -> List[SymbolItem]:
        symbols: List[SymbolItem] = []
        for scope in self.all_scopes:
            symbols.extend(scope.symbols.values())
        return symbols

    def get_all_scope_schemas(self) -> List[ScopeItem]:
        return [scope.to_schema() for scope in self.all_scopes]

