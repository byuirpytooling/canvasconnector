import requests


class CanvasClient:
    def __init__(
        self,
        api_key: str,
        canvas_url: str,
        timezone: str = "UTC",
        verify_connection: bool = True,
    ):
        """
        Initialize Canvas API client.

        Args:
            api_key: Your Canvas API token
            canvas_url: Your Canvas instance URL (e.g., 'https://canvas.instructure.com')
            timezone: IANA timezone string (e.g., 'America/Denver'). Default: 'UTC'
            verify_connection: If True, verify the connection on initialization (default: True)
        """
        self.canvas_url = canvas_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.timezone = timezone
        self.user_name = None
        self.user_id = None

        if verify_connection:
            self.test_connection()

    def __repr__(self):
        return f"CanvasClient(url={self.canvas_url}, user={self.user_name}, user_id={self.user_id})"

    def test_connection(self) -> bool:
        """
        Test if the Canvas API connection is working and store user info.

        Returns:
            bool: True if connection is successful, False otherwise.

        Raises:
            Exception: If there's a connection error with details.
        """
        try:
            response = requests.get(
                f"{self.canvas_url}/api/v1/users/self", headers=self.headers
            )

            if response.status_code == 200:
                user_data = response.json()
                self.user_name = user_data.get("name")
                self.user_id = user_data.get("id")
                print(f"✓ Connected successfully as: {self.user_name}")
                return True
            elif response.status_code == 401:
                raise Exception("Authentication failed. Check your API key.")
            else:
                raise Exception(
                    f"Connection failed with status {response.status_code}: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")
