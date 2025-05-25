import os
from tree_sitter import Language, Parser

# Cloned Repos
LANGUAGE_REPOS = {
    "python": "vendor/tree-sitter-python",
    "javascript": "vendor/tree-sitter-javascript",
    "php": "vendor/tree-sitter-php/php"
}

BUILD_PATH = 'build/my-languages.so'

# Build the Tree-sitter language library
if not os.path.exists(BUILD_PATH):
    Language.build_library(
        BUILD_PATH,
        list(LANGUAGE_REPOS.values())
    )

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

    def is_function_node(node):
        if language_id == "python":
            return node.type == "function_definition"
        elif language_id == "javascript":
            return node.type in ("function_declaration", "method_definition", "arrow_function")
        elif language_id == "php":
            return node.type in ("function_definition", "method_declaration")
        return False

    def get_name(node):
        # Common child types that store function/method names
        name_types = {"name", "identifier", "property_identifier"}
        for child in node.children:
            if child.type in name_types:
                return code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
        return None


    def extract_with_cursor(cursor):
        node = cursor.node
        if is_function_node(node):
            func_code = code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
            name = get_name(node)
            functions.append({
                "type": node.type,
                "name": name,
                "code": func_code,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1
            })

        if cursor.goto_first_child():
            extract_with_cursor(cursor)
            while cursor.goto_next_sibling():
                extract_with_cursor(cursor)
            cursor.goto_parent()

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

##### TEST #####

php_code = b"""
<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class AnswersTest extends TestCase
{
    use RefreshDatabase;

    /**
     * FT-AE1
     * Test for creating an answer with valid payload
     */
    public function test_create_answer_with_valid_playload(): void
    {
        $answer_payload = [
            "answer" => "Test answer1"
        ];

        $request = $this->json('post', '/api/answers', $answer_payload);
        $request->assertStatus(200);
        $this->assertDatabaseHas('answers', $answer_payload);
        $this->assertDatabaseCount('answers', 1);
    }

    /**
     * FT-AE2
     * Test for creating an answer with invalid payload
     */
    public function test_create_answer_with_invalid_payload(): void
    {
        // the post answer request reqires a 'answer' key to be not null.
        $malformed_answer_payload = [
            "bad_payload"=>"bad"
            // is missing answers field
        ];

        $request = $this->json('post', '/api/answers', $malformed_answer_payload);
        $request->assertStatus(422);
        $this->assertDatabaseCount('answers', 0);
    }
}
"""

functions = extract_functions_from_code(php_code, "php")
print(functions)

print("---------------------------------")
js_code = b"""
function add(a, b) {
  return a + b;
}

const subtract = (a, b) => {
  return a - b;
};

class Calculator {
  multiply(a, b) {
    return a * b;
  }
}
"""

functions = extract_functions_from_code(js_code, "javascript")
print(functions)