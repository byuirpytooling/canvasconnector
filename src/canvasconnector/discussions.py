from .make_client import CanvasClient
import polars as pl
import requests
from bs4 import BeautifulSoup
import random

#### GET ####

def get_discussions(client: CanvasClient, course_id: int) -> pl.DataFrame:
    response = requests.get(
        f"{client.canvas_url}/api/v1/courses/{course_id}/discussion_topics",
        headers=client.headers,
        params={"per_page": 100},
    )
    response.raise_for_status()
    topics = response.json()

    if not topics:
        return pl.DataFrame()

    records = [
        {
            "discussion_id": t.get("id"),
            "title": t.get("title"),
            "message": BeautifulSoup(t.get("message", ""), "html.parser").get_text(),
            "discussion_type": t.get("discussion_type"),
            "posted_at": t.get("posted_at"),
            "last_reply_at": t.get("last_reply_at"),
            "unread_count": t.get("unread_count"),
            "read_state": t.get("read_state"),
            "require_initial_post": t.get("require_initial_post", False),
            "locked": t.get("locked", False),
            "pinned": t.get("pinned", False),
            "assignment_id": t.get("assignment_id"),
            "is_graded": t.get("assignment_id") is not None,
        }
        for t in topics
    ]

    return pl.DataFrame(records)

def get_discussion_entries(client: CanvasClient, course_id: int, discussion_id: int) -> pl.DataFrame:
    response = requests.get(
        f"{client.canvas_url}/api/v1/courses/{course_id}/discussion_topics/{discussion_id}/entries",
        headers=client.headers,
        params={"per_page": 100},
    )
    response.raise_for_status()
    entries = response.json()

    if not entries:
        return pl.DataFrame()

    records = [
        {
            "entry_id": e.get("id"),
            "user_id": e.get("user_id"),
            "user_name": e.get("user_name"),
            "message": BeautifulSoup(e.get("message", ""), "html.parser").get_text(),
            "created_at": e.get("created_at"),
            "updated_at": e.get("updated_at"),
            "reply_count": len(e.get("recent_replies", [])),
            "has_more_replies": e.get("has_more_replies", False),
            "rating_count": e.get("rating_count") or 0,
            "read_state": e.get("read_state"),
        }
        for e in entries
    ]

    return pl.DataFrame(records)

def get_discussion_replies(client: CanvasClient, course_id: int, discussion_id: int, entry_id: int) -> pl.DataFrame:
    response = requests.get(
        f"{client.canvas_url}/api/v1/courses/{course_id}/discussion_topics/{discussion_id}/entries/{entry_id}/replies",
        headers=client.headers,
        params={"per_page": 100},
    )
    response.raise_for_status()
    replies = response.json()

    if not replies:
        return pl.DataFrame()

    records = [
        {
            "reply_id": r.get("id"),
            # parent_id is almost always entry_id. If there is a threaded discussion board, it will prove useful.
            # "parent_id": entry_id,
            "user_id": r.get("user_id"),
            "user_name": r.get("user_name"),
            "message": BeautifulSoup(r.get("message", ""), "html.parser").get_text(),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
            "rating_count": r.get("rating_count") or 0,
            "read_state": r.get("read_state"),
        }
        for r in replies
    ]

    return pl.DataFrame(records)


def get_all_discussion_posts(client: CanvasClient, course_id: int, discussion_id: int) -> pl.DataFrame:
    entries = get_discussion_entries(client, course_id, discussion_id)
    
    if entries.is_empty():
        return pl.DataFrame()
    
    entries = entries.with_columns(
        pl.lit(course_id).alias("course_id"),
        pl.lit(discussion_id).alias("discussion_id"),
        pl.lit(None, dtype=pl.Int64).alias("reply_id"),
    )
    
    all_replies = []
    for entry_id in entries["entry_id"].to_list():
        replies = get_discussion_replies(client, course_id, discussion_id, entry_id)
        if not replies.is_empty():
            replies = replies.with_columns(
                pl.lit(course_id).alias("course_id"),
                pl.lit(discussion_id).alias("discussion_id"),
                pl.lit(entry_id).alias("entry_id"),
            )
            all_replies.append(replies)
    
    if not all_replies:
        return entries
    
    replies_df = pl.concat(all_replies)
    return pl.concat([entries, replies_df], how="diagonal_relaxed")


#### POST ####

def post_discussion_entry(client: CanvasClient, course_id: int, discussion_id: int, message: str) -> dict:
    response = requests.post(
        f"{client.canvas_url}/api/v1/courses/{course_id}/discussion_topics/{discussion_id}/entries",
        headers=client.headers,
        json={"message": message},
    )
    response.raise_for_status()
    return response.json()


def post_discussion_reply(client: CanvasClient, course_id: int, discussion_id: int, entry_id: int, message: str) -> dict:
    response = requests.post(
        f"{client.canvas_url}/api/v1/courses/{course_id}/discussion_topics/{discussion_id}/entries/{entry_id}/replies",
        headers=client.headers,
        json={"message": message},
    )
    response.raise_for_status()
    return response.json()


def like_discussion_post(client: CanvasClient, course_id: int, discussion_id: int, post_id: int) -> None:
    '''
    Needs course_id, disscussion_id, and post_id. Post_id can be a entry_id or a reply_id. It works the same for either
    '''
    response = requests.post(
        f"{client.canvas_url}/api/v1/courses/{course_id}/discussion_topics/{discussion_id}/entries/{post_id}/rating",
        headers=client.headers,
        json={"rating": 1},
    )
    response.raise_for_status()


def like_all_discussion_posts(client: CanvasClient, posts: pl.DataFrame, probability: float = 0.25) -> None:
    discussion_id = posts["discussion_id"][0]
    course_id = posts["course_id"][0]
    
    for _, row in posts.iter_rows(named=True):
        post_id = row["reply_id"] if row["reply_id"] is not None else row["entry_id"]
        if random.random() < probability:
            like_discussion_post(client, course_id, discussion_id, post_id)


#### UPDATE ####
'''
TODO: Let users update their own posts. This can be done easily as each post has a user_id and canvas client stores their user id too
'''



#### DELETE ####
'''
TODO: Similar to update, but more perminant >:). I don't think this one is super important, but maybe it can help if you posted the same thing twice.
You would be able to delete all but the first one by wrangling and mapping this funciton. 
Could be useful for automated pulls...
'''