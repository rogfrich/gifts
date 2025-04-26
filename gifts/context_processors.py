import dotenv
import os

dotenv.load_dotenv()

def custom_context_processor(request):
    return {
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT")
    }


