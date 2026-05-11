from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_python as tspy
import tree_sitter_javascript as tsjs

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
    """
    found = []
 
    def walk(node):
        if node.type in node_types:
            found.append(node)
        for child in node.children:
            walk(child)
 
    walk(root)
    return found
 
 
def find_calls_inside(node, source_code: str) -> list[str]:
    """
    Given a node (function body), find all function calls inside it.
    Returns a deduplicated list of called function names.
    """
    call_nodes = find_nodes(node, "call")          # Python
    call_nodes += find_nodes(node, "call_expression")  # JS
 
    calls = []
    for call in call_nodes:
        # Python:  call → function: identifier or attribute
        # JS:      call_expression → function: identifier or member_expression
        func_node = call.child_by_field_name("function")
        if not func_node:
            continue
 
        if func_node.type == "identifier":
            # direct call: foo()
            calls.append(get_node_text(func_node, source_code))
 
        elif func_node.type in {"attribute", "member_expression"}:
            # method call: obj.foo() → we want "foo"
            # attribute node children: [object, ".", attribute_name]
            attr = func_node.child_by_field_name("attribute") or \
                   func_node.child_by_field_name("property")
            if attr:
                calls.append(get_node_text(attr, source_code))
 
    return list(set(calls))
 
 
# ─────────────────────────────────────────────
# PYTHON
# ─────────────────────────────────────────────
 
def get_python_call_graph(source_code: str, filename: str) -> dict:
    """
    Extract function/method definitions and what they call.
 
    Handles:
        def foo():          → function_definition
        async def bar():    → function_definition (async)
        class methods       → function_definition inside class_definition
 
    Returns:
        {
            "foo": {"calls": ["bar", "baz"], "filename": "file.py"},
        }
    """
    tree = PY_PARSER.parse(bytes(source_code, "utf-8"))
    result = {}
 
    # function_definition covers both regular and async def
    func_nodes = find_nodes(tree.root_node, "function_definition")
 
    for func_node in func_nodes:
        # name field → the identifier node with the function name
        name_node = func_node.child_by_field_name("name")
        if not name_node:
            continue
 
        func_name = get_node_text(name_node, source_code)
 
        # body field → the block containing the function body
        body_node = func_node.child_by_field_name("body")
        if not body_node:
            continue
 
        calls = find_calls_inside(body_node, source_code)
 
        # remove self-calls and built-ins that are noise
        calls = [c for c in calls if c != func_name and c not in {"print", "len", "range", "str", "int", "list", "dict", "set"}]
 
        result[func_name] = {
            "calls":    calls,
            "filename": filename
        }
 
    return result
 
 
# ─────────────────────────────────────────────
# JAVASCRIPT
# ─────────────────────────────────────────────
 
def get_js_call_graph(source_code: str, filename: str) -> dict:
    """
    Extract function definitions and what they call.
 
    Handles:
        function foo() {}               → function_declaration
        const foo = () => {}            → arrow_function (via variable_declarator)
        const foo = function() {}       → function_expression
        class methods                   → method_definition
 
    Returns:
        {
            "foo": {"calls": ["bar", "fetch"], "filename": "App.jsx"},
        }
    """
    tree = JS_PARSER.parse(bytes(source_code, "utf-8"))
    result = {}
 
    JS_NOISE = {
        "console", "log", "push", "map", "filter", "reduce",
        "forEach", "then", "catch", "finally", "setTimeout",
        "setInterval", "clearTimeout", "clearInterval",
        "parseInt", "parseFloat", "JSON", "Object", "Array",
        "Math", "Promise", "resolve", "reject"
    }
 
    # ── function_declaration: function foo() {} ──
    for func_node in find_nodes(tree.root_node, "function_declaration"):
        name_node = func_node.child_by_field_name("name")
        body_node = func_node.child_by_field_name("body")
        if not name_node or not body_node:
            continue
 
        func_name = get_node_text(name_node, source_code)
        calls = [c for c in find_calls_inside(body_node, source_code)
                 if c != func_name and c not in JS_NOISE]
 
        result[func_name] = {"calls": calls, "filename": filename}
 
    # ── arrow_function / function_expression via variable_declarator ──
    # const foo = () => {}   or   const foo = function() {}
    for var_node in find_nodes(tree.root_node, "variable_declarator"):
        name_node = var_node.child_by_field_name("name")
        value_node = var_node.child_by_field_name("value")
 
        if not name_node or not value_node:
            continue
        if value_node.type not in {"arrow_function", "function_expression"}:
            continue
 
        func_name = get_node_text(name_node, source_code)
 
        # body is the last child of arrow_function/function_expression
        body_node = value_node.child_by_field_name("body")
        if not body_node:
            continue
 
        calls = [c for c in find_calls_inside(body_node, source_code)
                 if c != func_name and c not in JS_NOISE]
 
        result[func_name] = {"calls": calls, "filename": filename}
 
    # ── method_definition inside class ──
    for method_node in find_nodes(tree.root_node, "method_definition"):
        name_node = method_node.child_by_field_name("name")
        body_node = method_node.child_by_field_name("body")
        if not name_node or not body_node:
            continue
 
        func_name = get_node_text(name_node, source_code)
        calls = [c for c in find_calls_inside(body_node, source_code)
                 if c != func_name and c not in JS_NOISE]
 
        result[func_name] = {"calls": calls, "filename": filename}
 
    return result
 
 
# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
 
def generate_call_graph(input_code_path: str) -> dict:
    """
    Generate a call graph for all Python and JS/JSX files.
 
    Returns:
        {
            "authenticate_user": {
                "calls": ["validate_token", "check_permissions"],
                "filename": "auth.py"
            },
            "handleSubmit": {
                "calls": ["validateForm", "postData"],
                "filename": "Form.jsx"
            }
        }
    """
    path = Path(input_code_path)
    call_graph = {}
    supported = {".py", ".js", ".jsx"}
 
    for file in path.rglob("*"):
        if file.suffix not in supported:
            continue
        if "node_modules" in file.parts:
            continue
 
        try:
            source_code = file.read_text(encoding="utf-8", errors="ignore")
 
            if file.suffix == ".py":
                file_graph = get_python_call_graph(source_code, file.name)
            else:
                file_graph = get_js_call_graph(source_code, file.name)
 
            call_graph.update(file_graph)
            print(f"Call graph: {file.name} → {len(file_graph)} functions")
 
        except Exception as e:
            print(f"Skipping {file}: {e}")
 
    return call_graph
 
 
if __name__ == "__main__":
    from pprint import pprint
    graph = generate_call_graph("../../input_code")
    pprint(graph)