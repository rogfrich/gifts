import os
import csv
import tempfile
import shutil
from django.test import TestCase
from django.conf import settings
from dotenv import load_dotenv
from utils import exporter
from gifts.models import Wish
from django.contrib.auth.models import User

load_dotenv()



class TestExporterWritesFiles(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up shared temp directory
        cls.temp_dir = tempfile.mkdtemp()
        settings.EXPORT_PATH = cls.temp_dir
        cls.users_file = os.path.join(cls.temp_dir, "users.csv")
        cls.wishes_file = os.path.join(cls.temp_dir, "wishes.csv")

        # Create test users
        cls.user1 = User.objects.create(username="testuser1", password="password")
        cls.user2 = User.objects.create(username="testuser2", password="password")
        cls.user3 = User.objects.create(username="testuser3", password="password")

        # Create test wishes
        Wish.objects.create(
            user=cls.user1,
            title="Wish 1",
            detail="Detail 1",
            link="http://example.com/wish1",
            claimed=False,
            claimed_by=None,
        )
        Wish.objects.create(
            user=cls.user2,
            title="Wish 2",
            detail="Detail 2",
            link="http://example.com/wish2",
            claimed=True,
            claimed_by=cls.user1,
        )
        Wish.objects.create(
            user=cls.user3,
            title="Wish 3",
            detail="Detail 3",
            link="http://example.com/wish3",
            claimed=True,
            claimed_by=cls.user2,
        )

        # Run export once for all tests
        exporter.export_all(export_path=cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.temp_dir)

    def test_exported_files_exist(self):
        self.assertTrue(os.path.exists(self.users_file), "users.csv was not created.")
        self.assertTrue(os.path.exists(self.wishes_file), "wishes.csv was not created.")

    def test_users_csv_contents(self):
        with open(self.users_file, newline='') as csvfile:
            reader = list(csv.DictReader(csvfile))
            self.assertEqual(len(reader), 3)
            usernames = [row["username"] for row in reader]
            self.assertIn("testuser1", usernames)
            self.assertIn("testuser2", usernames)
            self.assertIn("testuser3", usernames)

    def test_wishes_csv_contents(self):
        with open(self.wishes_file, newline='') as csvfile:
            reader = list(csv.DictReader(csvfile))
            self.assertEqual(len(reader), 3)

            wishes_by_title = {row['title']: row for row in reader}

            wish1 = wishes_by_title.get("Wish 1")
            self.assertIsNotNone(wish1)
            self.assertEqual(wish1["user_id"], str(self.user1.id))
            self.assertEqual(wish1["claimed"], "False")
            self.assertEqual(wish1["claimed_by"], "")

            wish2 = wishes_by_title.get("Wish 2")
            self.assertIsNotNone(wish2)
            self.assertEqual(wish2["user_id"], str(self.user2.id))
            self.assertEqual(wish2["claimed"], "True")
            self.assertEqual(wish2["claimed_by"], str(self.user1.id))

            wish3 = wishes_by_title.get("Wish 3")
            self.assertIsNotNone(wish3)
            self.assertEqual(wish3["user_id"], str(self.user3.id))
            self.assertEqual(wish3["claimed"], "True")
            self.assertEqual(wish3["claimed_by"], str(self.user2.id))