import ast
import tree_sitter_javascript as tsjs
import tree_sitter_python as tspy
from tree_sitter import Language, Parser
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from pathlib import Path

# Setup
model = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed", trust_remote_code=True)
MAX_TOKENS = 8192

# Tree-sitter parsers
JS_PARSER = Parser(Language(tsjs.language()))
PY_PARSER = Parser(Language(tspy.language()))

JS_CHUNK_TYPES = {
    "function_declaration",
    "arrow_function", 
    "method_definition",
    "class_declaration",
    "function_expression",
}

PY_CHUNK_TYPES = {
    "function_definition",
    "class_definition",
}

def chunk_with_treesitter(source_code: str, parser: Parser, chunk_types: set):
    tree = parser.parse(bytes(source_code, "utf-8"))
    chunks = []

    def walk(node):
        if node.type in chunk_types:
            chunk = source_code[node.start_byte:node.end_byte]
            token_count = len(tokenizer(chunk)["input_ids"])
            if token_count <= MAX_TOKENS:
                chunks.append({"code": chunk, "tokens": token_count})
            else:
                # Too large — recurse into children to get sub-chunks
                for child in node.children:
                    walk(child)
        else:
            for child in node.children:
                walk(child)

    walk(tree.root_node)
    return chunks

def chunk_file(filepath: str):
    source_code = Path(filepath).read_text()
    ext = Path(filepath).suffix

    if ext == ".py":
        return chunk_with_treesitter(source_code, PY_PARSER, PY_CHUNK_TYPES)
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        return chunk_with_treesitter(source_code, JS_PARSER, JS_CHUNK_TYPES)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def embed_file(filepath: str):
    chunks = chunk_file(filepath)
    if not chunks:
        print(f"No chunks found in {filepath}")
        return [], []

    codes = [c["code"] for c in chunks]
    embeddings = model.encode(codes)
    print(f"{filepath}: {len(codes)} chunks, embedding shape {embeddings.shape}")
    return codes, embeddings

# --- Usage ---
py_codes, py_embeddings = embed_file("myfile.py")
js_codes, js_embeddings = embed_file("myfile.js")