# Code Examples

> **Prerequisites**: Complete the [Setup](index.md#setup) in the getting started guide first.

All examples assume you have a client initialized:

```python
from canvasconnector import CanvasClient
from dotenv import load_dotenv
import os

load_dotenv()
client = CanvasClient(
    api_key=os.getenv("CANVAS_API_TOKEN"),
    canvas_url=os.getenv("CANVAS_URL"),
    timezone=os.getenv("TIMEZONE")
)
```

## Getting Your Courses

```python
from canvasconnector import get_courses_polars

# Get all courses
courses = get_courses_polars(client)

# Get only current courses
current_courses = get_courses_polars(client, current_only=True)
print(current_courses)
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

# Get assignments due in the next 2 weeks
upcoming = get_upcoming_assignments(
    client,
    courses["course_id"],
    days=14
)
print(upcoming)

# Get assignments due in the next week
upcoming_week = get_upcoming_assignments(
    client,
    courses["course_id"],
    days=7
)
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
