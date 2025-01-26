from dataclasses import dataclass
from pathlib import Path
from typing import List
import fugashi

from library.database_interface import DATABASE_ROOT, get_db_connection, get_source_locations_for_baseform, get_baseform


@dataclass
class Example:
    filename: str
    line_number: int
    sentences: List[str]
    example_line: int


def get_examples_for_word(
        word: str,
        db_path: str
) -> List[Example]:
    """
    Retrieves example sentences for a given Japanese word from the database.

    Args:
        word: The Japanese word/phrase to search for.
        db_path: Path to the SQLite database file.

    Returns:
        A list of Example objects, each containing context sentences and location info.
    """
    conn = get_db_connection(db_path)
    tagger = fugashi.Tagger('-Owakati')
    base_form = get_baseform(tagger, word)
    source_locations = get_source_locations_for_baseform(conn, base_form)
    conn.close()

    examples: List[Example] = []
    for location in source_locations:
        file_path = location.filename
        if not Path(file_path).exists():
            print(f"Warning: File not found: {file_path}. Skipping.")
            continue

        sentences, example_line_index = _extract_context_sentences(Path(file_path), location.line_number)
        if sentences:
            examples.append(Example(
                filename=location.filename,
                line_number=location.line_number,
                sentences=sentences,
                example_line=example_line_index
            ))
    return examples


def _extract_context_sentences(
        file_path: Path,
        line_number: int,
        context_lines_before: int = 2,
        context_lines_after: int = 2
) -> tuple[List[str], int]:
    """
    Extracts context sentences around a specific line number from a file.

    Args:
        file_path: Path to the text file.
        line_number: The line number of interest (0-indexed as stored in db, but file reading is 1-indexed so adjust
                     inside).
        context_lines_before: Number of lines to include before the target line.
        context_lines_after: Number of lines to include after the target line.

    Returns:
        A tuple containing:
            - A list of sentences (strings) representing the context.
            - The index of the target line within the returned list.
        Returns ([], -1) if the file reading or line extraction fails.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()

            if str(file_path).endswith(".tsv"):
                all_lines = all_lines[1:]

            target_line_index_file_indexed = line_number
            start_index = max(0, target_line_index_file_indexed - context_lines_before)
            end_index = min(len(all_lines), target_line_index_file_indexed + context_lines_after + 1)

            sentences = [line.strip() for line in all_lines[start_index:end_index]]
            example_line_index = target_line_index_file_indexed - start_index

            if not (0 <= example_line_index < len(sentences)):
                return [], -1

            return sentences, example_line_index

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return [], -1
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return [], -1


if __name__ == '__main__':
    def test():
        test_word = "言葉"
        examples = get_examples_for_word(test_word, DATABASE_ROOT)

        if examples:
            print(f"Found {len(examples)} examples for '{test_word}':")
            for example in examples:
                print(f"\nFile: {example.filename}, Line: {example.line_number} (file line number, 1-indexed)")
                for i, sentence in enumerate(example.sentences):
                    if i == example.example_line:
                        print(f"  > {sentence}")
                    else:
                        print(f"    {sentence}")
        else:
            print(f"No examples found for '{test_word}'.")
    test()
