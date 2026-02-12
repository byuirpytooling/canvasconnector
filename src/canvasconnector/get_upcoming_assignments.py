from .make_client import CanvasClient
from .get_assignments import get_assignments_all_courses
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import polars as pl


def get_upcoming_assignments(
    client: CanvasClient,
    course_ids: pl.Series,
    days: int = 7,
    exclude_submitted: bool = True,
):
    """Get assignments due within a specified number of days.

    Retrieves assignments from the Canvas LMS API that are due within the next
    ``days`` days, with optional filtering to exclude already-submitted assignments.

    Args:
        client: An authenticated CanvasClient instance.
        course_ids: A Polars Series containing course IDs to fetch assignments from.
        days: Number of days to look ahead for due assignments. Defaults to 7.
        exclude_submitted: Whether to filter out assignments that have already been
            submitted. Defaults to True.

    Returns:
        A Polars DataFrame containing upcoming assignments with columns including
        ``due_at``, ``submitted_at``, and other assignment metadata.

    Examples:
        >>> df_courses = get_courses_polars(client, current_only=True)
        >>> upcoming = get_assignments_due(client, df_courses['course_id'], days=5)
        >>> upcoming_all = get_assignments_due(client, df_courses['course_id'],
        ...                                    days=14, exclude_submitted=False)
    """
    assignments = get_assignments_all_courses(client, course_ids)

    tz = ZoneInfo(client.timezone)
    now = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    future_date = (now + timedelta(days=days)).replace(hour=23, minute=59, second=59)

    upcoming = assignments.filter(
        (pl.col("due_at").is_not_null())
        & (pl.col("due_at").is_between(pl.lit(now), pl.lit(future_date)))
    )

    if exclude_submitted:
        upcoming = upcoming.filter(
            pl.col("submitted_at").is_null()  # or check workflow_state != "submitted"
        )

    return upcoming
