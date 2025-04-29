import tempfile
import shutil
from django.test import TestCase
from django.contrib.auth import get_user_model
from gifts.models import Wish
from utils.exporter import export_all
from utils.importer import import_all, truncate_tables

User = get_user_model()


class TestImporter(TestCase):
    def setUp(self):
        # Create temporary directory for export files
        self.temp_dir = tempfile.mkdtemp()

        # Step 1: Create original users and wishes
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.user2 = User.objects.create_user(username="testuser2", password="password")
        self.user3 = User.objects.create_user(username="testuser3", password="password")

        Wish.objects.create(
            user=self.user1,
            title="Wish 1",
            detail="Detail 1",
            link="http://example.com/wish1",
            claimed=False,
        )
        Wish.objects.create(
            user=self.user2,
            title="Wish 2",
            detail="Detail 2",
            link="http://example.com/wish2",
            claimed=True,
            claimed_by=self.user1,
        )
        Wish.objects.create(
            user=self.user3,
            title="Wish 3",
            detail="Detail 3",
            link="http://example.com/wish3",
            claimed=True,
            claimed_by=self.user2,
        )

        # Step 2: Export the clean database
        export_all(export_path=self.temp_dir, verbose=False)

        # Step 3: CORRUPT the database AFTER export
        wish = Wish.objects.get(title="Wish 1")
        wish.title = "Corrupted Wish"
        wish.save()

        self.user1.delete()  # Delete one user to simulate data loss

        # Step 4: Now re-import (importer will expect clean environment)
        truncate_tables()
        import_all(source_folder=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_data_is_loaded(self):
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Wish.objects.count(), 3)

    def test_users_restored_with_correct_ids_and_fields(self):
        usernames = list(User.objects.values_list("username", flat=True))
        self.assertIn("testuser1", usernames)
        self.assertIn("testuser2", usernames)
        self.assertIn("testuser3", usernames)

    def test_wishes_restored_with_correct_relationships(self):
        wish1 = Wish.objects.get(title="Wish 1")
        self.assertEqual(wish1.user.username, "testuser1")
        self.assertFalse(wish1.claimed)
        self.assertIsNone(wish1.claimed_by)

        wish2 = Wish.objects.get(title="Wish 2")
        self.assertEqual(wish2.user.username, "testuser2")
        self.assertTrue(wish2.claimed)
        self.assertEqual(wish2.claimed_by.username, "testuser1")

        wish3 = Wish.objects.get(title="Wish 3")
        self.assertEqual(wish3.user.username, "testuser3")
        self.assertTrue(wish3.claimed)
        self.assertEqual(wish3.claimed_by.username, "testuser2")

    def test_import_fixes_corrupted_data(self):
        wish = Wish.objects.get(user__username="testuser1")
        self.assertEqual(wish.title, "Wish 1")  # Confirm it overwrote "Corrupted Wish"

    def test_truncate_tables_actually_deletes_data(self):
        truncate_tables()
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Wish.objects.count(), 0)

    def test_import_does_not_crash_on_valid_csv(self):
        try:
            import_all(source_folder=self.temp_dir)
        except Exception as e:
            self.fail(f"Import raised an unexpected exception: {e}")


