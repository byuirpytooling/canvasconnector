from .make_client import CanvasClient
import requests
from datetime import datetime
import polars as pl


def get_courses_raw(client: CanvasClient):
    """Get courses as a list of dictionaries.

        This function retrieves all courses for the authenticated user from the
        Canvas API and returns them as raw Python dictionaries with selected fields.

        Args:
            client (CanvasClient): The Canvas API client instance.

        Returns:
            list[dict]: A list of course dictionaries with the following keys:
                - id (int): Course ID
                - name (str): Course name
                - course_code (str): Course code (e.g., "BUS 301")
                - term_id (int): Term ID
                - term_name (str): Term name (e.g., "Winter 2025")
                - term_start_at (str): Term start date (ISO 8601 format)
                - term_end_at (str): Term end date (ISO 8601 format)
                - enrollment_type (str): Type of enrollment (student, teacher, ta, observer)

        Example:
    ```python
            client = CanvasClient(
                api_key="your_token",
                canvas_url="https://byui.instructure.com"
            )
            courses = get_courses_raw(client)
            print(courses[0]['name'])  # "Adv Writing in Pro Contexts"
    ```
    """

    response = requests.get(
        f"{client.canvas_url}/api/v1/courses",
        headers=client.headers,
        params=[("per_page", 100), ("include[]", "term")],
    )

    if response.status_code == 200:
        courses = response.json()

        # Extract only the fields you want
        filtered_courses = []
        for course in courses:
            filtered_course = {
                "course_id": course["id"],
                "course_name": course["name"],
                "course_code": course.get("course_code"),
                "term_id": course.get("term", {}).get("id"),
                "term_name": course.get("term", {}).get("name"),
                "term_start_at": course.get("term", {}).get("start_at"),
                "term_end_at": course.get("term", {}).get("end_at"),
                "enrollment_type": course["enrollments"][0]["type"]
                if course.get("enrollments")
                else None,
            }
            filtered_courses.append(filtered_course)

        # Now filtered_courses has only what you want
        return filtered_courses
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


def get_courses_polars(client: CanvasClient, current_only: bool):
    """Get courses as a Polars DataFrame.

        This function retrieves all courses for the authenticated user from the
        Canvas API and returns them as a Polars DataFrame for easy analysis.

        Args:
            client (CanvasClient): The Canvas API client instance.
            current_only (bool): If True, only return courses from current term.

        Returns:
            pl.DataFrame: A Polars DataFrame with course data.

        Example:
    ```python
            client = CanvasClient(
                api_key="your_token",
                canvas_url="https://byui.instructure.com"
            )
            courses_df = get_courses_polars(client, current_only=True)
            print(courses_df.head())
    ```
    """
    data = get_courses_raw(client)

    df = pl.DataFrame(
        data,
        schema={
            "course_id": pl.Int64,
            "course_name": pl.Utf8,
            "course_code": pl.Utf8,
            "term_id": pl.Int64,
            "term_name": pl.Utf8,
            "term_start_at": pl.Utf8,  # or pl.Datetime if you want to parse dates
            "term_end_at": pl.Utf8,
            "enrollment_type": pl.Utf8,
        },
    )
    # Convert to date only (no time)
    df = df.with_columns(
        [
            pl.col("term_start_at").str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%SZ"),
            pl.col("term_end_at").str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%SZ"),
        ]
    )

    if current_only:
        today = pl.lit(datetime.now().date())
        df = df.filter(
            (pl.col("term_start_at") <= today) & (pl.col("term_end_at") >= today)
        )

    return df
