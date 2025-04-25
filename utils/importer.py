"""
Import data from CSV files into the database.

Usage: python importer.py <source_folder> [--truncate]
Source folder should contain two CSV files: 'users.csv' and 'wishes.csv'.
If the --truncate flag is set, all tables will be truncated before importing data.


"""

import sys
import os
from pathlib import Path
import argparse
import csv
import secrets


import django

# Set the DJANGO_SETTINGS_MODULE environment variable. Needed because we are running this script outside of Django.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

django.setup()

from gifts.models import Wish
from django.contrib.auth.models import User


def truncate_tables():
    """
    Truncate all tables in the database.
    """
    User.objects.all().delete()
    Wish.objects.all().delete()
    print("Truncated all tables.")


def import_users(source_folder):
    """
    Import users from a CSV file into the database.
    """
    import_user_file = os.path.join(source_folder, "users.csv")
    print(f"Importing users from {import_user_file}")
    with open(import_user_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
            )
            random_password = secrets.token_urlsafe(16)
            print(f"Generated password for {row['username']}: {random_password}")
            user.set_password(random_password)
            user.save()

    print(f"Imported {User.objects.count()} users.")


def import_wishes(source_folder):
    """
    Import wishes from a CSV file into the database.
    """
    import_wishes_file = os.path.join(source_folder, "wishes.csv")
    print(f"Importing wishes from {import_wishes_file}")
    with open(import_wishes_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Wish.objects.create(
                user_id=row["user_id"],
                title=row["title"],
                detail=row["detail"],
                link=row["link"],
                claimed=row["claimed"].lower() == "true",
                claimed_by_id=row["claimed_by"] if row["claimed_by"] else None,
            )
    print(f"Imported {Wish.objects.count()} wishes.")


def import_all(source_folder):
    """
    Import all data from CSV files into the database.
    """
    import_users(source_folder)
    import_wishes(source_folder)
    print("Imported all data.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_folder", help="Path to the directory containing CSV files to import."
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate all tables before importing data.",
    )
    args = parser.parse_args()
    if args.truncate:
        truncate_tables()
    
    source_folder = args.source_folder
    import_all(source_folder)
