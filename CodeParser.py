import os
import ast
import re


def strip_comments(code):
    # Patterns for strings and comments
    string_pattern = r"(\"\"\".*?\"\"\"|'''.*?'''|\".*?\"|'.*?'|r\".*?\"|r'.*?')"
    comment_pattern = r"#.*(?=\n|$)"

    # Dictionary to store unique placeholders for each string
    strings = {}
    def string_replacer(match):
        placeholder = f"{{{{STR_{len(strings)}}}}}"
        strings[placeholder] = match.group(0)
        return placeholder

    # Replace all strings with placeholders
    code_without_strings = re.sub(string_pattern, string_replacer, code, flags=re.DOTALL)

    # Remove comments
    code_without_comments = re.sub(comment_pattern, "", code_without_strings)

    # Restore the strings from placeholders
    for placeholder, original in strings.items():
        code_without_comments = code_without_comments.replace(placeholder, original)

    return code_without_comments


def strip_empty_lines(code):
    lines = code.splitlines()

    stripped_lines = [line for line in lines if line.strip()]

    stripped_code = '\n'.join(stripped_lines)

    return stripped_code


class CodeExtractor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.classes = []

    def visit_FunctionDef(self, node):
        function_source = ast.get_source_segment(self.code, node)
        self.functions.append(function_source)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_source = ast.get_source_segment(self.code, node)
        self.classes.append(class_source)

        self.generic_visit(node)

    def extract_from_code(self, code):
        self.code = code
        tree = ast.parse(self.code)
        self.visit(tree)


def extract_code_blocks(code):
    extractor = CodeExtractor()
    extractor.extract_from_code(code)
    return extractor.functions, extractor.classes


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.function_calls = []

    def visit_Call(self, node):
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            func_name = ".".join(parts)

        args = [ast.get_source_segment(self.source_code, arg) for arg in node.args]
        if func_name:
            self.function_calls.append({
                "function": func_name,
                "arguments": args,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "col_offset": node.col_offset,
                "end_col_offset": node.end_col_offset
            })

        self.generic_visit(node)


def find_function_calls_with_args(source_code):
    tree = ast.parse(source_code)

    visitor = FunctionCallVisitor(source_code)
    visitor.visit(tree)

    return visitor.function_calls


class AssignmentVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assignments = []

    def visit_Assign(self, node):
        self.collect_assignment_info(node)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.collect_assignment_info(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.collect_assignment_info(node)
        self.generic_visit(node)

    def collect_assignment_info(self, node):
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AugAssign):
            targets = [node.target]
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            return

        start_line = node.lineno
        end_line = node.end_lineno
        end_col = node.end_col_offset

        start_col = value.col_offset if hasattr(value, 'col_offset') else 0

        for _ in targets:
            assignment_info = {
                'start_line': start_line,
                'start_col': start_col,
                'end_line': end_line,
                'end_col': end_col,
            }
            self.assignments.append(assignment_info)


def find_assignments(code):
    tree = ast.parse(code)
    visitor = AssignmentVisitor()
    visitor.visit(tree)
    assignments_positions = []
    for assignment in visitor.assignments:
        assignments_positions.append(((assignment['start_line'], assignment['start_col']), (assignment['end_line'], assignment['end_col'])))
    return list(set(assignments_positions))


def find_conditions(code):
    tree = ast.parse(code)
    conditions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While)):
            start_line = node.test.lineno
            start_col = node.test.col_offset
            end_line = node.test.end_lineno
            end_col = node.test.end_col_offset
            conditions.append(((start_line, start_col), (end_line, end_col)))

        elif isinstance(node, ast.Assert):
            start_line = node.test.lineno
            start_col = node.test.col_offset
            end_line = node.test.end_lineno
            end_col = node.test.end_col_offset
            conditions.append(((start_line, start_col), (end_line, end_col)))

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.IfExp):
            start_line = node.value.test.lineno
            start_col = node.value.test.col_offset
            end_line = node.value.test.end_lineno
            end_col = node.value.test.end_col_offset
            conditions.append(((start_line, start_col), (end_line, end_col)))

    return conditions


if __name__ == '__main__':
    repo_path = os.getcwd()
    files = [f for f in os.listdir(repo_path) if f.endswith('.py')]
    file_path = os.path.join(repo_path, files[0])

    with open(file_path, 'r') as file:
        source_code = file.read()
        clean_code = strip_comments(source_code)
        print(clean_code)
