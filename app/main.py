"""
Word Search Generator Web Application
------------------------------------
A FastAPI web application that provides a user interface for generating word search puzzles.
Production-ready with file upload support, health checks, and configuration management.
"""

import asyncio
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .health import router as health_router
from .logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    description="Generate word search puzzles with customizable options",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")


def create_friendly_filename(title: str, description: str, request_id: str) -> str:
    """Create a friendly filename based on title and description.

    Args:
        title: The word search title
        description: The word search description
        request_id: UUID to ensure uniqueness

    Returns:
        A sanitized filename with title and description (if available)
    """
    filename = title.strip() if title.strip() else "Word-Search"

    if description.strip():
        desc_words = description.strip().split()
        short_desc = " ".join(desc_words[:3])
        desc_words = description.strip().split()
        short_desc = " ".join(desc_words[:3])
        if len(short_desc) > 30:
            short_desc = short_desc[:27] + "..."
        filename = f"{filename}-{short_desc}"

    filename = re.sub(r"[^\w\-\.]", "-", filename.replace(" ", "-"))

    if len(filename) > 100:
        filename = filename[:97] + "..."

    # Add the UUID to ensure uniqueness
    return f"{filename}-{request_id[:8]}"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page with the word search generator form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
async def generate_word_search(
    request: Request,
    background_tasks: BackgroundTasks,
    title: str = Form("Word Search"),
    description: str = Form(""),
    words: Optional[str] = Form(default=""),
    grid_size: int = Form(15),
    file: Optional[UploadFile] = File(None),
):
    """Generate a word search puzzle based on form input or uploaded file."""
    request_id = str(uuid.uuid4())
    logger.info(f"Generating word search with ID: {request_id}")

    final_title = title
    final_description = description
    temp_file_path = Path(f"{settings.UPLOADS_DIR}/{request_id}_temp.txt")

    try:
        # Process the input (either file or text)
        if file and file.filename:
            try:
                logger.info(f"Using uploaded file: {file.filename}")
                content = await file.read()
                if not content:  # Check if file is empty
                    logger.error("Uploaded file is empty")
                    return templates.TemplateResponse(
                        "error.html",
                        {
                            "request": request,
                            "error": "The uploaded file is empty. Please select a valid word list file.",
                        },
                    )

                # Write content to a temporary file first
                with open(temp_file_path, "wb") as f:
                    f.write(content)

                try:
                    with open(temp_file_path, "r") as f:
                        file_lines = f.readlines()

                    if file_lines and file_lines[0].lower().startswith("title:"):
                        file_title = file_lines[0].strip()[6:].strip()
                        if file_title:
                            final_title = file_title

                    if len(file_lines) > 1 and file_lines[1].lower().startswith(
                        "desc:"
                    ):
                        file_desc = file_lines[1].strip()[5:].strip()
                        if file_desc:
                            final_description = file_desc
                except Exception as e:
                    logger.warning(
                        f"Could not extract title/description from file: {e}"
                    )

                logger.info(f"Successfully processed uploaded file to {temp_file_path}")

            except Exception as e:
                logger.error(f"File upload error: {str(e)}")
                return templates.TemplateResponse(
                    "error.html",
                    {"request": request, "error": f"Error processing file: {str(e)}"},
                )
        elif (
            words and words.strip()
        ):  # Only use form input if no file was uploaded and words isn't empty
            logger.info("Using form input for word list")
            with open(temp_file_path, "w") as f:
                f.write(f"Title: {final_title}\n")
                f.write(f"Desc: {final_description}\n\n")
                f.write(words)
        else:
            logger.error("No input provided: neither file nor words")
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error": "Please either upload a file or enter words in the text area.",
                },
            )

        friendly_name = create_friendly_filename(
            final_title, final_description, request_id
        )
        logger.info(f"Using friendly filename: {friendly_name}")
        words_file = Path(f"{settings.UPLOADS_DIR}/{friendly_name}.txt")
        output_pdf = Path(f"{settings.DOWNLOADS_DIR}/{friendly_name}.pdf")
        solved_pdf = Path(f"{settings.DOWNLOADS_DIR}/{friendly_name}_solved.pdf")

        if temp_file_path.exists():
            shutil.copy(temp_file_path, words_file)
            temp_file_path.unlink()
        background_tasks.add_task(
            schedule_cleanup, [words_file, output_pdf, solved_pdf]
        )

        logger.info(f"Running word search generator with grid size: {grid_size}")
        result = subprocess.run(
            [
                sys.executable,
                "app/word_search.py",
                str(words_file),
                "-o",
                str(output_pdf),
                "-s",
                str(grid_size),
            ],
            capture_output=True,
            text=True,
        )

        if not solved_pdf.exists():
            logger.warning(f"Solved PDF not found at expected path: {solved_pdf}")
            solved_pdf = Path(str(output_pdf).replace(".pdf", "_solved.pdf"))
            if not solved_pdf.exists():
                logger.error("Could not find solved PDF version")
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "error": "Could not generate solution PDF. Please try again.",
                    },
                )

        if result.returncode != 0:
            logger.error(f"Word search generation failed: {result.stderr}")
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error": result.stderr or "Failed to generate word search",
                },
            )

        logger.info("Word search generated successfully")
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "output_pdf": f"/download/{friendly_name}.pdf",
                "solved_pdf": f"/download/{friendly_name}_solved.pdf",
            },
        )
    except Exception as e:
        logger.error(f"Error generating word search: {str(e)}")
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@app.get("/download/{filename}")
async def download(filename: str):
    """Download a generated PDF file."""
    file_path = f"downloads/{filename}"
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(path=file_path, filename=filename, media_type="application/pdf")


async def schedule_cleanup(files: List[Path]):
    """Schedule cleanup of temporary files after a delay.

    Args:
        files: List of file paths to be removed
    """
    wait_seconds = settings.CLEANUP_INTERVAL_HOURS * 3600

    try:
        await asyncio.sleep(wait_seconds)

        for file_path in files:
            if os.path.exists(str(file_path)):
                os.remove(str(file_path))
                logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error during scheduled cleanup: {str(e)}")


def cleanup_old_files(max_age_hours=None):
    """Remove files older than the specified age.

    Args:
        max_age_hours: Number of hours after which files should be deleted.
                      Defaults to settings.CLEANUP_INTERVAL_HOURS.
    """
    import time

    if max_age_hours is None:
        max_age_hours = settings.CLEANUP_INTERVAL_HOURS

    cutoff = time.time() - (max_age_hours * 3600)

    logger.info(f"Starting cleanup of files older than {max_age_hours} hours")

    for directory in [settings.UPLOADS_DIR, settings.DOWNLOADS_DIR]:
        cleaned = 0
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
                try:
                    os.remove(file_path)
                    cleaned += 1
                except Exception as e:
                    logger.error(f"Error removing old file {file_path}: {str(e)}")

        logger.info(f"Cleaned up {cleaned} files from {directory}")

    return {"status": "success", "cleaned_files_count": cleaned}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
