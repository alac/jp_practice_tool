from pathlib import Path
import csv
import fugashi
import random
import sqlite3

from library.chunk_reader import read_file_content
from library.database_interface import (DATABASE_ROOT, add_baseform_appearances, add_kanji_appearances, add_source_file,
                                        initialize_database, get_db_connection, get_source_file_id)


def chunk_txt_file(input_file: Path, output_dir: Path, chunk_size: int) -> None:
    """Process a text file by splitting it into chunks."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = input_file.stem

    with input_file.open('r', encoding='utf-8') as f:
        lines_seen = 0
        while True:
            lines = []
            first_line_in_chunk = lines_seen
            for _ in range(chunk_size):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
                lines_seen += 1

            if not lines:
                break

            chunk_file = output_dir / f"{base_name}.{first_line_in_chunk:06d}.txt"
            with chunk_file.open('w', encoding='utf-8') as out_f:
                out_f.writelines(lines)


def chunk_tsv_file(input_file: Path, output_dir: Path, chunk_size: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = input_file.stem

    with input_file.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames

        if 'Dialogue' not in headers:
            raise ValueError(f"TSV file {input_file} must contain a 'Dialogue' column")

        lines_seen = 0
        first_line_in_chunk = 0
        chunk_lines = []
        output_headers = ['Name', 'Dialogue'] if 'Name' in headers else ['Dialogue']

        for row in reader:
            output_row = {h: row.get(h, '') for h in output_headers}
            chunk_lines.append(output_row)
            lines_seen += 1

            if len(chunk_lines) >= chunk_size:
                chunk_file = output_dir / f"{base_name}.{first_line_in_chunk:06d}.tsv"
                with chunk_file.open('w', encoding='utf-8', newline='') as out_f:
                    writer = csv.DictWriter(out_f, fieldnames=output_headers, delimiter='\t')
                    writer.writeheader()
                    writer.writerows(chunk_lines)
                first_line_in_chunk = lines_seen
                chunk_lines = []

        if chunk_lines:
            chunk_file = output_dir / f"{base_name}.{first_line_in_chunk:06d}.tsv"
            with chunk_file.open('w', encoding='utf-8', newline='') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=output_headers, delimiter='\t')
                writer.writeheader()
                writer.writerows(chunk_lines)


def chunk_data(raw_data_root: str, chunks_root: str, chunk_size: int = 100) -> None:
    raw_data_root = Path(raw_data_root)
    chunks_root = Path(chunks_root)

    chunks_root.mkdir(parents=True, exist_ok=True)

    for input_file in raw_data_root.glob('*.*'):
        if not input_file.is_file():
            continue

        output_dir = chunks_root / input_file.stem
        if output_dir.exists():
            continue

        if input_file.suffix.lower() == '.tsv':
            chunk_tsv_file(input_file, output_dir, chunk_size)
        elif input_file.suffix.lower() == '.txt':
            chunk_txt_file(input_file, output_dir, chunk_size)


def process_chunk(conn: sqlite3.Connection, text: str, filename: str, tagger: fugashi.Tagger) -> None:
    try:
        sourcefile_id = add_source_file(conn, filename)
        lines = text.splitlines()
        for line_idx, line in enumerate(lines, start=0):
            if not line.strip():
                continue

            kanji_set = set()
            baseform_set = set()

            for word in tagger(line):
                for char in word.surface:
                    if '\u4e00' <= char <= '\u9fff':
                        kanji_set.add(char)
                if word.feature.lemma:
                    baseform_set.add(word.feature.lemma)

            if kanji_set:
                add_kanji_appearances(
                    conn,
                    list(kanji_set),
                    sourcefile_id,
                    line_idx,
                    max_appearances=50
                )

            if baseform_set:
                add_baseform_appearances(
                    conn,
                    list(baseform_set),
                    sourcefile_id,
                    line_idx,
                    max_appearances=50
                )

    except Exception as e:
        print(f"Processing error in {filename}: {e}")
        raise


def should_keep_word(word: fugashi.UnidicNode) -> bool:
    pos1 = word.feature.pos1
    pos2 = word.feature.pos2

    skip_pos1 = {
        '助詞',  # Particles
        '助動詞',  # Auxiliary verbs
        '記号',  # Symbols
        '接続詞',  # Conjunctions
        '感動詞',  # Interjections
    }

    skip_pos2 = {
        '接尾辞',  # Suffixes
        '助数詞',  # Counter words
    }

    skip_if_noun = {
        '代名詞',  # Pronouns
        '数詞',  # Numerical nouns
    }

    if pos1 in skip_pos1:
        return False

    if pos2 in skip_pos2:
        return False

    if pos1 == '名詞' and pos2 in skip_if_noun:
        return False

    return True


def process_all_chunks(db_root_str: str, chunks_root: str) -> None:
    db_root = Path(db_root_str)
    chunks_root = Path(chunks_root)
    if not db_root.parent.exists():
        db_root.parent.mkdir(parents=True, exist_ok=True)

    initialize_database(db_root_str)
    connection = get_db_connection(db_root_str)
    tagger = fugashi.Tagger('-Owakati')

    try:
        file_queue = []
        for folder in chunks_root.iterdir():
            if not folder.is_dir():
                continue
            for file in folder.iterdir():
                if not file.is_file():
                    continue
                if get_source_file_id(connection, str(file)) != -1:
                    print(f"Skipping already processed file: {file}")
                    continue
                file_queue.append(file)
        random.shuffle(file_queue)

        for file in file_queue:
            try:
                text = "\n".join(read_file_content(file))
                print(f"Processing file: {file}")
                process_chunk(connection, text, str(file), tagger)
                connection.commit()
            except Exception as e:
                print(f"Error processing file {file}: {str(e)}")
                connection.rollback()

    finally:
        connection.close()


if __name__ == "__main__":
    RAW_ROOT = r'data\raw'
    CHUNK_ROOT = r'data\chunk'
    chunk_data(RAW_ROOT, CHUNK_ROOT)
    process_all_chunks(DATABASE_ROOT, CHUNK_ROOT)
