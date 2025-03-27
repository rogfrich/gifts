"""
This script is one time use script to import data from the old Anvil app to the Django app. The data from Anvil was downloaded as CSV,
and loaded into the local dev instance of the Django Gifts app.

The script reads the CSV file, and for each row, it creates a new Wish object in the Django app using the Django ORM API.

This was successfully run on 2021-03-27. While the script may be useful as a reference, it is not intended to be run again until it 
is needed to import data into the eventual production app. 
"""

import csv
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable. Needed because we are running this script outside of Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django. Needed because we are running this script outside of Django.
django.setup()

from django.contrib.auth.models import User
from gifts.models import Wish


# The Anvil data identifies users by an obscure DB reference. This mapping is used to map the user ID to the username in the Django app.
USER_MAPPING = {
    "[539608,853743788]": "Adele",
    "[539608,855462803]": "Maureen",
    "[539608,853806408]": "Codey",
    "[539608,855566160]": "Max",
    "[539608,1787527993]": "Chloe",
    "[539608,853806251]": "Minerva",
    "[539608,853710915]": "Rich",
    "[539608,853770845]": "Martin",
}
 

def get_mapped_user(user_id):
    return USER_MAPPING.get(user_id)

# Note that the .local directory is in the .gitignore file, so this file will not be committed to the repo.
PATH_TO_DATA = "./local/anvil_export_wishes.csv"

# Read the CSV file and create a new Wish object for each row.
with open(PATH_TO_DATA) as fin:
    reader = csv.reader(fin)
    for index, row in enumerate(reader):
        if index == 0:
            continue # Skip header
        userID = row[1][4:]
     
        claimed_column = row[6]
        if claimed_column == "1":
            claimed = True
            claimer = get_mapped_user(row[7][4:])
            django_claimer = User.objects.get(username=claimer)

        elif claimed_column == "0":
            claimed = False
            django_claimer = None
        else:
            raise ValueError("Invalid value for claimed column")
        
        user = get_mapped_user(userID)
        django_user = User.objects.get(username=user)

        
        data_to_load_into_wishes_table = {
            "user": django_user,
            "title": row[2],
            "detail": row[3],
            "link": row[4],
            "claimed": claimed,
            "claimed_by": django_claimer,
        }
        try:
            Wish.objects.create(**data_to_load_into_wishes_table)
        except Exception as e:
            print(f"Error with row: {row}")
            print(e)
            input("Press enter to continue")




