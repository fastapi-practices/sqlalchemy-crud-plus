import ast
import textwrap

from pathlib import Path

import pytest


def iter_python_code_blocks():
    docs_dir = Path(__file__).resolve().parents[1] / 'docs'
    for path in sorted(docs_dir.rglob('*.md')):
        in_block = False
        start_line = 0
        lines: list[str] = []

        for line_no, line in enumerate(path.read_text().splitlines(), 1):
            stripped = line.lstrip()
            if not in_block:
                if stripped.startswith('```') and stripped[3:].strip().lower().startswith('python'):
                    in_block = True
                    start_line = line_no
                    lines = []
                continue

            if stripped.startswith('```'):
                yield path, start_line, '\n'.join(lines)
                in_block = False
                continue

            lines.append(line)


def compile_doc_example(code: str):
    source = textwrap.dedent(code).strip()
    if not source:
        return

    try:
        ast.parse(source)
    except SyntaxError:
        wrapped = 'async def __doc_example__():\n' + textwrap.indent(source, '    ') + '\n'
        ast.parse(wrapped)


def test_all_python_doc_examples_have_valid_syntax():
    checked = 0
    for path, start_line, code in iter_python_code_blocks():
        try:
            compile_doc_example(code)
        except SyntaxError as exc:
            raise AssertionError(f'Invalid Python example in {path}:{start_line}: {exc}') from exc
        checked += 1

    assert checked > 0


def test_compile_doc_example_skips_empty_code():
    compile_doc_example('')


def test_compile_doc_example_wraps_top_level_await():
    compile_doc_example('await run_example()')


def test_doc_example_failure_message_includes_location(monkeypatch: pytest.MonkeyPatch):
    def invalid_blocks():
        yield Path('docs/example.md'), 10, 'if'

    monkeypatch.setattr('tests.test_docs_examples.iter_python_code_blocks', invalid_blocks)

    with pytest.raises(AssertionError, match='docs/example.md:10'):
        test_all_python_doc_examples_have_valid_syntax()
