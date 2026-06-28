import os
import re
from datetime import datetime, timezone
from app.utils.constants import ALLOWED_EXTENSIONS

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file is of a supported format."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_timestamp_string() -> str:
    """Generate a clean timestamp string for file names."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")



def sanitize_filename(filename: str) -> str:
    """Basic filename sanitization."""
    base = os.path.basename(filename).replace(" ", "_")
    return re.sub(r'[^a-zA-Z0-9_.-]', '', base)
