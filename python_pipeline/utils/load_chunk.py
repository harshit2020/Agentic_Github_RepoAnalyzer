from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from tree_sitter import Parser,Language
import tree_sitter_javascript
import tree_sitter_python
from pathlib import Path
from pprint import pprint

MAX_TOKENS = 8192
JS_PARSER = Parser(Language(tree_sitter_javascript.language()))
PY_PARSER = Parser(Language(tree_sitter_python.language()))
JS_CHUNK_TYPES = {
    "function_declaration",
    "arrow_function", 
    "method_definition",
    "class_declaration",
    "function_expression",
}
PY_CHUNK_TYPES = {
    "function_definition",
    "class_definition"
}

def chunk_function(source_code:str,chunk_types:set,tokenizer,parser:Parser,filename):
    try:
        tree_source_code = parser.parse(bytes(source_code,"utf-8"))
        chunks = []

        def walk(node):
            if node.type in chunk_types:
                chunk_node = source_code[node.start_byte:node.end_byte]
                tokens = tokenizer(chunk_node)
                token_count = len(tokens["input_ids"])
                if token_count <= MAX_TOKENS:
                    chunks.append({"code":chunk_node,"tokens":token_count,"filename":filename})
                else:
                    for child in node.children:
                        walk(child)
            else:
                for child in node.children:
                    walk(child)
        walk(tree_source_code.root_node)
        return chunks
    except Exception as e:
        raise RuntimeError(f"chunking failed!! {e}")
        

def load_source_code(path):
    try:
        loader = GenericLoader.from_filesystem(
            path,
            glob="**/*",
            suffixes=[".py",".js",".jsx"],
            parser = LanguageParser()
        )
        docs = loader.load()
        if not docs:
            raise ValueError(f"No documents found in {path}")
        else:
            return docs
    except Exception as e:
        raise RuntimeError(f"Document loading failed {e}")

def chunk_acc_file_type(path,tokenizer):
    docs = load_source_code(path)
    source_code_chunks = []
    for doc in docs:
        ext = Path(doc.metadata["source"]).suffix
        filename = Path(doc.metadata["source"]).name
        source_code = doc.page_content
        if ext == ".py":
            py_chunks = chunk_function(source_code,PY_CHUNK_TYPES,tokenizer,PY_PARSER,filename)
            source_code_chunks.extend(py_chunks)
        elif ext in {".js",".jsx"}:
            js_chunks = chunk_function(source_code,JS_CHUNK_TYPES,tokenizer,JS_PARSER,filename)
            source_code_chunks.extend(js_chunks)
        else:
            raise ValueError(f"Unsupported File type {ext}")
    return source_code_chunks


if __name__ == "__main__":

    path = "../input_code"
    tokenizer = AutoTokenizer.from_pretrained("nomic-ai/CodeRankEmbed",trust_remote_code=True)
    source_code_chunks = chunk_acc_file_type(path,tokenizer)
    # total_token_source_code = 0
    # for functions in source_code_chunks:
    #     total_token_source_code += functions["tokens"] 
    #     print(f" Tokens : {functions["tokens"]}")

    # print(f"The total source code token count is : {total_token_source_code}")
    print(source_code_chunks)