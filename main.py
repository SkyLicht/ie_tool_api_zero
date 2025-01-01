import json
from datetime import datetime, timezone

from core.auth.auth_utils import generate_custom_id

if __name__ == "__main__":
    print(datetime.now(timezone.utc))
