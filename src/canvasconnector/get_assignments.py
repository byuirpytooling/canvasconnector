from .make_client import CanvasClient
from .utils import convert_canvas_datetime

import requests
import polars as pl
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_assignments(
    client: CanvasClient, course_code: int, assignment_weights: bool = False
):
    url: Optional[str] = f"{client.canvas_url}/api/v1/courses/{course_code}/assignments"

    params: Optional[dict[str, int | str]] = {
        "per_page": 100,
        "include[]": "submission",
    }

    all_assignments = []

    while url:
        response = requests.get(url, headers=client.headers, params=params)
        all_assignments.extend(response.json())

        # Check for next page
        url = None
        params = None  # Clear params for subsequent requests
        if "Link" in response.headers:
            links = response.headers["Link"].split(",")
            for link in links:
                if 'rel="next"' in link:
                    url = link[link.find("<") + 1 : link.find(">")]
                    break

    # Handle empty assignments
    if not all_assignments:
        return pl.DataFrame()

    # Convert to DataFrame with strict=False to handle mixed types
    assignments_df = pl.DataFrame(all_assignments, strict=False)

    # Check if submission column exists - if not, we have a problem
    has_submissions = "submission" in assignments_df.columns

    if has_submissions:
        # fmt: off
        clean_df = assignments_df.select(
            [
                "workflow_state",
                "course_id",
                pl.col("id").alias("assignment_id"),
                pl.col("name").alias("assignment_name"),
                "position",
                "points_possible",
                "grading_type",
                "created_at",
                "due_at",
                "omit_from_final_grade",
                "assignment_group_id",
                # Submission fields - cast to explicit types
                pl.col("submission").struct.field("score").cast(pl.Float64).alias("score"),
                pl.col("submission").struct.field("grade").cast(pl.String).alias("grade"),
                pl.col("submission").struct.field("submission_type").cast(pl.String).alias("submission_type"),
                pl.col("submission").struct.field("submitted_at").cast(pl.String).alias("submitted_at"),
                pl.col("submission").struct.field("excused").cast(pl.Boolean).alias("excused"),
                pl.col("submission").struct.field("attempt").cast(pl.Int64).alias("attempt"),
                pl.col("submission").struct.field("late").cast(pl.Boolean).alias("late"),
                pl.col("submission").struct.field("missing").cast(pl.Boolean).alias("missing"),
            ]
        )
        # fmt: on
    else:
        # No submission data available - create columns with nulls
        print(
            f"\tWarning: Course {course_code} has no submission data. All submission fields will be null."
        )

        clean_df = assignments_df.select(
            [
                "workflow_state",
                "course_id",
                pl.col("id").alias("assignment_id"),
                pl.col("name").alias("assignment_name"),
                "position",
                "points_possible",
                "grading_type",
                "created_at",
                "due_at",
                "omit_from_final_grade",
                "assignment_group_id",
            ]
        ).with_columns(
            [
                pl.lit(None, dtype=pl.Float64).alias("score"),
                pl.lit(None, dtype=pl.String).alias("grade"),
                pl.lit(None, dtype=pl.String).alias("submission_type"),
                pl.lit(None, dtype=pl.String).alias("submitted_at"),
                pl.lit(None, dtype=pl.Boolean).alias("excused"),
                pl.lit(None, dtype=pl.Int64).alias("attempt"),
                pl.lit(None, dtype=pl.Boolean).alias("late"),
                pl.lit(None, dtype=pl.Boolean).alias("missing"),
            ]
        )

    # clean_df = clean_df.with_columns(
    #     [pl.col("created_at").str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%SZ")]
    # )

    if assignment_weights:
        weights = get_assignment_group(client, course_code)
        clean_df = clean_df.join(weights, how="left", on="assignment_group_id")

    # Convert datetime columns
    datetime_columns = ["created_at", "due_at", "submitted_at"]

    for col in datetime_columns:
        if clean_df[col].dtype == pl.Utf8:
            clean_df = clean_df.with_columns(
                pl.col(col)
                .str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%SZ", strict=False)
                .dt.replace_time_zone("UTC")
                .dt.convert_time_zone(client.timezone)
                .alias(col)
            )

    return clean_df


def get_assignment_group(client: CanvasClient, course_code: int):
    url = f"{client.canvas_url}/api/v1/courses/{course_code}/assignment_groups"

    response = requests.get(url, headers=client.headers)
    groups = response.json()

    # Convert to DataFrame
    groups_df = pl.DataFrame(groups)

    # Select useful fields
    groups_clean = groups_df.select(
        [
            pl.col("id").alias(
                "assignment_group_id"
            ),  # This is the assignment_group_id
            pl.col("name").alias("assignment_group_name"),
            pl.col("group_weight").alias(
                "assignment_group_weight"
            ),  # The percentage weight (e.g., 40 for 40%)
            pl.col("position").alias("assignment_group_position"),
        ]
    )

    return groups_clean


# def get_assignments_all_courses(client: CanvasClient, course_list: pl.Series):
#     """Get assignments for all courses and concatenate into one DataFrame."""

#     all_courses_assignments = []

#     for course_id in course_list:
#         try:
#             print(f"Fetching assignments for course {course_id}...")

#             # Get assignments with weights for this course
#             course_assignments = get_assignments(client, course_id, assignment_weights=True)

#             # Only append if we got data back
#             if len(course_assignments) > 0:
#                 all_courses_assignments.append(course_assignments)

#         except Exception as e:
#             print(f"Error fetching course {course_id}: {e}")
#             continue

#     # Concatenate all course assignments
#     if not all_courses_assignments:
#         return pl.DataFrame()

#     return pl.concat(all_courses_assignments)


def get_assignments_all_courses(
    client: CanvasClient, course_list: pl.Series, max_workers: int = 5
):
    """Get assignments for all courses in parallel."""

    all_courses_assignments = []

    # Use ThreadPoolExecutor to fetch in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(get_assignments, client, course_id, True): course_id
            for course_id in course_list
        }

        # Collect results as they complete
        for future in as_completed(futures):
            course_id = futures[future]
            try:
                print(f"Fetching assignments for course {course_id}...")
                result = future.result()
                if len(result) > 0:
                    all_courses_assignments.append(result)
            except Exception as e:
                print(f"Error fetching course {course_id}: {e}")

    # Concatenate all course assignments
    if not all_courses_assignments:
        return pl.DataFrame()

    return pl.concat(all_courses_assignments, how="diagonal")
