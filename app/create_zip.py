"""
Create a zip archive of all word search PDFs for easy sharing.
"""

import datetime
import zipfile
from pathlib import Path


def main():
    """Create a zip file containing all word search PDFs in the downloads directory."""
    base_dir = Path("/home/rthurman/code/word_search")
    downloads_dir = base_dir / "downloads"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"word_searches_{timestamp}.zip"
    zip_path = base_dir / zip_filename

    exclude_files = [".gitkeep"]

    pdf_files = []
    total_size = 0

    for file in downloads_dir.glob("*.pdf"):
        if file.name not in exclude_files:
            pdf_files.append(file)
            total_size += file.stat().st_size

    total_size_mb = total_size / (1024 * 1024)

    if not pdf_files:
        print("No PDF files found in the downloads directory.")
        return

    print(f"Found {len(pdf_files)} PDF files (total size: {total_size_mb:.2f} MB)")
    print(f"Creating zip archive: {zip_filename}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in pdf_files:
            zipf.write(file, arcname=file.name)
            print(f"Added: {file.name}")

    zip_size = zip_path.stat().st_size / (1024 * 1024)
    compression_ratio = (1 - (zip_size / total_size_mb)) * 100

    print("\nZip creation complete!")
    print(f"Zip file size: {zip_size:.2f} MB")
    print(f"Compression ratio: {compression_ratio:.1f}%")
    print(f"Zip file location: {zip_path}")


if __name__ == "__main__":
    main()
