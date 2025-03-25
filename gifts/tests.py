from django.test import TestCase
from django.contrib.auth.models import User  # Import the User model
from .models import Gift  # Import the Wish model


class WishModelTest(TestCase):
    def setUp(self):
        # Create a sample Gift instance
        test_user = User.objects.create(
            username="test_user",
            
        )
        self.gift = Gift.objects.create(
            user=test_user,  # Replace with a valid User instance if needed
            title="Test gift",
            detail="A test wish description",
            link="https://www.example.com",

        )

    def test_gift_creation(self):
        # Test if the Wish instance is created successfully
        self.assertEqual(self.gift.title, "Test gift")
        self.assertEqual(self.gift.detail, "A test wish description")
        self.assertEqual(self.gift.link, "https://www.example.com")
        self.assertFalse(self.gift.claimed)
        self.assertEqual(self.gift.claimed_by, None)

    def test_gift_string_representation(self):
        # Test the string representation of the Wish model
        self.assertEqual(str(self.gift), "Test gift")
