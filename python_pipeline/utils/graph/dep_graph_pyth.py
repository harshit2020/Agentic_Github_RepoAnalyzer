import ast
import sys
from pathlib import Path
from graphviz import Digraph

STDLIB_MODULES = sys.stdlib_module_names

COLORS = {
    "bg":      "#1e1e2e",
    "local":   "#89b4fa",
    "stdlib":  "#a6e3a1",
    "third":   "#f38ba8",
    "font":    "#cdd6f4",
}


def _get_python_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py"))


def _extract_imports(filepath: Path) -> list[tuple[str, str]]:
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"[WARN] Skipping {filepath}: {e}", file=sys.stderr)
        return []

    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                results.append((alias.name, "stdlib" if top in STDLIB_MODULES else "third"))
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                results.append(("." * node.level + (node.module or ""), "relative"))
            elif node.module:
                top = node.module.split(".")[0]
                results.append((node.module, "stdlib" if top in STDLIB_MODULES else "third"))
    return results


def build_dependency_graph(source_path: str, output_path: str = "dependency_graph") -> str:
    """
    Scan all .py files under source_path, build an import dependency
    graph, and save it as a PNG.

    Args:
        source_path: Root directory of the Python project to scan.
        output_path: Destination file path for the PNG (no extension needed).

    Returns:
        Absolute path to the generated PNG file.
    """
    root = Path(source_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    # Build raw graph: file -> [(module, kind), ...]
    graph: dict[str, list[tuple[str, str]]] = {}
    for filepath in _get_python_files(root):
        graph[str(filepath.relative_to(root))] = _extract_imports(filepath)

    # Graphviz diagram
    dot = Digraph(
        format="png",
        graph_attr={"bgcolor": COLORS["bg"], "rankdir": "LR", "splines": "curved",
                    "nodesep": "0.6", "ranksep": "1.2", "pad": "0.5", "fontname": "Courier New"},
        node_attr={"style": "filled,rounded", "shape": "box",
                   "fontname": "Courier New", "fontsize": "11", "margin": "0.3,0.15"},
        edge_attr={"arrowsize": "0.7", "penwidth": "1.2"},
    )

    # Project file nodes
    for file in graph:
        dot.node(file, label=file, fillcolor="#313244",
                 fontcolor=COLORS["local"], color=COLORS["local"], penwidth="1.8")

    # Dependency nodes + edges
    seen: set[str] = set()
    for source_file, imports in graph.items():
        for module, kind in imports:
            if kind == "relative":
                continue  # skip relative imports — they're internal
            color = COLORS["stdlib"] if kind == "stdlib" else COLORS["third"]
            if module not in seen:
                seen.add(module)
                dot.node(module, label=module,
                         fillcolor="#1e3a2f" if kind == "stdlib" else "#3a1e1e",
                         fontcolor=color, color=color, shape="ellipse")
            dot.edge(source_file, module, color=color)

    # Legend
    with dot.subgraph(name="cluster_legend") as leg:
        leg.attr(label="Legend", style="filled", fillcolor="#181825",
                 color="#585b70", fontcolor=COLORS["font"], fontname="Courier New", fontsize="11")
        leg.node("_proj",  "project file", shape="box",     style="filled,rounded",
                 fillcolor="#313244", fontcolor=COLORS["local"],  color=COLORS["local"])
        leg.node("_std",   "stdlib",       shape="ellipse", style="filled",
                 fillcolor="#1e3a2f", fontcolor=COLORS["stdlib"], color=COLORS["stdlib"])
        leg.node("_third", "third-party",  shape="ellipse", style="filled",
                 fillcolor="#3a1e1e", fontcolor=COLORS["third"],  color=COLORS["third"])

    result = dot.render(output_path, cleanup=True)
    print(f"Graph saved → {result}")
    return result


if __name__ == "__main__":
    build_dependency_graph("./input_code", output_path="my_graph")