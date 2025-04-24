"""
A utility script to export data from the database to CSV files. Primarily meant as a form of backup,
this can also be used to transfer data between different instances of the application.
"""

import argparse
import csv
import sys
import os
from pathlib import Path

import django

# Set the DJANGO_SETTINGS_MODULE environment variable. Needed because we are running this script outside of Django.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

django.setup()

from django.contrib.auth.models import User
from gifts.models import Wish







def export_users(export_path):
    """
    Export all users to a CSV file.
    """
    users = User.objects.all()
    with open(os.path.join(export_path, "users.csv"), "w", newline="") as csvfile:
        fieldnames = ["id", "username", "email"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for user in users:
            writer.writerow(
                {"id": user.id, "username": user.username, "email": user.email}
            )
    print(f"Exported {users.count()} users to {os.path.join(export_path, 'users.csv')}")


def export_wishes(export_path):
    """
    Export all wishes to a CSV file.
    """
    wishes = Wish.objects.all()
    with open(os.path.join(export_path, "wishes.csv"), "w", newline="") as csvfile:
        fieldnames = [
            "id",
            "user_id",
            "title",
            "detail",
            "link",
            "created_at",
            "claimed",
            "claimed_by",
            "updated_at",
        ]
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC
        )

        writer.writeheader()
        for wish in wishes:
            writer.writerow(
                {
                    "id": wish.id,
                    "user_id": wish.user.id,
                    "title": wish.title,
                    "detail": wish.detail,
                    "link": wish.link,
                    "created_at": wish.created_at,
                    "claimed": wish.claimed,
                    "claimed_by": wish.claimed_by.id if wish.claimed_by else "",
                    "updated_at": wish.updated_at,
                }
            )
    print(
        f"Exported {wishes.count()} wishes to {os.path.join(export_path, 'wishes.csv')}"
    )


def export_all(export_path):
    """
    Export all data to CSV files.
    """
    export_users(export_path)
    export_wishes(export_path)
    print("Exported all data.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "export_path", help="Path to the directory where the CSV files will be saved."
    )
    args = parser.parse_args()
    export_path = args.export_path
    # Check if the export path exists, if not create it
    if not os.path.exists(export_path):
        os.makedirs(export_path)
        print(f"Created directory: {export_path}")

    export_all(export_path)
