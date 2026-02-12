"""Canvas LMS API Connector"""

# read version from installed package
from importlib.metadata import version

__version__ = version("canvasconnector")


from .make_client import CanvasClient
from .get_courses import get_courses_raw, get_courses_polars
from .get_assignments import (
    get_assignments,
    get_assignments_all_courses,
    get_assignment_group,
)
from .get_peers import get_peers, get_all_peers
from .get_best_friends import get_best_friends
from .get_upcoming_assignments import get_upcoming_assignments


__all__ = [
    "CanvasClient",
    "get_courses_raw",
    "get_courses_polars",
    "get_assignments",
    "get_assignments_all_courses",
    "get_assignment_group",
    "get_peers",
    "get_all_peers",
    "get_best_friends",
    "get_upcoming_assignments",
]
