from .make_client import CanvasClient
import requests
import polars as pl
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_peers(client: CanvasClient, course_code: int):
    """
    Get all users enrolled in a Canvas course as a Polars DataFrame.
    
    This function retrieves all users (students, teachers, TAs, etc.) from a 
    specified Canvas course, handling pagination automatically to ensure all 
    users are retrieved.
    
    Args:
        client (CanvasClient): The Canvas API client instance with authentication.
        course_code (int): The Canvas course ID to retrieve users from.
    
    Returns:
        pl.DataFrame: A Polars DataFrame with the following columns:
            - course_id (int): The course ID
            - user_id (int): Unique user identifier
            - user_name (str): Full name of the user
            - user_date (date): Date when the user's Canvas account was created
            - user_type (str): Enrollment type (e.g., 'StudentEnrollment', 
              'TeacherEnrollment', 'TaEnrollment')
    
    Raises:
        PermissionError: If you don't have permission to access the course users.
            This typically occurs when you're not enrolled in the course.
        ValueError: If the course ID doesn't exist.
        Exception: For other API-related errors.
    
    Example:
```python
        client = CanvasClient(
            api_key="your_token",
            canvas_url="https://byui.instructure.com"
        )
        peers_df = get_peers(client, 396812)
        print(peers_df)
```
    
    Note:
        - Each user appears only once in the returned DataFrame, even if they
          have multiple enrollment types in the course.
        - The function automatically handles API pagination to retrieve all users.
        - You can typically only retrieve users from courses you're enrolled in.
    """
    url = f"{client.canvas_url}/api/v1/courses/{course_code}/users"  # Changed to /users
    
    params = {
        'per_page': 100,
        'include[]': 'enrollments',
    }
    
    all_users = []
    
    # Pagination loop
    # Pagination loop
    while url:
        response = requests.get(url, headers=client.headers, params=params)
        
        if response.status_code == 200:
            users = response.json()
            all_users.extend(users)
            
            # Check for next page
            if 'next' in response.links:
                url = response.links['next']['url']
                params = None
            else:
                url = None
        elif response.status_code == 403:
            raise PermissionError(f"Access denied to course {course_code}. You may not be enrolled in this course or lack permissions to view its users. In most cases, you may only see the users of classes you are currently taking.")
        elif response.status_code == 404:
            raise ValueError(f"Course {course_code} not found.")
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    
    # Prepare data for DataFrame
    data = []
    for user in all_users:
        user_id = user.get('id')
        user_name = user.get('name')
        user_date = user.get('created_at')
        
        enrollments = user.get('enrollments', [])
        for enrollment in enrollments:
            user_type = enrollment.get('type')
            
            data.append({
                'course_id': course_code,
                'user_id': user_id,
                'user_name': user_name,
                'user_date': user_date,
                'user_type': user_type
            })
    
    # Create Polars DataFrame
    df = pl.DataFrame(data)
    
    # Convert user_date to date only
    df = df.with_columns([
        pl.col('user_date').str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%S%z")
    ]).unique(subset=['user_id'])  
    
    return df  

def get_all_peers(client: CanvasClient, course_list: pl.Series, max_workers: int = 2, unique_per_course: bool = True):
    """
    Get peers from multiple courses concurrently.
    
    Args:
        client: CanvasClient instance
        course_list: Polars Series containing course IDs
        max_workers: Maximum number of concurrent threads (default: 2)
        unique_per_course: If True (default), each user appears once per course they're in.
                          If False, each user appears only once total.
    
    Returns:
        pl.DataFrame: Combined DataFrame of all peers from all courses
    """
    all_dfs = []
    failed_courses = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_course = {
            executor.submit(get_peers, client, course_id): course_id 
            for course_id in course_list
        }
        
        # Process completed tasks
        for future in as_completed(future_to_course):
            course_id = future_to_course[future]
            try:
                df = future.result()
                all_dfs.append(df)
                print(f"Successfully retrieved peers from course {course_id}")
            except PermissionError as e:
                print(f"Skipping course {course_id}: {e}")
                failed_courses.append(course_id)
            except Exception as e:
                print(f"Error with course {course_id}: {e}")
                failed_courses.append(course_id)
    
    # Combine all DataFrames
    if all_dfs:
        combined_df = pl.concat(all_dfs)
        
        # Remove duplicates based on flag
        if unique_per_course:
            # Each user appears once per course
            combined_df = combined_df.unique(subset=['course_id', 'user_id'])
            print(f"\nTotal unique user-course pairs: {len(combined_df)}")
        else:
            # Each user appears only once total
            combined_df = combined_df.unique(subset=['user_id'])
            print(f"\nTotal unique peers: {len(combined_df)}")
        
        if failed_courses:
            print(f"Failed courses: {failed_courses}")
        return combined_df
    else:
        print("No data retrieved from any courses")
        return pl.DataFrame()

    
    