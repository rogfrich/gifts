import os

def custom_context_processor(request):
    return {
        "DATABASE_NAME": os.getenv("DATABASE_NAME", "Unknown"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "Unknown")
    }


