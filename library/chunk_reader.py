from pathlib import Path
import csv


def read_file_content(file_path: Path, keep_tsv_names: bool = False) -> list[str]:
    """
    Read content from either txt or tsv file.
    For TSV files, extract only the dialogue (and name if present).
    """
    if file_path.suffix.lower() == '.txt':
        with file_path.open('r', encoding='utf-8') as f:
            return f.read().splitlines(keepends=False)

    elif file_path.suffix.lower() == '.tsv':
        dialogues = []
        with file_path.open('r', encoding='utf-8', newline='') as f:
            # First read the header to find the column indices
            reader = csv.reader(f, delimiter='\t')
            headers = next(reader)

            # Find the indices for Name and Dialogue columns
            dialogue_idx = -1
            name_idx = -1
            for idx, header in enumerate(headers):
                if header == 'Dialogue':
                    dialogue_idx = idx
                elif header == 'Name':
                    name_idx = idx

            if dialogue_idx == -1:
                raise ValueError(f"No 'Dialogue' column found in {file_path}")

            for row in reader:
                if not row:
                    continue
                if keep_tsv_names and name_idx != -1 and name_idx < len(row) and row[name_idx].strip():
                    dialogues.append(f"{row[name_idx]}: {row[dialogue_idx]}")
                else:
                    dialogues.append(row[dialogue_idx])
        return dialogues
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
