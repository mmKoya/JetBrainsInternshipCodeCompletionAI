import os
import random
from CodeParser import extract_code_blocks, find_function_calls_with_args, strip_comments, strip_empty_lines, find_assignments, find_conditions
import json
from typing import List, Tuple, Callable, Any


class TextUtils:
    @staticmethod
    def split_indentation(line: str) -> Tuple[str, str]:
        """Separate leading whitespace (indentation) from the rest of the line."""
        indentation_length = len(line) - len(line.lstrip())
        indentation = line[:indentation_length]
        code_text = line[indentation_length:]
        return indentation, code_text

    @staticmethod
    def extract_function_call_details(lines: List[str], function_call: dict) -> Tuple[str, str, str]:
        """Extract the components of a function call: prefix, arguments, and suffix."""
        current_line, start_idx, end_idx = (
            function_call['end_line'] - 1,
            function_call['end_col_offset'] - 2,
            function_call['end_col_offset'] - 1,
        )
        parentheses_balance = 1

        while parentheses_balance:
            char = lines[current_line][start_idx]
            parentheses_balance += 1 if char == ')' else -1 if char == '(' else 0
            start_idx -= 1
            if start_idx < 0:
                current_line -= 1
                start_idx = len(lines[current_line]) - 1

        prefix = '\n'.join(lines[function_call['start_line'] - 1:current_line] + [lines[current_line][:start_idx + 2]])
        arguments = ', '.join(function_call['arguments'])
        suffix = lines[function_call['end_line'] - 1][end_idx:]
        return prefix, arguments, suffix

    @staticmethod
    def random_split_middle_examples(examples: List[Tuple[str, str, str]], min_left: int = 5, min_right: int = 5) -> List[Tuple[str, str, str]]:
        """Randomly split the middle section of examples with specific constraints."""
        new_examples = []
        for example in examples:
            prefix, middle, suffix = example
            if len(middle) < min_left + min_right:
                continue
            while True:
                split_idx = random.randint(min_left, min_left + (len(middle) - min_right - min_left) // 2 + 1)
                if middle[split_idx - 1:split_idx + 1] != r'\n':
                    break

            prefix += middle[:split_idx]
            middle = middle[split_idx:]
            new_examples.append((prefix, middle, suffix))
        return new_examples


class CodeSegmentExtractor:
    @staticmethod
    def extract_lines(block: str, middle_line_count: int = 1, min_context_lines: int = 1, max_context_lines: int = -1) -> List[Tuple[str, str, str]]:
        """Generate examples by extracting specified middle lines with configurable context lines."""
        lines = block.splitlines()
        num_lines = len(lines)
        if num_lines < 2 * min_context_lines + middle_line_count:
            return []

        examples = []
        for middle_start in range(min_context_lines, num_lines - min_context_lines - middle_line_count):
            middle_end = middle_start + middle_line_count
            start_prefix = max(0, middle_start - (max_context_lines if max_context_lines >= 0 else middle_start))
            end_suffix = min(num_lines, middle_end + (max_context_lines if max_context_lines >= 0 else num_lines))

            indentation, middle_text = TextUtils.split_indentation('\n'.join(lines[middle_start:middle_end]))
            prefix = '\n'.join(lines[start_prefix:middle_start]) + '\n' + indentation
            suffix = '\n' + '\n'.join(lines[middle_end:end_suffix])

            examples.append((prefix, middle_text, suffix))
        return examples

    @staticmethod
    def extract_function_arguments(block: str, max_arguments: int = 5, min_context_lines: int = 1, max_context_lines: int = -1) -> List[Tuple[str, str, str]]:
        """Extract function arguments with specified context and argument count limitations."""
        function_calls = find_function_calls_with_args(block)
        lines = block.splitlines()
        num_lines = len(lines)

        examples = []
        for call in function_calls:
            if len(call['arguments']) > max_arguments > 0:
                continue
            if call['start_line'] - 1 < min_context_lines or num_lines - call['end_line'] < min_context_lines:
                continue

            prefix, middle, suffix = TextUtils.extract_function_call_details(lines, call)
            if not middle:
                continue

            start = max(0, call['start_line'] - 1 - (max_context_lines if max_context_lines >= 0 else call['start_line'] - 1))
            end = min(num_lines, call['end_line'] + (max_context_lines if max_context_lines >= 0 else num_lines))

            prefix = '\n'.join(lines[start:call['start_line'] - 1] + [prefix])
            suffix = '\n'.join([suffix] + lines[call['end_line']:end])
            examples.append((prefix, middle, suffix))

        return examples

    @staticmethod
    def extract_section(lines: List[str], start_pos: (int, int), end_pos: (int, int), max_characters: int = -1,
                        min_context_lines: int = 1, max_context_lines: int = -1) -> Tuple[str, str, str]:

        num_lines = len(lines)
        start_line, start_idx = start_pos[0] - 1, start_pos[1]
        end_line, end_idx = end_pos[0] - 1, end_pos[1]

        if start_line < min_context_lines or num_lines - end_line - 1 < min_context_lines:
            return None

        middle_text = (
            lines[start_line][start_idx:end_idx] if start_line == end_line
            else '\n'.join(
                [lines[start_line][start_idx:]] + lines[start_line + 1:end_line] + [lines[end_line][:end_idx]]
            )
        )
        if 0 < max_characters < len(middle_text):
            return None

        start = max(0, start_line - (max_context_lines if max_context_lines >= 0 else start_line))
        end = min(num_lines, end_line + 1 + (max_context_lines if max_context_lines >= 0 else num_lines))

        prefix = '\n'.join(lines[start:start_line] + [lines[start_line][:start_idx]])
        suffix = '\n'.join([lines[end_line][end_idx:]] + lines[end_line + 1:end])

        return prefix, middle_text, suffix

    @staticmethod
    def extract_assignment_sections(block: str, max_characters: int = 100, min_context_lines: int = 1, max_context_lines: int = -1) -> List[Tuple[str, str, str]]:
        """Extract assignment sections with character limit and surrounding context."""
        assignments = find_assignments(block)
        lines = block.splitlines()

        examples = []
        for start_pos, end_pos in assignments:
            result = CodeSegmentExtractor.extract_section(lines, start_pos, end_pos, max_characters, min_context_lines, max_context_lines)
            if result:
                examples.append(result)

        return examples

    @staticmethod
    def extract_condition_sections(block: str, max_characters: int = 100, min_context_lines: int = 1, max_context_lines: int = -1) -> List[Tuple[str, str, str]]:
        """Extract condition sections with character limit and surrounding context."""
        conditions = find_conditions(block)
        lines = block.splitlines()

        examples = []
        for start_pos, end_pos in conditions:
            result = CodeSegmentExtractor.extract_section(lines, start_pos, end_pos, max_characters, min_context_lines, max_context_lines)
            if result:
                examples.append(result)

        return examples


class DatasetBuilder:

    @staticmethod
    def extract_datasets(
        code_blocks: List[str],
        max_values: List[int],
        max_context_lines: List[int],
        dataset_type: str,
        extract_method: Callable[[str, Any, Any], List[Tuple[str, str, str]]]
    ) -> List[Tuple[str, List[Tuple[str, str, str]]]]:
        datasets = []
        for max_value in max_values:
            for max_context in max_context_lines:
                dataset_name = f'{dataset_type}_{max_value}_{max_context}'
                examples = []
                for block in code_blocks:
                    examples.extend(extract_method(block, max_value, max_context))

                if examples:
                    datasets.append((dataset_name, examples))

                    random_split_name = f'random_split_{dataset_type}_{max_value}_{max_context}'
                    examples_split = TextUtils.random_split_middle_examples(examples, min_left=5, min_right=5)
                    if examples_split:
                        datasets.append((random_split_name, examples_split))

        return datasets

    @staticmethod
    def extract_assignments_datasets(code_blocks: List[str], max_characters: List[int], max_context_lines: List[int]) -> List[Tuple[str, List[Tuple[str, str, str]]]]:
        return DatasetBuilder.extract_datasets(
            code_blocks,
            max_characters,
            max_context_lines,
            'assignments',
            lambda block, max_c, max_pf: CodeSegmentExtractor.extract_assignment_sections(block, max_characters=max_c, max_context_lines=max_pf),
        )

    @staticmethod
    def extract_arguments_datasets(code_blocks: List[str], max_arguments: List[int], max_context_lines: List[int]) -> List[Tuple[str, List[Tuple[str, str, str]]]]:
        return DatasetBuilder.extract_datasets(
            code_blocks,
            max_arguments,
            max_context_lines,
            'arguments',
            lambda block, max_args, max_pf: CodeSegmentExtractor.extract_function_arguments(block, max_arguments=max_args, max_context_lines=max_pf),
        )

    @staticmethod
    def extract_lines_datasets(code_blocks: List[str], num_lines: List[int], max_context_lines: List[int]) -> List[Tuple[str, List[Tuple[str, str, str]]]]:
        return DatasetBuilder.extract_datasets(
            code_blocks,
            num_lines,
            max_context_lines,
            'lines',
            lambda block, num_l, max_pf: CodeSegmentExtractor.extract_lines(block, middle_line_count=num_l, max_context_lines=max_pf),
        )

    @staticmethod
    def extract_conditions_datasets(code_blocks: List[str], max_characters: List[int], max_context_lines: List[int]) -> List[Tuple[str, List[Tuple[str, str, str]]]]:
        return DatasetBuilder.extract_datasets(
            code_blocks,
            max_characters,
            max_context_lines,
            'conditions',
            lambda block, max_c, max_pf: CodeSegmentExtractor.extract_condition_sections(block, max_characters=max_c, max_context_lines=max_pf),
        )


if __name__ == '__main__':
    repo_paths = ["RandomScripts", os.getcwd()]

    function_blocks = []
    class_blocks = []
    source_codes = []

    for repo_path in repo_paths:
        files = [f for f in os.listdir(repo_path) if f.endswith('.py')]

        for file in files:
            file_path = os.path.join(repo_path, file)

            with open(file_path, 'r') as file:
                source_code = file.read()
                clean_code = strip_comments(source_code)
                tight_code = strip_empty_lines(clean_code)

            functions, classes = extract_code_blocks(tight_code)

            function_blocks.extend(functions)
            class_blocks.extend(classes)
            source_codes.append(tight_code)

    function_datasets = []
    class_datasets = []
    # source_code_datasets = []

    function_datasets.extend(DatasetBuilder.extract_assignments_datasets(function_blocks, [-1], [3, -1]))
    function_datasets.extend(DatasetBuilder.extract_conditions_datasets(function_blocks, [-1], [3, -1]))
    function_datasets.extend(DatasetBuilder.extract_arguments_datasets(function_blocks, [-1], [-1]))
    function_datasets.extend(DatasetBuilder.extract_lines_datasets(function_blocks, [3], [-1]))

    class_datasets.extend(DatasetBuilder.extract_lines_datasets(class_blocks, [5], [-1]))

    # function_datasets.extend(DatasetBuilder.extract_assignments_datasets(function_blocks, [60, 120, -1], [3, 5, -1]))
    # function_datasets.extend(DatasetBuilder.extract_conditions_datasets(function_blocks, [60, 120, -1], [3, 5, -1]))
    # function_datasets.extend(DatasetBuilder.extract_arguments_datasets(function_blocks, [1, 3, -1], [3, 5, -1]))
    # function_datasets.extend(DatasetBuilder.extract_lines_datasets(function_blocks, [1, 2, 3], [3, 5, -1]))

    # class_datasets.extend(DatasetBuilder.extract_assignments_datasets(class_blocks, [60, 120, -1], [3, 5, -1]))
    # class_datasets.extend(DatasetBuilder.extract_conditions_datasets(class_blocks, [60, 120, -1], [3, 5, -1]))
    # class_datasets.extend(DatasetBuilder.extract_arguments_datasets(class_blocks, [1, 3, -1], [3, 5, -1]))
    # class_datasets.extend(DatasetBuilder.extract_lines_datasets(class_blocks, [1, 2, 3], [3, 5, -1]))

    # source_code_datasets.extend(DatasetBuilder.extract_assignments_datasets(source_codes, [60, 120, -1], [3, 5, 20]))
    # source_code_datasets.extend(DatasetBuilder.extract_conditions_datasets(source_codes, [60, 120, -1], [3, 5, -1]))
    # source_code_datasets.extend(DatasetBuilder.extract_arguments_datasets(source_codes, [1, 3, -1], [3, 5, 20]))
    # source_code_datasets.extend(DatasetBuilder.extract_lines_datasets(source_codes, [1, 2, 3], [3, 5, 20]))

    output_dir = 'Datasets/'
    for dataset in function_datasets:
        print(len(dataset[1]))
    for dataset in class_datasets:
        print(len(dataset[1]))

    for dataset in function_datasets:
        with open(f'{output_dir}functions_{dataset[0]}.json', 'w') as file:
            json.dump(dataset[1], file, indent=4)

    for dataset in class_datasets:
        with open(f'{output_dir}class_{dataset[0]}.json', 'w') as file:
            json.dump(dataset[1], file, indent=4)

