import os
from tree_sitter import Language

# Define language repos relative to the working directory in Docker
LANGUAGE_REPOS = {
    "python": "vendor/tree-sitter-python",
    "javascript": "vendor/tree-sitter-javascript",
    "php": "vendor/tree-sitter-php/php"
}

BUILD_PATH = 'build/my-languages.so'

if not os.path.exists('build'):
    os.makedirs('build')

if not os.path.exists(BUILD_PATH):
    Language.build_library(
        BUILD_PATH,
        list(LANGUAGE_REPOS.values())
    )
else:
    print(f"{BUILD_PATH} already exists, skipping build.")
