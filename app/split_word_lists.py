"""
Script to split a combined word list file into separate files by section.
Each section is identified by 'Title:' and 'Desc:' headers.
"""

import re
import subprocess
import sys
from pathlib import Path


def split_word_list(input_file, output_dir):
    """Split a combined word list file into individual files by section.
    
    Args:
        input_file (str): Path to the input file containing multiple word lists
        output_dir (str): Directory where output files will be saved
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(input_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    # Split on 'Title:' to separate each puzzle section
    sections = re.split(r"(?=Title:)", content)
    sections = [s.strip() for s in sections if s.strip()]

    if not sections:
        print("No valid sections found in the input file.")
        return []

    print(f"Found {len(sections)} word list sections to process")
    created_files = []

    for i, section in enumerate(sections, 1):
        lines = section.strip().split("\n")
        title = "Untitled"

        # Extract title
        for line in lines:
            if line.startswith("Title:"):
                title = line[6:].strip()
                break

        # Create a filename from the title
        sanitized_title = re.sub(r'[^\w\s-]', '', title.lower())
        sanitized_title = re.sub(r'[\s-]+', '_', sanitized_title).strip('_')
        filename = f"{sanitized_title}.txt"
        output_path = output_dir / filename

        # Ensure unique filename
        counter = 1
        while output_path.exists():
            filename = f"{sanitized_title}_{counter}.txt"
            output_path = output_dir / filename
            counter += 1

        # Write the section to a new file
        with open(output_path, "w") as f:
            f.write(section)

        created_files.append(str(output_path))
        print(f"Created file {i}/{len(sections)}: {filename}")

    return created_files

def main():
    """Main function to handle command line arguments and process the word list."""
    if len(sys.argv) != 2:
        print("Usage: python split_word_lists.py <input_file>")
        print("Example: python split_word_lists.py /path/to/word_lists.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    base_dir = Path(__file__).parent.parent
    uploads_dir = base_dir / "uploads"
    
    print(f"Splitting word lists from: {input_file}")
    print(f"Output directory: {uploads_dir}")
    
    created_files = split_word_list(input_file, uploads_dir)
    
    if created_files:
        print("\nAll word lists have been successfully separated into individual files.")
        print(f"Files are located in: {uploads_dir}")
        
        # Ask if user wants to generate PDFs
        if input("\nWould you like to generate PDFs for these word lists? (y/n): ").lower() == 'y':
            print("\nGenerating PDFs...")
            subprocess.run([sys.executable, "batch_generate_pdfs.py"], cwd=base_dir / "app")
    else:
        print("No files were created. Please check the input file format.")


if __name__ == "__main__":
    main()
