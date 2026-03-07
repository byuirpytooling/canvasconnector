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

# Get all courses (current only or all)
courses = get_courses_polars(client, current_only=True)
print(courses)
```

## Fetching Assignments

```python
from canvasconnector import get_assignments, get_assignments_all_courses

# Get assignments for a single course
assignments = get_assignments(
    client,
    course_code=396812,         # Change to one of your course IDs
    assignment_weights=True
)

# Get assignments for all your courses (parallel processing)
all_assignments = get_assignments_all_courses(
    client,
    courses["course_id"],
    max_workers=10              # Fetch 10 courses at once
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

## Assignment Detials

```python
from canvasconnector import get_assignment_details

# Get full assignment context (useful for LLMs)
details = get_assignment_details(client, course_id=396812, assignment_id=16622655)
print(details["description"])
print(details["rubric"])
print(details["links"])

# Get a quick summary of submission requirements only
details_only = get_assignment_details(
    client,
    course_id=396812,
    assignment_id=16622655,
    details_only=True
)
print(details_only["submission_types"])
print(details_only["allowed_attempts"])
```

## Submitting an Assignment

```python
# Submit a URL assignment (type is detected automatically)
submit_assignment(
    client,
    course_id=396812,
    assignment_id=16622657,
    submission_url="https://example.com/my-project"
)

# Submit a text entry assignment
submit_assignment(
    client,
    course_id=396812,
    assignment_id=16622655,
    body="My submission text here..."
)

# Submit a file upload assignment (Carefule about the upload type...)
submit_assignment(
    client,
    course_id=396812,
    assignment_id=16622659,
    file_path="/path/to/my_file.pdf"
)
```

## Submission Comments

```python

from canvasconnector import get_submission_comments, post_submission_comment

# Get comments on a submission
comments = get_submission_comments(client, course_id=396812, assignment_id=16622659)
print(comments)

# Post a comment on a submission
post_submission_comment(
    client,
    course_id=396812,
    assignment_id=16622659,
    comment="Great feedback, thank you!"
)
```

## Submission and Comment Together

```python

# Submit and leave a comment in one flow
if submit_assignment(
    client,
    course_id=396812,
    assignment_id=16622657,
    submission_url="https://example.com/my-project"
):
    post_submission_comment(
        client,
        course_id=396812,
        assignment_id=16622657,
        comment="Submitted! Let me know if you have any questions."
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

## Discussion

```python

from canvasconnector import (
    get_discussions,
    get_discussion_entries,
    get_discussion_replies,
    get_all_discussion_posts,
    post_discussion_entry,
    post_discussion_reply,
    like_discussion_post,
    like_all_discussion_posts,
)

# Get all discussion topics for a course
discussions = get_discussions(client, course_id=396812)
print(discussions)

# Get entries (top-level posts) for a discussion
entries = get_discussion_entries(client, course_id=396812, discussion_id=9875322)

# Get replies to a specific entry
replies = get_discussion_replies(
    client,
    course_id=396812,
    discussion_id=9875322,
    entry_id=78441102
)

# Get all posts and replies in one flat DataFrame
all_posts = get_all_discussion_posts(client, course_id=396812, discussion_id=9875322)

# Post a top-level entry
post_discussion_entry(
    client,
    course_id=396812,
    discussion_id=9875322,
    message="Here is my initial post..."
)

# Reply to an existing entry
post_discussion_reply(
    client,
    course_id=396812,
    discussion_id=9875322,
    entry_id=entries["entry_id"][4],
    message="I randomly responde to the 5th entry!"
)

# Like a specific post
like_discussion_post(
    client,
    course_id=396812,
    discussion_id=9875322,
    post_id=entries["entry_id"][4]
)

# Like all posts in a discussion (25% of posts randomly liked by default)
all_posts = get_all_discussion_posts(client, course_id=396812, discussion_id=9875322)
like_all_discussion_posts(client, all_posts)

# Increase the probability
like_all_discussion_posts(client, all_posts, probability=0.5)

```
