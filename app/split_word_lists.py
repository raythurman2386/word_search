"""
Script to split a combined word list file into separate files by section.
Each section is identified by 'Title:' and 'Desc:' headers.
"""

import os
import re
import time
from pathlib import Path


def main():
    """Split the sample_words.txt file into individual word list files."""
    base_dir = Path("/home/rthurman/code/word_search")
    uploads_dir = base_dir / "uploads"
    source_file = uploads_dir / "sample_words.txt"

    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    with open(source_file, "r") as f:
        content = f.read()

    sections = re.split(r"(?=Title:)", content)

    sections = [s.strip() for s in sections if s.strip()]

    print(f"Found {len(sections)} word list sections to process")

    for i, section in enumerate(sections, 1):
        lines = section.strip().split("\n")

        title = ""
        desc = ""

        for line in lines:
            if line.startswith("Title:"):
                title = line[6:].strip()
            elif line.startswith("Desc:"):
                desc = line[5:].strip()
                break

        sanitized_desc = re.sub(r"[^\w\-]", "_", desc.lower().replace(" ", "_"))
        timestamp = int(time.time())
        filename = f"{sanitized_desc}_{timestamp}.txt"
        output_path = uploads_dir / filename

        with open(output_path, "w") as f:
            f.write(section)

        print(f"Created file {i}/{len(sections)}: {filename}")

    print("\nAll word lists have been successfully separated into individual files.")
    print(f"Files are located in: {uploads_dir}")


if __name__ == "__main__":
    main()
