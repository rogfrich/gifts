from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from .models import Wish  # Updated import to Wish

from .views import my_wishes, other_wishes, my_claims


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


class UrlViewTemplateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_url_view_template_wiring(self):
        """
        For each URL:
        1. Test if the URL can be reached and returns the correct status codes.
        2. Test if the correct templates is returned by the view.
        3. Test if the correct view are used.
        """
        response = self.client.get(reverse("my_wishes"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/my-wishes.html")
        found = resolve("/my-wishes/")
        self.assertEqual(found.func, my_wishes)

        response = self.client.get(reverse("other_wishes"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/other-wishes.html")
        found = resolve("/wishes/")
        self.assertEqual(found.func, other_wishes)

        response = self.client.get(reverse("my_claims"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/my-claims.html")
        found = resolve("/my-claims/")
        self.assertEqual(found.func, my_claims)


class AuthenticationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_login(self):
        """
        User should be able to log in successfully. and should be redirected to my_wishes.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)  # Redirect to my_wishes
        self.assertRedirects(response, "/my-wishes/")

    def test_logout(self):
        """
        User should be able to log out successfully. and should be redirected to login.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post("/logout/")
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, "/login/")

    def test_logged_in_user_access(self):
        """
        Logged-in user should be able to access all views.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/wishes/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/my-wishes/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/my-claims/")
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_access(self):
        """
        Logged-out user should be redirected to login page when trying to access views.
        """
        response = self.client.get("/wishes/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/wishes/")
        response = self.client.get("/my-wishes/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/my-wishes/")
        response = self.client.get("/my-claims/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/my-claims/")


class MyWishesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser1", password="testpassword"
        )
        self.client.login(username="testuser1", password="testpassword")
        for i in range(3):
            Wish.objects.create(
                user=self.user,
                title=f"User 1 - Test Wish {i}",
                detail=f"This is test wish {i}",
                link="https://www.example.com",
            )

        self.client.logout()

        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )
        self.client.login(username="testuser2", password="testpassword")
        for i in range(3):
            Wish.objects.create(
                user=self.user2,
                title=f"Test Wish User2 {i}",
                detail=f"This is test wish {i}",
                link="https://www.example.com",
            )
        self.client.logout()

    def test_my_wishes_context(self):
        """
        Test if the context of my_wishes view contains the correct wishes.
        """
        self.client.login(username="testuser1", password="testpassword")
        response = self.client.get(reverse("my_wishes"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["wishes"]), 3)
        for i in range(3):
            self.assertContains(response, f"User 1 - Test Wish {i}")


class LinkFieldBehaviourWithURLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.wish_with_link = Wish.objects.create(
            user=self.user,
            title="Test Wish",
            detail="A test wish a link",
            link="https://www.example.com",
        )

    def test_link_field_behaviour(self):
        """
        Test if the link field behaves correctly.
        """
        response = self.client.get(reverse("my_wishes"))
        self.assertContains(
            response, '<a href="https://www.example.com">Link</a>'
        )  # Check if the link is rendered correctly


class LinkFieldBehaviourWithoutURL(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.wish_without_link = Wish.objects.create(
            user=self.user,
            title="Test Wish",
            detail="A test wish without a link",
        )

    def test_link_field_behaviour(self):
        """
        Test if the link field behaves correctly when no URL is provided.
        """
        response = self.client.get(reverse("my_wishes"))
        self.assertContains(
            response, "<td>N/A</td>"
        )  # Check if the link is not rendered


class CreateWishViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_create_wish_get(self):
        """
        Test if the create_wish view returns the correct template.
        """
        response = self.client.get(reverse("create_wish"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/wish-form.html")

    def test_create_wish_post(self):
        """
        Test if the create_wish view creates a wish and redirects correctly.
        """
        response = self.client.post(
            reverse("create_wish"),
            {
                "title": "New Wish",
                "detail": "A new wish description",
                "link": "https://www.example.com",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect to my_wishes
        self.assertRedirects(response, "/my-wishes/")


class EditViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.wish = Wish.objects.create(
            user=self.user,
            title="Test Wish",
            detail="A test wish description",
            link="https://www.example.com",
        )

    def test_edit_wish_get(self):
        """
        Test if the edit_wish view returns the correct template.
        """
        response = self.client.get(reverse("edit_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/wish-form.html")
        self.assertContains(response, "Test Wish")
        self.assertContains(response, "A test wish description")
        self.assertContains(response, "https://www.example.com")

    def test_edit_wish_post(self):
        """
        Test if the edit_wish view updates the wish and redirects correctly.
        """
        response = self.client.post(
            reverse("edit_wish", args=[self.wish.id]),
            {
                "title": "Updated Wish",
                "detail": "An updated wish description",
                "link": "https://www.updated-example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/my-wishes/")

        # Check if the wish was updated
        self.wish.refresh_from_db()
        self.assertEqual(self.wish.title, "Updated Wish")
        self.assertEqual(self.wish.detail, "An updated wish description")
        self.assertEqual(self.wish.link, "https://www.updated-example.com")

    def test_edit_wish_not_owner(self):
        """
        Test if a user cannot edit a wish that they do not own.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.client.logout()
        self.client.login(username="otheruser", password="otherpassword")

        response = self.client.get(reverse("edit_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 404)


class DeleteWishTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.wish = Wish.objects.create(
            user=self.user,
            title="Test Wish",
            detail="A test wish description",
            link="https://www.example.com",
        )

    def test_delete_wish_get(self):
        """
        Test if the delete_wish view returns the correct template.
        """
        response = self.client.get(reverse("delete_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gifts/delete-wish.html")
        self.assertContains(response, "Are you sure you want to delete")
        self.assertContains(response, "Test Wish")
        self.assertContains(response, '<form method="post">')
        self.assertContains(response, '<button type="submit">Delete Wish</button>')

    def test_delete_wish_post(self):
        """
        Test if the delete_wish view deletes the wish and redirects correctly.
        """
        response = self.client.post(reverse("delete_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/my-wishes/")

        # Check if the wish was deleted
        with self.assertRaises(Wish.DoesNotExist):
            Wish.objects.get(id=self.wish.id)

    def test_delete_wish_not_owner(self):
        """
        Test if a user cannot delete a wish that they do not own.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.client.logout()
        self.client.login(username="otheruser", password="otherpassword")

        response = self.client.get(reverse("delete_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 404)

    def test_delete_wish_not_owner_post(self):
        """
        Test if a user cannot delete a wish that they do not own.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.client.logout()
        self.client.login(username="otheruser", password="otherpassword")

        response = self.client.post(reverse("delete_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 404)
        # Check if the wish still exists
        self.assertTrue(Wish.objects.filter(id=self.wish.id).exists())

class OtherWishesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        for i in range(3):
            Wish.objects.create(
                user=self.user,
                title=f"MY-WISH {i}",
                detail=f"This is test wish {i}",
                link="https://www.example.com",
            )

        self.client.logout()

        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )
        self.client.login(username="testuser2", password="testpassword")
        for i in range(3):
            Wish.objects.create(
                user=self.user2,
                title="OTHER-WISH",
                detail=f"ONLY IN OTHER WISHES {i}",
                link="https://www.example.com",
            )
        self.client.logout()

    def test_other_wishes_context(self):
        """
        Test that only wishes from other users are shown in the context of other_wishes view.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("other_wishes"))
        for i in range(3):
            self.assertContains(response, f"ONLY IN OTHER WISHES {i}")
        self.assertNotContains(response, "MY-WISH")