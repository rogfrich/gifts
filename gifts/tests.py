from django.test import TestCase
from django.contrib.auth.models import User
from .models import Wish  # Updated import to Wish

class WishModelTest(TestCase):  # Updated class name
    def setUp(self):
        test_user = User.objects.create(username="test_user")
        self.wish = Wish.objects.create(  # Updated to Wish
            user=test_user,
            title="Test wish",
            detail="A test wish description",
            link="https://www.example.com",
        )

    def test_wish_creation(self):  # Updated method name
        self.assertEqual(self.wish.title, "Test wish")
        self.assertEqual(self.wish.detail, "A test wish description")
        self.assertEqual(self.wish.link, "https://www.example.com")
        self.assertFalse(self.wish.claimed)
        self.assertEqual(self.wish.claimed_by, None)

    def test_wish_string_representation(self):  # Updated method name
        self.assertEqual(str(self.wish), "Test wish")
