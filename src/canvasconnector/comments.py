from .make_client import CanvasClient
import polars as pl
import requests 

def get_submission_comments(client: CanvasClient, course_id: int, assignment_id: int):
    url = f"{client.canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{client.user_id}"
    
    params = {"include[]": "submission_comments"}
    
    response = requests.get(url, headers=client.headers, params=params)
    comments = response.json().get("submission_comments", [])
    
    if not comments:
        return pl.DataFrame()
    
    return pl.DataFrame(comments, strict=False).select([
        pl.col("id").alias("comment_id"),
        pl.col("author_name"),
        pl.col("comment"),
        pl.col("created_at")
    .str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%SZ", strict=False)
    .dt.replace_time_zone("UTC")
    .dt.convert_time_zone(client.timezone)
    .alias("created_at"),
    pl.col("author_id").cast(pl.Int64).alias("author_id"),
    (pl.col("author_id") == client.user_id).alias("is_mine"),
    ])


def post_submission_comment(client: CanvasClient, course_id: int, assignment_id: int, comment: str):
    url = f"{client.canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{client.user_id}"
    
    payload = {"comment": {"text_comment": comment}}
    
    response = requests.put(url, headers=client.headers, json=payload)
    
    if response.status_code == 200:
        print("✓ Comment posted successfully")
        return True
    else:
        raise Exception(f"Failed to post comment: {response.status_code}: {response.text}")