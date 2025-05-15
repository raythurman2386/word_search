"""
Word Search Generator
---------------------
A script that generates a word search puzzle from a list of words in a text file
and saves it as a PDF.
"""

import argparse
import os
import random
import string

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class WordSearchGenerator:
    def __init__(self, word_list, grid_size=20, max_attempts=100):
        """Initialize the word search generator.

        Args:
            word_list (list): List of words to include in the puzzle
            grid_size (int): Size of the grid (grid_size x grid_size)
            max_attempts (int): Maximum attempts to place a word
        """
        self.word_list = [word.upper() for word in word_list if word.strip()]
        self.grid_size = grid_size
        self.max_attempts = max_attempts
        self.grid = [[" " for _ in range(grid_size)] for _ in range(grid_size)]
        self.placed_words = []
        self.word_locations = {}  # Store word locations for solution
        self.directions = [
            (0, 1),  # right
            (1, 0),  # down
            (1, 1),  # down-right
            (1, -1),  # down-left
            (0, -1),  # left
            (-1, 0),  # up
            (-1, 1),  # up-right
            (-1, -1),  # up-left
        ]

    def generate_puzzle(self):
        """Generate the word search puzzle."""
        # Sort words by length (longest first for better placement)
        words = sorted(self.word_list, key=len, reverse=True)

        for word in words:
            if self._place_word(word):
                self.placed_words.append(word)
            else:
                print(f"Warning: Could not place '{word}' in the grid")

        # Fill empty cells with random letters
        self._fill_empty_cells()
        return self.grid, self.placed_words

    def _place_word(self, word):
        """Try to place a word in the grid.

        Args:
            word (str): Word to place

        Returns:
            bool: True if word was placed, False otherwise
        """
        attempts = 0
        while attempts < self.max_attempts:
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)

            direction = random.choice(self.directions)

            # Check if word fits in the grid in this direction
            row_step, col_step = direction
            end_row = row + (len(word) - 1) * row_step
            end_col = col + (len(word) - 1) * col_step

            if 0 <= end_row < self.grid_size and 0 <= end_col < self.grid_size:
                # Check if word can be placed without conflicts
                can_place = True
                positions = []

                for i in range(len(word)):
                    curr_row = row + i * row_step
                    curr_col = col + i * col_step
                    curr_cell = self.grid[curr_row][curr_col]

                    if curr_cell != " " and curr_cell != word[i]:
                        can_place = False
                        break

                    positions.append((curr_row, curr_col))

                if can_place:
                    # Place the word
                    for i, (curr_row, curr_col) in enumerate(positions):
                        self.grid[curr_row][curr_col] = word[i]
                    # Store word location for solution
                    self.word_locations[word] = positions
                    return True

            attempts += 1

        return False

    def _fill_empty_cells(self):
        """Fill empty cells with random letters."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == " ":
                    self.grid[row][col] = random.choice(string.ascii_uppercase)

    def save_to_pdf(
        self, filename, title="Word Search Puzzle", description="", solved=False
    ):
        """Save the word search puzzle to a PDF file.

        Args:
            filename (str): Output filename
            title (str): Title for the puzzle
            description (str): Description for the puzzle
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            topMargin=20,
            bottomMargin=20,
            leftMargin=30,
            rightMargin=30,
        )
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="CompactTitle",
            parent=styles["Title"],
            spaceAfter=2,
        )
        elements.append(Paragraph(title, title_style))

        elements.append(Spacer(1, 5))

        data = []
        for row in self.grid:
            data.append([letter for letter in row])

        page_width, page_height = letter
        cell_size = min(page_width, page_height) / (self.grid_size + 2)

        table = Table(data, colWidths=cell_size, rowHeights=cell_size)

        table_style = [
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGNMENT", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 1.5, colors.black),
        ]

        if solved:
            elements.append(Paragraph("*Solved Version*", styles["Heading3"]))

            colors_list = [
                colors.red,
                colors.blue,
                colors.green,
                colors.orange,
                colors.purple,
                colors.cyan,
                colors.magenta,
                colors.brown,
            ]

            for idx, (word, positions) in enumerate(self.word_locations.items()):
                color = colors_list[idx % len(colors_list)]
                for row, col in positions:
                    table_style.append(("BACKGROUND", (col, row), (col, row), color))
                    table_style.append(
                        ("TEXTCOLOR", (col, row), (col, row), colors.white)
                    )

        table.setStyle(TableStyle(table_style))

        elements.append(table)
        elements.append(Spacer(1, 5))

        word_list_header = ParagraphStyle(
            name="WordListHeader",
            parent=styles["Heading2"],
            alignment=1,
            spaceAfter=2,
            textColor=colors.darkblue,
            fontSize=14,
        )
        elements.append(Paragraph("Words to Find", word_list_header))

        word_count_style = ParagraphStyle(
            name="WordCount",
            parent=styles["Normal"],
            fontSize=7,
            alignment=1,
            textColor=colors.darkgrey,
            spaceAfter=1,
        )

        if description:
            word_count_msg = f"Find all {len(self.placed_words)} words hidden in the puzzle - {description}"
        else:
            word_count_msg = (
                f"Find all {len(self.placed_words)} words hidden in the puzzle"
            )

        elements.append(Paragraph(word_count_msg, word_count_style))

        sorted_words = sorted(self.placed_words)

        max_word_len = max(len(word) for word in sorted_words)
        optimal_columns = min(5, max(2, int(page_width / (max_word_len * 10))))

        words_per_column = max(
            1,
            len(sorted_words) // optimal_columns
            + (1 if len(sorted_words) % optimal_columns else 0),
        )

        word_columns = []
        for i in range(0, len(sorted_words), words_per_column):
            word_columns.append(sorted_words[i : i + words_per_column])

        word_list_data = []
        max_rows = max(len(col) for col in word_columns)

        bullet_style = ParagraphStyle(
            name="BulletStyle",
            parent=styles["Normal"],
            fontSize=9,
            leftIndent=5,
            spaceBefore=1,
            spaceAfter=1,
            bulletIndent=0,
            bulletFontName="Helvetica",
            bulletFontSize=9,
        )

        for row in range(max_rows):
            row_data = []
            for col in word_columns:
                if row < len(col):
                    word_para = Paragraph(f"• {col[row]}", bullet_style)
                    word_para = Paragraph(f"• {col[row]}", bullet_style)
                    row_data.append(word_para)
                else:
                    row_data.append("")
            word_list_data.append(row_data)

        col_width = page_width / (len(word_columns) + 0.5)
        word_table = Table(word_list_data, colWidths=[col_width] * len(word_columns))

        word_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        elements.append(word_table)

        doc.build(elements)
        print(f"Word search puzzle saved to {filename}")


