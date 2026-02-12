# Code Examples

## Setting Up the Client

```python
from canvasconnector import CanvasClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = CanvasClient(
    api_token=os.getenv("CANVAS_TOKEN"), # e.g., "https://byui.instructure.com"
    canvas_url=os.getenv("CANVAS_URL"),
    timezone=os.getenv("TIMEZONE")  # e.g., "America/Denver"
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
