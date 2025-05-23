#!/usr/bin/env python3
"""
Convert word lists from the format:
  Puzzle 1: Title
  WORD1,WORD2,WORD3
  
to the expected format:
  Title: Title
  Desc: 
  
  WORD1
  WORD2
  WORD3
"""
import os
from pathlib import Path

def get_description(title):
    """Return a description for the given puzzle title."""
    descriptions = {
        "Heavy Duty Machines": "Find the names of powerful construction and industrial equipment.",
        "Building Materials": "Discover essential materials used in construction and building.",
        "Essential Tools": "Identify the most important tools found on any job site.",
        "Safety First": "Spot the critical safety equipment used in construction.",
        "Construction Crew": "Locate the various professionals who make up a construction team.",
        "Road Construction": "Find terms related to building and maintaining roads.",
        "Structural Elements": "Identify key components that make up building structures.",
        "Demolition Tools": "Discover equipment used for tearing down and removing structures.",
        "Electrical Work": "Find terms related to electrical systems and components.",
        "Plumbing Systems": "Identify parts and terms related to plumbing installations.",
        "Concrete Work": "Discover terms related to working with concrete.",
        "Roofing Materials": "Find materials commonly used in roof construction.",
        "Masonry Tools": "Identify tools used in bricklaying and stone work.",
        "Earthmoving Equipment": "Locate heavy machinery used for moving earth.",
        "Carpentry Tools": "Find essential tools used in woodworking and framing.",
        "Welding Gear": "Identify equipment used in welding and metalwork.",
        "Building Plans": "Discover terms related to architectural and engineering drawings.",
        "Foundation Work": "Find terms related to building foundations.",
        "Heavy Lifting": "Identify equipment used for moving heavy loads.",
        "Scaffolding": "Discover components of temporary work platforms.",
    }
    return descriptions.get(title, "Find all the hidden words in this puzzle!")

def convert_file(input_file, output_dir):
    """Convert a single word list file to the expected format."""
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    output_lines = []
    current_title = ""
    current_words = []
    
    for line in lines:
        if line.startswith("Puzzle"):
            # If we have a puzzle in progress, save it
            if current_title and current_words:
                output_lines.append(f"Title: {current_title}")
                output_lines.append(f"Desc: {get_description(current_title)}")
                output_lines.append("")  # Empty line
                output_lines.extend(current_words)
                output_lines.append("\n")  # Separate puzzles with blank lines
            
            # Start new puzzle
            current_title = line.split(":", 1)[1].strip()
            current_words = []
        else:
            # Add words to current puzzle
            words = [w.strip() for w in line.split(",") if w.strip()]
            current_words.extend(words)
    
    # Add the last puzzle
    if current_title and current_words:
        output_lines.append(f"Title: {current_title}")
        output_lines.append("Desc: ")
        output_lines.append("")  # Empty line
        output_lines.extend(current_words)
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write output file
    output_file = output_dir / input_file.name
    with open(output_file, 'w') as f:
        f.write("\n".join(output_lines))
    
    return output_file

def main():
    # Set up paths
    base_dir = Path(__file__).parent
    input_file = base_dir / "new_list.txt"
    output_dir = base_dir / "uploads"
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found.")
        return
    
    try:
        output_file = convert_file(input_file, output_dir)
        print(f"Successfully converted {input_file} to {output_file}")
        
        # Run the batch processor
        print("\nRunning batch processor...")
        import subprocess
        subprocess.run(["python3", "app/batch_generate_pdfs.py"], check=True)
        
        print("\nProcessing complete! Check the downloads directory for the generated PDFs.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
