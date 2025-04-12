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

        self.user_with_no_wishes = User.objects.create_user(
            username="testuser3", password="testpassword"
        )
    def test_no_wishes_gives_message_not_table(self):
        """
        Test if the my_wishes view returns a message when there are no wishes.
        """
        self.client.login(username="testuser3", password="testpassword")
        response = self.client.get(reverse("my_wishes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have no wishes.")
        self.assertNotContains(response, "<table>")
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

        # Create a user with no wishes
        self.user3 = User.objects.create_user(
            username="testuser3", password="testpassword"
        )
        self.no_wish_user_id = self.user3.id

    def test_other_wishes_no_wishes(self):
        """
        Test if the other_wishes view returns a message when there are no wishes.
        """
        self.client.login(username="testuser", password="testpassword")


        response = self.client.get(
            reverse("other_wishes") + f"?recipient_id={self.no_wish_user_id}"
        )
        self.assertContains(response, "No wishes available.")
        self.assertNotContains(response, "<table>")
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

class ClaimUnclaimWishTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="otheruser", password="otherpassword")

        self.wish = Wish.objects.create(
            user=self.user2,
            title="Other User's Wish",
            detail="A test wish description",
            link="https://www.example.com",
        )

    def test_claim_and_unclaim(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(reverse("claim_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 302)

        wish = Wish.objects.get(id=self.wish.id)
        self.assertTrue(wish.claimed)
        self.assertEqual(wish.claimed_by, self.user1)

        response = self.client.post(reverse("unclaim_wish", args=[self.wish.id]))
        self.assertEqual(response.status_code, 302)

        wish.refresh_from_db()
        self.assertFalse(wish.claimed)
        self.assertIsNone(wish.claimed_by)


class TemplateUsesCorrectURLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        Wish.objects.create(
            user=self.user,
            title=f"MY-WISH",
            detail=f"This is a test wish",
            link="https://www.example.com",
        )

        self.client.logout()

        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )

        self.user3 = User.objects.create_user(
            username="testuser3", password="testpassword"
        )
 
    def test_template_uses_correct_url(self):
        """
        Test if the template uses the correct URL or placeholder text for the edit and delete function.
        """
        wish = Wish.objects.all().first()
        self.client.login(username="testuser2", password="testpassword")
        response = self.client.get(reverse("other_wishes"))
        self.assertContains(response, '<button type="submit">CLAIM</button>')
        self.client.post(reverse("claim_wish", args=[wish.id]))
        response = self.client.get(reverse("other_wishes"))
        self.assertContains(response, '<button type="submit">UNCLAIM</button>')
        self.client.logout()
        self.client.login(username="testuser3", password="testpassword")
        response = self.client.get(reverse("other_wishes"))
        self.assertContains(response, 'CLAIMED')


class OtherWishFilteringTest(TestCase):
    def setUp(self):
        for i in range(3):
            user = User.objects.create_user(
                username=f"testuser{i}", password="testpassword"
            )
            self.client.login(username=f"testuser{i}", password="testpassword")
            Wish.objects.create(
                user=user,
                title=f"Wish for testuser{i}",
                detail=f"This is test wish {i}",
                link="https://www.example.com",
            )
            self.client.logout()

    def test_other_wishes_filtering_default(self):
        """
        Test if the other_wishes view defaults to returning all other users' wishes.
        """
        # We should initially get all other users' wishes but not the logged in user's
        self.client.login(username="testuser0", password="testpassword")
        response = self.client.get(reverse("other_wishes"))
        self.assertContains(response, "Wish for testuser1")
        self.assertContains(response, "Wish for testuser2")
        self.assertNotContains(response, "Wish for testuser0")

    def test_other_wishes_filtering_by_recipient(self):
        """
        Test if the other_wishes view filters by recipient_id correctly.
        """
        self.client.login(username="testuser0", password="testpassword")

        # Here we want testuser1's wishes only. The others should be filtered.
        # testuser0's should be filtered because they are the logged in user.
        # testuser2's should be filtered because they are not the selected recipient.
        user_id = User.objects.get(username="testuser1").id
        base_url = reverse("other_wishes")
        query_string = f"?recipient_id={user_id}"
        full_url = f"{base_url}{query_string}"
        filtered_response = self.client.get(full_url)
        self.assertNotContains(filtered_response, "Wish for testuser0")
        self.assertContains(filtered_response, "Wish for testuser1")
        self.assertNotContains(filtered_response, "Wish for testuser2")

        
class InvalidClaimTest(TestCase):
    def setUp(self):
        # Create three users: one wish owner, one valid claimer, one intruder
        self.owner = User.objects.create_user(username="owner", password="testpassword")
        self.claimer = User.objects.create_user(username="claimer", password="testpassword")
        self.intruder = User.objects.create_user(username="intruder", password="testpassword")

        # Owner's wish (initially unclaimed)
        self.own_wish = Wish.objects.create(
            user=self.owner,
            title="Owner's Wish",
            detail="Should not be claimable by the owner",
        )

        # Another wish that is already claimed by 'claimer'
        self.claimed_wish = Wish.objects.create(
            user=self.owner,
            title="Claimed Wish",
            detail="Already claimed",
            claimed=True,
            claimed_by=self.claimer,
        )

    def test_cannot_claim_own_wish(self):
        """
        Ensure a user cannot claim their own wish.
        """
        self.client.login(username="owner", password="testpassword")
        response = self.client.post(reverse("claim_wish", args=[self.own_wish.id]))
        self.assertEqual(response.status_code, 404)

        # Confirm it wasn't claimed
        self.own_wish.refresh_from_db()
        self.assertFalse(self.own_wish.claimed)
        self.assertIsNone(self.own_wish.claimed_by)

    def test_cannot_claim_wish_already_claimed_by_another_user(self):
        """
        Ensure a user cannot claim a wish that has already been claimed by someone else.
        """
        self.client.login(username="intruder", password="testpassword")
        response = self.client.post(reverse("claim_wish", args=[self.claimed_wish.id]))
        self.assertEqual(response.status_code, 404)

        # Confirm claim was not overwritten
        self.claimed_wish.refresh_from_db()
        self.assertTrue(self.claimed_wish.claimed)
        self.assertEqual(self.claimed_wish.claimed_by, self.claimer)
