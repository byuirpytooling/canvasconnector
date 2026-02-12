# Code Examples

## Initial Setup

### 1. Create a `.env` file

Create a `.env` file in your project root with your Canvas credentials:

```plaintext
# Canvas API Configuration
CANVAS_TOKEN=your_canvas_api_token_here
CANVAS_URL=https://byui.instructure.com
TIMEZONE=America/Denver
```

**Getting your credentials:**

- **CANVAS_TOKEN**: Canvas → Account → Settings → New Access Token
- **CANVAS_URL**: Your institution's Canvas URL
- **TIMEZONE**: Your IANA timezone (e.g., `America/Denver`, `America/New_York`)

**Security**: Add `.env` to your `.gitignore` to keep your API token private.

### 2. Setting Up the Client

```python
from canvasconnector import CanvasClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = CanvasClient(
    api_key=os.getenv("CANVAS_TOKEN"),
    canvas_url=os.getenv("CANVAS_URL"),
    timezone=os.getenv("TIMEZONE")
)
```

## Getting Your Courses

```python
from canvasconnector import get_courses_polars

# Get only current courses
courses = get_courses_polars(client, current_only=True)
print(courses)
```

## Fetching Assignments

```python
from canvasconnector import get_assignments, get_assignments_all_courses

# Get assignments for a single course
assignments = get_assignments(
    client,
    course_id=398922,
    assignment_weights=True
)

# Get assignments for all your courses (parallel processing)
all_assignments = get_assignments_all_courses(
    client,
    courses["course_id"],
    max_workers=10  # Fetch 10 courses at once
)
```

## Finding Upcoming Assignments

```python
from canvasconnector import get_upcoming_assignments

upcoming = get_upcoming_assignments(
    client,
    courses["course_id"],
    days=14  # Next 2 weeks
)
print(upcoming)
```

## Getting Peer Information

```python
from canvasconnector import get_all_peers, get_best_friends

# Get all peers from your courses
peers = get_all_peers(client, courses["course_id"])

# Find your most common classmates
best_friends = get_best_friends(
    client,
    peers,
    students_only=True
)
print(best_friends)
```
