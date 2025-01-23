"""API client for Nemy."""
import aiohttp
import async_timeout
from datetime import datetime, timedelta
from collections import deque
import logging

_LOGGER = logging.getLogger(__name__)

class NemyApiError(Exception):
    """Exception for Nemy API errors."""

class NemyDataValidationError(NemyApiError):
    """Exception for data validation errors."""

class NemyRateLimitError(NemyApiError):
    """Exception for rate limit errors."""

class NemyApi:
    """Nemy API client."""

    REQUIRED_FIELDS = [
        "time_interval",
        "price_household",
        "price_dispatch",
        "price_percentile",
        "price_category",
        "renewables",
        "renewables_no_rooftop",
        "renewables_percentile",
        "renewables_category"
    ]

    VALID_PRICE_CATEGORIES = [
        "free",
        "cheap",
        "typical",
        "expensive",
        "spike"
    ]

    VALID_RENEWABLES_CATEGORIES = [
        "extremely green",
        "green",
        "typical",
        "polluting",
        "extremely polluting"
    ]

    def __init__(self, api_key: str, state: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._state = state
        self._session = session
        self._base_url = "https://nemy.p.rapidapi.com"
        
        # Rate limiting setup
        self._requests_per_minute = 30  # RapidAPI Basic tier limit
        self._requests_per_day = 1000   # RapidAPI Basic tier limit
        self._minute_requests = deque(maxlen=self._requests_per_minute)
        self._daily_requests = deque(maxlen=self._requests_per_day)

    def _validate_data(self, data: dict) -> None:
        """Validate the API response data.
        
        Args:
            data: The response data to validate
            
        Raises:
            NemyDataValidationError: If the data fails validation
        """
        # Check for required fields
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in data]
        if missing_fields:
            raise NemyDataValidationError(
                f"Missing required fields in API response: {', '.join(missing_fields)}"
            )

        # Validate price category
        if data["price_category"] not in self.VALID_PRICE_CATEGORIES:
            raise NemyDataValidationError(
                f"Invalid price category: {data['price_category']}"
            )

        # Validate renewables category
        if data["renewables_category"] not in self.VALID_RENEWABLES_CATEGORIES:
            raise NemyDataValidationError(
                f"Invalid renewables category: {data['renewables_category']}"
            )

        # Validate numeric fields
        numeric_fields = [
            "price_household",
            "price_dispatch",
            "price_percentile",
            "renewables",
            "renewables_no_rooftop",
            "renewables_percentile"
        ]
        
        for field in numeric_fields:
            try:
                value = float(data[field])
                # Basic range validation
                if field.endswith("_percentile") and not 0 <= value <= 100:
                    raise NemyDataValidationError(
                        f"Invalid percentile value for {field}: {value}"
                    )
                # Special handling for renewable fields
                if field == "renewables_no_rooftop":
                    if value < -1 or value > 100:
                        raise NemyDataValidationError(
                            f"Invalid percentage value for {field}: {value}"
                        )
                elif field.startswith("renewables"):
                    # Allow slightly negative values with -0.1 tolerance
                    if value < -0.1 or value > 100:
                        raise NemyDataValidationError(
                            f"Invalid percentage value for {field}: {value}"
                        )
                # Only validate household prices for negative values
                if field == "price_household" and value < 0:
                    raise NemyDataValidationError(
                        f"Invalid negative household price value: {value}"
                    )
            except (ValueError, TypeError):
                raise NemyDataValidationError(
                    f"Invalid numeric value for {field}: {data[field]}"
                )

    def _check_rate_limits(self) -> None:
        """Check if we're within rate limits.
        
        Raises:
            NemyRateLimitError: If rate limits would be exceeded
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        day_ago = now - timedelta(days=1)

        # Clean up old requests
        while self._minute_requests and self._minute_requests[0] < minute_ago:
            self._minute_requests.popleft()
        while self._daily_requests and self._daily_requests[0] < day_ago:
            self._daily_requests.popleft()

        # Check limits
        if len(self._minute_requests) >= self._requests_per_minute:
            retry_after = (self._minute_requests[0] + timedelta(minutes=1) - now).seconds
            raise NemyRateLimitError(
                f"Per-minute rate limit exceeded. Retry after {retry_after} seconds"
            )

        if len(self._daily_requests) >= self._requests_per_day:
            retry_after = (self._daily_requests[0] + timedelta(days=1) - now).seconds
            raise NemyRateLimitError(
                f"Daily rate limit exceeded. Retry after {retry_after} seconds"
            )

    def _record_request(self) -> None:
        """Record a successful API request."""
        now = datetime.now()
        self._minute_requests.append(now)
        self._daily_requests.append(now)

    async def get_current_summary(self) -> dict:
        """Get current summary data."""
        # Check rate limits before making request
        self._check_rate_limits()

        headers = {
            "x-rapidapi-key": self._api_key,
            "x-rapidapi-host": "nemy.p.rapidapi.com"
        }
        
        url = f"{self._base_url}/NEM/summary/current"
        params = {"state": self._state}

        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers, params=params) as response:
                    if response.status == 429:
                        raise NemyRateLimitError("RapidAPI rate limit exceeded")
                    if response.status != 200:
                        raise NemyApiError(f"API request failed with status {response.status}")
                    
                    data = await response.json()
                    self._validate_data(data)
                    
                    # Record successful request
                    self._record_request()
                    
                    return data
                    
        except Exception as err:
            if isinstance(err, (NemyApiError, NemyDataValidationError, NemyRateLimitError)):
                raise
            raise NemyApiError(f"Error communicating with API: {err}") from err