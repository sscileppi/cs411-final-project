import unittest
from weather_bites.models.review import Review, create_review, get_review_by_id, delete_review, get_favorites, update_review, update_rating, update_favorite, clear_reviews
from weather_bites.models.db import db
from app import app

class ReviewModelTestCase(unittest.TestCase):
    """
    Unit test suite for the Review model and its helper functions.
    """

    def setUp(self):
        """
        Set up the test environment before each test.
        """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite database
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.init_app(app)
            db.create_all()

    def tearDown(self):
        """
        Clean up the test environment after each test.
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_review(self):
        """
        Test creating a new review and saving it to the database.
        """
        with app.app_context():
            create_review(
                name="Hot Chocolate",
                location="1369 Coffee House",
                rating=5,
                favorite=True,
                review="Best hot chocolate ever!"
            )
            review = Review.query.filter_by(name="Hot Chocolate").first()
            self.assertIsNotNone(review)
            self.assertEqual(review.name, "Hot Chocolate")
            self.assertEqual(review.location, "1369 Coffee House")
            self.assertEqual(review.rating, 5)
            self.assertTrue(review.favorite)

    def test_invalid_rating(self):
        """
        Test that creating a review with an invalid rating raises a ValueError.
        """
        with app.app_context():
            with self.assertRaises(ValueError):
                create_review(
                    name="Bad Rating Test",
                    location="Soup Shack",
                    rating=6,  # Invalid rating
                    favorite=False,
                    review="Testing invalid rating."
                )

    def test_get_review_by_id(self):
        """
        Test retrieving a review by its ID.
        """
        with app.app_context():
            create_review(
                name="Sample Review",
                location="Tatte",
                rating=4,
                favorite=False,
                review="Great ambiance!"
            )
            review = Review.query.filter_by(name="Sample Review").first()
            retrieved_review = get_review_by_id(review.id)
            self.assertEqual(retrieved_review.name, "Sample Review")

    def test_delete_review(self):
        """
        Test soft-deleting a review.
        """
        with app.app_context():
            create_review(
                name="Delete Test",
                location="Tiger Sugar",
                rating=5,
                favorite=True,
                review="Best boba ever!"
            )
            review = Review.query.filter_by(name="Delete Test").first()
            delete_review(review.id)
            deleted_review = Review.query.get(review.id)
            self.assertTrue(deleted_review.deleted)

    def test_get_favorites(self):
        """
        Test retrieving all reviews marked as favorites.
        """
        with app.app_context():
            create_review(
                name="Favorite 1",
                location="Levain",
                rating=5,
                favorite=True,
                review="Delicious cookies!"
            )
            create_review(
                name="Favorite 2",
                location="Fomu",
                rating=4,
                favorite=True,
                review="Great vegan ice cream."
            )
            favorites = get_favorites()
            self.assertEqual(len(favorites), 2)
            self.assertEqual(favorites[0].name, "Favorite 1")
            self.assertEqual(favorites[1].name, "Favorite 2")

    def test_update_review(self):
        """
        Test updating a review's text.
        """
        with app.app_context():
            create_review(
                name="Update Test",
                location="Blank Street Coffee",
                rating=3,
                favorite=False,
                review="Decent coffee."
            )
            review = Review.query.filter_by(name="Update Test").first()
            update_review(review.id, "Changed my mind, it's great!")
            updated_review = get_review_by_id(review.id)
            self.assertEqual(updated_review.review, "Changed my mind, it's great!")

    def test_update_rating(self):
        """
        Test updating a review's rating.
        """
        with app.app_context():
            create_review(
                name="Rating Test",
                location="Pavement Coffeehouse",
                rating=3,
                favorite=False,
                review="Mediocre coffee."
            )
            review = Review.query.filter_by(name="Rating Test").first()
            update_rating(review.id, 5)
            updated_review = get_review_by_id(review.id)
            self.assertEqual(updated_review.rating, 5)

    def test_update_favorite(self):
        """
        Test updating the favorite status of a review.
        """
        with app.app_context():
            create_review(
                name="Favorite Test",
                location="Kyo Matcha",
                rating=4,
                favorite=False,
                review="Good matcha!"
            )
            review = Review.query.filter_by(name="Favorite Test").first()
            update_favorite(review.id, True)
            updated_review = get_review_by_id(review.id)
            self.assertTrue(updated_review.favorite)


if __name__ == "__main__":
    unittest.main()

