import os


def custom_context_processor(request):
    ACCEPTABLE_ENVIRONMENT_VALUES = ("dev", "qa", "prod")

    environment_value_from_dotenv = os.getenv("ENVIRONMENT")

    if environment_value_from_dotenv:
        environment_value_from_dotenv = environment_value_from_dotenv.strip('"').strip("'")

    if environment_value_from_dotenv not in ACCEPTABLE_ENVIRONMENT_VALUES:
        environment = "unknown"  # covers invalid values, and also None if env var is not set

    else:
        environment = environment_value_from_dotenv

    return {
        "DATABASE_NAME": os.getenv("DATABASE_NAME", "Unknown"),
        "ENVIRONMENT": environment,
    }
