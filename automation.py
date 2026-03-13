"""
Basic File Organizer Automation
Sorts files in a target directory into subfolders by file type.
"""

import os
import shutil
import argparse
from pathlib import Path

# Map of category name -> list of extensions
FILE_CATEGORIES = {
    "Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Videos":     [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
    "Audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Documents":  [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".odt"],
    "Archives":   [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
    "Code":       [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs"],
    "Data":       [".csv", ".json", ".xml", ".yaml", ".yml", ".sql", ".db"],
}


def get_category(ext: str) -> str:
    """Return the category name for a given file extension."""
    ext = ext.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def organize(directory: str, dry_run: bool = False) -> dict:
    """
    Organize files in `directory` into category subfolders.

    Args:
        directory: Path to the folder to organize.
        dry_run:   If True, only print what would happen without moving files.

    Returns:
        A summary dict {category: [filenames moved]}.
    """
    target = Path(directory).resolve()

    if not target.is_dir():
        raise NotADirectoryError(f"'{target}' is not a valid directory.")

    summary: dict[str, list] = {}

    for item in target.iterdir():
        # Skip directories and this script itself
        if item.is_dir() or item.name == Path(__file__).name:
            continue

        category = get_category(item.suffix)
        dest_folder = target / category

        action = f"{'[DRY RUN] ' if dry_run else ''}Moving '{item.name}' -> {category}/"
        print(action)

        if not dry_run:
            dest_folder.mkdir(exist_ok=True)
            shutil.move(str(item), dest_folder / item.name)

        summary.setdefault(category, []).append(item.name)

    return summary


def print_summary(summary: dict) -> None:
    if not summary:
        print("\nNo files to organize.")
        return

    print("\n--- Summary ---")
    total = 0
    for category, files in sorted(summary.items()):
        print(f"  {category}: {len(files)} file(s)")
        total += len(files)
    print(f"  Total: {total} file(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Organize files in a directory into subfolders by type."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to organize (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files",
    )
    args = parser.parse_args()

    print(f"Organizing: {Path(args.directory).resolve()}")
    if args.dry_run:
        print("(Dry run — no files will be moved)\n")

    summary = organize(args.directory, dry_run=args.dry_run)
    print_summary(summary)


if __name__ == "__main__":
    main()
