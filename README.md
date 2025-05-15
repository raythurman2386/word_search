# Word Search Generator

A modern web application for generating customized word search puzzles, built with FastAPI and HTMX for a responsive, interactive user experience.

## Features

- **Interactive Web Interface:** Create word search puzzles through a user-friendly web application
- **Two Output Formats:** Generates both regular and solution versions of each puzzle
- **Flexible Word Placement:** Places words horizontally, vertically, and diagonally (forward and backward)
- **Customizable:** Adjust grid size and other options to suit your needs
- **PDF Output:** Clean, printable PDF format for easy distribution
- **Modern Tech Stack:** Built with FastAPI, HTMX, and Python for optimal performance

## Implementation Details

### Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend Enhancement:** HTMX for dynamic interactions without JavaScript
- **PDF Generation:** ReportLab
- **Styling:** Bootstrap 5
- **UI Responsiveness:** Responsive design for desktop and mobile

### Architecture

The application follows modern best practices:

- **Separation of Concerns:** Clear separation between UI and puzzle generation logic
- **RESTful API Design:** Clean API endpoints for future extensibility
- **Template-Based UI:** Server-side rendering for fast initial load times
- **Progressive Enhancement:** Works without JavaScript, enhanced with HTMX

## Installation

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/word_search.git
   cd word_search
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the web server:

```bash
uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000

## Usage

1. **Enter Words:** Type or paste your list of words (one per line) in the text area
2. **Customize:** Set a title, description, and adjust the grid size
3. **Generate:** Click "Generate Word Search" to create your puzzle
4. **Download:** Get both the regular puzzle and the solution key as PDF files

## Docker Support (Optional)

A Dockerfile is included for containerized deployment:

```bash
# Build the Docker image
docker build -t word-search-generator .

# Run the container
docker run -p 8000:8000 word-search-generator
```

## Project Structure

```
word_search/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── word_search.py     # Word search generation logic
│   └── templates/         # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── results.html
│       └── error.html
├── static/                # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── htmx.min.js
├── uploads/               # Temporary storage for word lists
├── downloads/             # Generated PDFs
├── requirements.txt
└── README.md
```

## License

MIT License - Feel free to use, modify, and distribute as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
