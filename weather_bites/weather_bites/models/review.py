import logging
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from weather_bites.utils.logger import configure_logger

# Initialize the database instance
db = SQLAlchemy()

# Configure the logger
logger = logging.getLogger(__name__)
configure_logger(logger)


class Review(db.Model):

    """
    SQLAlchemy model for the Reviews table.

    Attributes:
        id (int): The primary key identifier for the review.
        name (str): The name of the item being reviewed.
        location (str): The location where the item was purchased.
        rating (int): The rating of the item or service (1-5).
        favorite (bool): Whether the item is a favorite.
        review (str): The review text provided by the user.
        deleted (bool): Indicates if the review is soft-deleted.
    """
     
    __tablename__ = 'ReviewsTable'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    location = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    favorite = db.Column(db.Boolean, default=False)
    review = db.Column(db.Text, nullable=True)
    deleted = db.Column(db.Boolean, default=False)

    def __init__(self, name, location, rating, favorite, review):

        """
        Initializes a Review instance.

        Args:
            name (str): The name of the item being reviewed.
            location (str): The location where the item was purchased.
            rating (int): The rating of the item or service (1-5).
            favorite (bool): Whether the item or service is a favorite.
            review (str): The review text provided by the user.

        Raises:
            ValueError: If the rating is not between 1 and 5.
        """

        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        self.name = name
        self.location = location
        self.rating = rating
        self.favorite = favorite
        self.review = review

    def mark_deleted(self):
        """
        Marks the review as soft-deleted by setting the 'deleted' attribute to True.
        """

        self.deleted = True

#helper functions
        
def create_review(name: str, location: str, rating: int, favorite: bool, review:str) -> None:

    """
    Creates a new review and saves it to the database.

    Args:
        name (str): The name of the item being reviewed.
        location (str): The location where the item was purchased.
        rating (int): The rating of the item or service (1-5).
        favorite (bool): Whether the item or service is a favorite.
        review (str): The review text provided by the user.

    Raises:
        ValueError: If the rating is invalid or the location is not in the allowed list.
        Exception: If there is a database error while saving the review.
    """

    valid_locations = [
        "1369 Coffee House (hot chocolate)", "Soup Shack", "1369 Coffee House",
        "Tatte", "Blank Street Coffee", "Pavement Coffeehouse",
        "Boba Tea and Snow Ice House", "Tiger Sugar", "Levain",
        "Fomu", "JP Licks", "Kyo Matcha"
    ]

    if rating < 1 or rating > 5:
        raise ValueError(f"Invalid rating: {rating}. Rating must be between 1 and 5.")
    if location not in valid_locations:
        raise ValueError(f"Invalid location: {location}. Must be one of {', '.join(valid_locations)}.")

    review_instance = Review(name=name, location=location, rating=rating, favorite=favorite, review=review)

    try:
        db.session.add(review_instance)
        db.session.commit()
        logger.info("Review successfully added to the database: %s", name)
    except Exception as e:
        db.session.rollback()
        logger.error("Error while adding review: %s", str(e))
        raise

def clear_reviews() -> None:
    """
    Deletes all reviews from the database.

    Raises:
        Exception: If there is a database error while deleting reviews.
    """
    try:
        Review.query.delete()
        db.session.commit()
        logger.info("All reviews cleared successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error("Error while clearing reviews: %s", str(e))
        raise
    
def delete_review(id: int) -> None:

    """
    Soft-deletes a review by marking it as deleted.

    Args:
        id (int): The ID of the review to delete.

    Raises:
        ValueError: If the review does not exist or has already been deleted.
        Exception: If there is a database error while marking the review as deleted.
    """

    review = Review.query.get(id)
    if not review:
        logger.info("Review with ID %s not found.", id)
        raise ValueError(f"Review with ID {id} not found.")
    if review.deleted:
        logger.info("Review with ID %s is already deleted.", id)
        raise ValueError(f"Review with ID {id} has already been deleted.")

    review.mark_deleted()
    try:
        db.session.commit()
        logger.info("Review with ID %s marked as deleted.", id)
    except Exception as e:
        db.session.rollback()
        logger.error("Error while deleting review: %s", str(e))
        raise
    
def get_favorites() -> List[Review]:
    """
    Retrieves all reviews marked as favorites from the database.

    Returns:
        List[Review]: A list of Review objects that are marked as favorites.

    Raises:
        Exception: If there is a database error while retrieving favorites.
    """
    try:
        favorites = Review.query.filter_by(favorite=True, deleted=False).all()
        logger.info("Retrieved %d favorite reviews.", len(favorites))
        return favorites
    except Exception as e:
        logger.error("Error while retrieving favorites: %s", str(e))
        raise
    
def get_review_by_id(id: int) -> Review:

    """
    Retrieves a review by its ID.

    Args:
        id (int): The ID of the review to retrieve.

    Returns:
        Review: The Review object matching the provided ID.

    Raises:
        ValueError: If the review does not exist or has been deleted.
    """

    review = Review.query.get(id)
    if not review or review.deleted:
        logger.info("Review with ID %s not found or deleted.", id)
        raise ValueError(f"Review with ID {id} not found or has been deleted.")
    if review.deleted:
        logger.info("Review with ID %s has been soft-deleted.", id)
        raise ValueError(f"Review with ID {id} has been deleted.")
    return review
    
    
def update_review(id: int, new_review: str) -> None:
    """
    Updates the review text for a specific review.

    Args:
        id (int): The ID of the review to update.
        new_review (str): The new review text.

    Raises:
        ValueError: If the review does not exist or has been deleted.
        Exception: If there is a database error while updating the review.
    """
    review = get_review_by_id(id)
    review.review = new_review
    try:
        db.session.commit()
        logger.info("Updated review text for ID %d.", id)
    except Exception as e:
        db.session.rollback()
        logger.error("Error while updating review: %s", str(e))
        raise
    
def update_rating(id: int, new_rating: int) -> None:
    """
    Updates the rating for a specific review.

    Args:
        id (int): The ID of the review to update.
        new_rating (int): The new rating (1-5).

    Raises:
        ValueError: If the rating is not between 1 and 5 or the review ID does not exist.
        Exception: If a database error occurs.
    """
    if not (1 <= new_rating <= 5):
        raise ValueError("Rating must be an integer between 1 and 5.")

    try:
        review = get_review_by_id(id)
        review.rating = new_rating
        db.session.commit()
        logger.info("Updated rating for ID %d to %d.", id, new_rating)
    except ValueError as ve:
        logger.error("Invalid ID provided: %s", str(ve))
        raise ve
    except Exception as e:
        db.session.rollback()
        logger.error("Error while updating rating: %s", str(e))
        raise


def update_favorite(id: int, is_favorite: bool) -> None:
    """
    Updates the favorite status for a specific review.

    Args:
        id (int): The ID of the review to update.
        is_favorite (bool): The new favorite status (True or False).

    Raises:
        Exception: If any database error occurs.
    """
    review = get_review_by_id(id)
    review.favorite = is_favorite
    try:
        db.session.commit()
        logger.info("Updated favorite status for ID %d to %s.", id, is_favorite)
    except Exception as e:
        db.session.rollback()
        logger.error("Error while updating favorite status: %s", str(e))
        raise