def read_words_from_file(file_path):
    """Read words from a text file.

    Args:
        file_path (str): Path to the text file

    Returns:
        tuple: Title, description, and list of words
    """
    title = ""
    description = ""
    words = []

    with open(file_path, "r") as file:
        lines = [line.strip() for line in file if line.strip()]

        # Check if file starts with title/description format
        if len(lines) >= 2 and lines[0].startswith("Title:"):
            title = lines[0].replace("Title:", "").strip()
            description = lines[1].replace("Desc:", "").strip()
            # Skip empty line if present
            start_idx = 2
            if len(lines) > 2 and not lines[2]:
                start_idx = 3
            words = [line for line in lines[start_idx:] if line.strip()]
        else:
            # No title/description format, all lines are words
            words = lines

    return title, description, words


def main():
    parser = argparse.ArgumentParser(
        description="Generate a word search puzzle from a list of words."
    )
    parser.add_argument("input_file", help="Text file containing words (one per line)")
    parser.add_argument(
        "-o", "--output", help="Output PDF file", default="word_search.pdf"
    )
    parser.add_argument(
        "-s", "--size", type=int, help="Grid size (default: 20)", default=20
    )
    parser.add_argument(
        "-a",
        "--attempts",
        type=int,
        help="Maximum attempts to place a word (default: 100)",
        default=100,
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return

    title, description, words = read_words_from_file(args.input_file)

    if not words:
        print("Error: No words found in the input file.")
        return

    print(f"Loaded {len(words)} words from {args.input_file}")
    if title:
        print(f"Title: {title}")
    if description:
        print(f"Description: {description}")

    generator = WordSearchGenerator(words, args.size, args.attempts)
    generator.generate_puzzle()

    generator.save_to_pdf(args.output, title or "Word Search Puzzle", description)

    solved_filename = args.output.rsplit(".", 1)[0] + "_solved.pdf"
    generator.save_to_pdf(
        solved_filename, title or "Word Search Puzzle", description, solved=True
    )
    print(f"Solved version saved to {solved_filename}")


if __name__ == "__main__":
    main()
