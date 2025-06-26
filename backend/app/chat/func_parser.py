import os
from tree_sitter import Language, Parser

import pkg_resources

try:
    version = pkg_resources.get_distribution("tree-sitter").version
    print("tree-sitter version:", version)
except pkg_resources.DistributionNotFound:
    print("tree-sitter not found")

LANGUAGE_REPOS = {
    "python": "../vendor/tree-sitter-python",
    "javascript": "../vendor/tree-sitter-javascript",
    "php": "../vendor/tree-sitter-php/php"
}

BUILD_PATH = '../build/my-languages.so' # ../build/my-languages.so when running local


LANGUAGES = {lang: Language(BUILD_PATH, lang) for lang in LANGUAGE_REPOS}

EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".php": "php"
}

def extract_functions_from_code(code: bytes, language_id: str):
    language = LANGUAGES[language_id]
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(code)
    root = tree.root_node

    functions = []
    all_comments = []

    def is_function_node(node):
        if language_id == "python":
            return node.type == "function_definition"
        elif language_id == "javascript":
            return node.type in ("function_declaration", "method_definition", "arrow_function")
        elif language_id == "php":
            return node.type in ("function_definition", "method_declaration")
        return False

    def get_name(node):
        name_types = {"name", "identifier", "property_identifier"}
        for child in node.children:
            if child.type in name_types:
                return code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
        return None

    def collect_comments(node):
        comments = []
        if node.type == "comment":
            comments.append(node)
        for child in node.children:
            comments.extend(collect_comments(child))
        return comments

    def extract_with_cursor(cursor):
        node = cursor.node
        if is_function_node(node):
            func_code = code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
            name = get_name(node)

            # Comments within the function
            inner_comments = [
                code[c.start_byte:c.end_byte].decode("utf-8", errors="ignore")
                for c in all_comments
                if node.start_byte <= c.start_byte < node.end_byte
            ]

            # Comments directly above the function (up to 2 lines above)
            leading_comments = [
                code[c.start_byte:c.end_byte].decode("utf-8", errors="ignore")
                for c in all_comments
                if c.end_byte <= node.start_byte and (0 <= node.start_point[0] - c.end_point[0] <= 2)
            ]

            merged_comment = "\n".join(leading_comments + inner_comments).strip()

            functions.append({
                "type": node.type,
                "name": name,
                "code": func_code,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "comment": merged_comment
            })

        if cursor.goto_first_child():
            extract_with_cursor(cursor)
            while cursor.goto_next_sibling():
                extract_with_cursor(cursor)
            cursor.goto_parent()

    all_comments = collect_comments(root)

    cursor = root.walk()
    extract_with_cursor(cursor)

    return functions


def parse_directory_for_functions(path: str):
    all_functions = []
    for root, dirs, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[-1]
            if ext in EXTENSION_MAP:
                language_id = EXTENSION_MAP[ext]
                full_path = os.path.join(root, file)
                with open(full_path, "rb") as f:
                    code = f.read()
                functions = extract_functions_from_code(code, language_id)
                for func in functions:
                    func["file"] = full_path
                    func["language"] = language_id
                all_functions.extend(functions)
    return all_functions

def question_needs_code_body(question: str) -> bool:
    keywords = [
        "how does", "what does", "show the logic", "assert", "check", 
        "verify", "does it validate", "explain", "implementation", "details"
    ]

    question_lower = question.lower()
    return any(kw in question_lower for kw in keywords)

def preprocess_functions(parsed_functions, question):
    if parsed_functions == "USER HASNT UPLOADED CODE YET":
        return parsed_functions

    #include_code = question_needs_code_body(question)
    include_code = False
    clean = []


    for item in parsed_functions:
        cleaned_item = {
            "file": item["file"].split("/")[-1],
            "function_name": item["name"],
            "type": "test" if "test" in item["file"].lower() else "function",
            "language": item.get("language", "unknown")
        }

        if include_code:
            cleaned_item["code"] = item["code"]

        clean.append(cleaned_item)

    return clean