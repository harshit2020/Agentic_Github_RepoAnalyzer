from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_python as tspy
import tree_sitter_javascript as tsjs
 
# ─────────────────────────────────────────────
# Setup parsers — reusing same pattern as load_chunk.py
# ─────────────────────────────────────────────
PY_PARSER = Parser(Language(tspy.language()))
JS_PARSER = Parser(Language(tsjs.language()))
 
 
# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
 
def get_node_text(node, source_code: str) -> str:
    """Extract raw text from a node using byte offsets."""
    return source_code[node.start_byte:node.end_byte]
 
 
def find_nodes(root, *node_types) -> list:
    """
    Walk the entire tree and collect every node
    whose type is in node_types.
 
    This is the same walk() pattern from load_chunk.py
    but generalised to collect any node type you want.
    """
    found = []
 
    def walk(node):
        if node.type in node_types:
            found.append(node)
        for child in node.children:
            walk(child)
 
    walk(root)
    return found
 
 
# ─────────────────────────────────────────────
# PYTHON
# ─────────────────────────────────────────────
 
def get_python_imports(source_code: str) -> list[str]:
    """
    Extract all imports from a Python file.
 
    Handles:
        import os
        import os.path
        from pathlib import Path
        from . import something  (relative imports)
    """
    tree = PY_PARSER.parse(bytes(source_code, "utf-8"))
    imports = []
 
    # two node types carry import info in Python grammar:
    # import_statement      → "import os"
    # import_from_statement → "from pathlib import Path"
    nodes = find_nodes(
        tree.root_node,
        "import_statement",
        "import_from_statement"
    )
 
    for node in nodes:
        if node.type == "import_statement":
            # children: [import_keyword, dotted_name/identifier, ...]
            for child in node.children:
                if child.type in {"dotted_name", "identifier"}:
                    imports.append(get_node_text(child, source_code))
 
        elif node.type == "import_from_statement":
            # children: [from_keyword, module_name, import_keyword, names...]
            # we only want the module name (first dotted_name or relative_import)
            for child in node.children:
                if child.type in {"dotted_name", "relative_import"}:
                    imports.append(get_node_text(child, source_code))
                    break
 
    return list(set(imports))
 
 
# ─────────────────────────────────────────────
# JAVASCRIPT
# ─────────────────────────────────────────────
 
def get_js_imports(source_code: str) -> list[str]:
    """
    Extract all imports from a JS/JSX file.
 
    Handles:
        import React from 'react'
        import { useState } from 'react'
        import * as _ from 'lodash'
        import './styles.css'
        const x = require('./utils')
    """
    tree = JS_PARSER.parse(bytes(source_code, "utf-8"))
    imports = []
 
    # ── ES module imports ──────────────────────
    # import_statement structure:
    #   import [specifiers] from "module_string"
    #                             ^^^^^^^^^^^^^ this is a string node
    import_nodes = find_nodes(tree.root_node, "import_statement")
    for node in import_nodes:
        for child in node.children:
            if child.type == "string":
                raw = get_node_text(child, source_code)
                imports.append(raw.strip("'\""))
 
    # ── require() calls ───────────────────────
    # call_expression structure:
    #   function: identifier     → "require"
    #   arguments: argument_list → ("./utils")
    call_nodes = find_nodes(tree.root_node, "call_expression")
    for node in call_nodes:
        func = node.child_by_field_name("function")
        args = node.child_by_field_name("arguments")
        if func and get_node_text(func, source_code) == "require" and args:
            for arg in args.children:
                if arg.type == "string":
                    raw = get_node_text(arg, source_code)
                    imports.append(raw.strip("'\""))
 
    return list(set(imports))
 
 
# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
 
def generate_dep_graph(input_code_path: str) -> dict:
    """
    Generate a dependency graph for all Python and JS/JSX files.
 
    Returns:
        {
            "path/to/file.py": {
                "filename": "file.py",
                "imports": ["os", "pathlib", "utils.load_chunk"]
            },
            "path/to/App.jsx": {
                "filename": "App.jsx",
                "imports": ["react", "./components/Header", "axios"]
            }
        }
    """
    path = Path(input_code_path)
    dep_graph = {}
    supported = {".py", ".js", ".jsx"}
 
    for file in path.rglob("*"):
        if file.suffix not in supported:
            continue
        if "node_modules" in file.parts:
            continue
 
        try:
            source_code = file.read_text(encoding="utf-8", errors="ignore")
 
            if file.suffix == ".py":
                imports = get_python_imports(source_code)
            else:
                imports = get_js_imports(source_code)
 
            dep_graph[str(file)] = {
                "filename": file.name,
                "imports":  imports
            }
            print(f"Dep graph: {file.name} → {len(imports)} imports")
 
        except Exception as e:
            print(f"Skipping {file}: {e}")
 
    return dep_graph
 
 
if __name__ == "__main__":
    from pprint import pprint
    graph = generate_dep_graph("../../input_code")
    pprint(graph)