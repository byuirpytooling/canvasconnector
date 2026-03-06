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
from .comments import get_submission_comments, post_submission_comment
from .submissions import submit_assignment, get_assignment_details
from .discussions import (
    get_discussions,
    get_discussion_entries,
    get_discussion_replies,
    get_all_discussion_posts,
    post_discussion_entry,
    post_discussion_reply,
    like_discussion_post,
    like_all_discussion_posts,
)


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
    # Comments
    "get_submission_comments",
    "post_submission_comment",
    # Submissions
    "submit_assignment",
    "get_assignment_details",
    # Discussions
    "get_discussions",
    "get_discussion_entries",
    "get_discussion_replies",
    "get_all_discussion_posts",
    "post_discussion_entry",
    "post_discussion_reply",
    "like_discussion_post",
    "like_all_discussion_posts",
    
]
