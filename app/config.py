import os


PARTS_SOFT_API_KEYS = {
    os.getenv("PARTS_SOFT_API_KEY", "test_static_key_very_long_random"): {
        "customer_id": int(os.getenv("PARTS_SOFT_CUSTOMER_ID", "5124")),
    }
}

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
