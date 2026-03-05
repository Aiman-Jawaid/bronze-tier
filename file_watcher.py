#!/usr/bin/env python3
"""
File Watcher for AI Employee Inbox
Monitors /Inbox folder and moves new files to /Needs_Action with metadata.
"""

import os
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
INBOX_DIR = BASE_DIR / "Inbox"
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
LOGS_DIR = BASE_DIR / "Logs"
LOG_FILE = LOGS_DIR / "watcher.log"

# Ensure directories exist
INBOX_DIR.mkdir(parents=True, exist_ok=True)
NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class InboxEventHandler(FileSystemEventHandler):
    """Handle file creation events in Inbox folder."""

    def on_created(self, event):
        """Process newly created files in Inbox."""
        if event.is_directory:
            return

        src_path = Path(event.src_path)
        
        # Skip hidden files and temporary files
        if src_path.name.startswith(".") or src_path.suffix == ".tmp":
            logger.debug(f"Skipping hidden/temp file: {src_path.name}")
            return

        logger.info(f"New file detected: {src_path.name}")
        self.process_file(src_path)

    def process_file(self, src_path: Path):
        """Copy file to Needs_Action with metadata."""
        try:
            # Determine destination filename
            if src_path.suffix.lower() == ".md":
                dest_name = src_path.name
            else:
                dest_name = src_path.name + ".md"

            dest_path = NEEDS_ACTION_DIR / dest_name

            # Handle duplicate filenames
            counter = 1
            while dest_path.exists():
                stem = src_path.stem
                suffix = src_path.suffix if src_path.suffix else ""
                if suffix:
                    dest_name = f"{stem}_{counter}{suffix}.md"
                else:
                    dest_name = f"{src_path.name}_{counter}.md"
                dest_path = NEEDS_ACTION_DIR / dest_name
                counter += 1

            # Create metadata header
            metadata = f"""---
type: file_drop
original: {src_path.name}
created: {datetime.now().isoformat()}
---
"""

            # Read source content
            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Handle binary files
                logger.warning(f"Binary file detected: {src_path.name}, copying as-is")
                with open(src_path, "rb") as f:
                    content = f.read()
                metadata = metadata.encode("utf-8")

            # Write to destination with metadata
            with open(dest_path, "wb" if isinstance(content, bytes) else "w", encoding="utf-8" if not isinstance(content, bytes) else None) as f:
                f.write(metadata)
                f.write(content)

            logger.info(f"Processed: {src_path.name} -> {dest_name}")

        except Exception as e:
            logger.error(f"Error processing file {src_path.name}: {e}")


def main():
    """Main entry point for the file watcher."""
    logger.info("=" * 50)
    logger.info("AI Employee File Watcher Started")
    logger.info(f"Monitoring: {INBOX_DIR}")
    logger.info(f"Output to: {NEEDS_ACTION_DIR}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info("=" * 50)
    logger.info("Press Ctrl+C to stop...")

    event_handler = InboxEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)

    try:
        observer.start()
        logger.info("Watcher is now running...")

        while True:
            # Keep alive with 10s sleep intervals
            import time
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Shutdown signal received...")
        observer.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        observer.stop()
        sys.exit(1)

    observer.join()
    logger.info("Watcher stopped.")


if __name__ == "__main__":
    main()
