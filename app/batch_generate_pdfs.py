#!/usr/bin/env python3
"""
Batch processor for word search lists.
This script automatically generates PDFs for all word list files in the uploads directory.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import concurrent.futures

# Number of processes to run in parallel (adjust as needed)
MAX_CONCURRENT_PROCESSES = 4

def generate_pdf_for_file(word_file_path, grid_size=15):
    """Generate a word search PDF for a given word list file.
    
    Args:
        word_file_path: Path to the word list file
        grid_size: Size of the word search grid
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Get the base name without extension
        base_name = os.path.basename(word_file_path)
        file_name = os.path.splitext(base_name)[0]
        
        # Set output PDF paths
        output_dir = Path('/home/rthurman/code/word_search/downloads')
        output_pdf = output_dir / f"{file_name}.pdf"
        
        print(f"Generating word search for {base_name}...", end="", flush=True)
        
        # Run the word search generator
        result = subprocess.run([
            sys.executable, 
            "app/word_search.py",
            str(word_file_path),
            "-o", str(output_pdf),
            "-s", str(grid_size)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f" [FAILED]")
            return (False, f"Error processing {base_name}: {result.stderr}")
        
        solved_pdf = Path(str(output_pdf).replace('.pdf', '_solved.pdf'))
        if not output_pdf.exists() or not solved_pdf.exists():
            print(f" [FAILED]")
            return (False, f"Failed to create PDFs for {base_name}")
        
        print(f" [SUCCESS]")
        return (True, f"Generated PDFs: {output_pdf.name} and {solved_pdf.name}")
        
    except Exception as e:
        print(f" [ERROR]")
        return (False, f"Exception processing {os.path.basename(word_file_path)}: {str(e)}")

def main():
    """Process all word list files in the uploads directory and generate PDFs."""
    start_time = time.time()
    
    # Get paths to directories
    uploads_dir = Path('/home/rthurman/code/word_search/uploads')
    downloads_dir = Path('/home/rthurman/code/word_search/downloads')
    
    # Ensure the downloads directory exists
    if not downloads_dir.exists():
        os.makedirs(downloads_dir)
    
    # Get all txt files in uploads directory, but skip the original sample_words.txt
    word_files = [f for f in uploads_dir.glob("*.txt") 
                 if f.name != "sample_words.txt" and os.path.getsize(f) > 0]
    
    if not word_files:
        print("No word list files found in the uploads directory.")
        return
    
    print(f"Found {len(word_files)} word list files to process.")
    print(f"Output PDFs will be saved to: {downloads_dir}")
    print("-" * 60)
    
    # Process files in parallel to speed up generation
    success_count = 0
    error_count = 0
    error_messages = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_CONCURRENT_PROCESSES) as executor:
        future_to_file = {executor.submit(generate_pdf_for_file, file): file for file in word_files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                success, message = future.result()
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(message)
            except Exception as e:
                error_count += 1
                error_messages.append(f"Exception processing {file.name}: {str(e)}")
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"Batch processing completed in {elapsed_time:.2f} seconds.")
    print(f"Successfully generated PDFs: {success_count}/{len(word_files)}")
    print(f"Failed: {error_count}/{len(word_files)}")
    
    if error_count > 0:
        print("\nErrors encountered:")
        for i, msg in enumerate(error_messages, 1):
            print(f"{i}. {msg}")
    
    print("\nAll word searches are ready for your buddy!")
    print(f"PDF files are located in: {downloads_dir}")

if __name__ == "__main__":
    main()
