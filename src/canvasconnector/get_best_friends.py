from .make_client import CanvasClient
import polars as pl


def get_best_friends(
    client: CanvasClient,
    peers_df: pl.DataFrame,
    top_n: int = 10,
    students_only: bool = False,
):
    """Find the people you share the most classes with.

                This function analyzes peer data to identify which users appear in the
                most courses with you, helping you identify your "best friends" or most
                frequent classmates.

                Args:
                    peers_df (pl.DataFrame): DataFrame from get_all_peers() containing peer data.
                    client (CanvasClient): Canvas client instance (used to exclude yourself).
                    top_n (int): Number of top results to return (default: 10).
                    students_only (bool): Whether or not to exclude teachers and TAs from the count.

                Returns:
                    pl.DataFrame: A DataFrame with columns:
                        - user_name (str): Name of the peer
                        - shared_courses (int): Number of courses shared with this person
                        Sorted by shared_courses in descending order.

                Example:
    ```python
                    peers_df = get_all_peers(client, course_list)
                    best_friends = get_best_friends(peers_df, client, top_n=5)
                    print(best_friends)
            ```
    """
    # Take out the user from the counts
    filtered_df = peers_df.filter(pl.col("user_name") != client.user_name)

    # Remove Teachers or TAs depending on settings
    if students_only:
        filtered_df = filtered_df.filter(pl.col("user_type") == "StudentEnrollment")

    return (
        filtered_df.group_by(["user_id", "user_name"])
        .agg(pl.len().alias("shared_courses"))
        .sort("shared_courses", descending=True)
        .head(top_n)
    )
