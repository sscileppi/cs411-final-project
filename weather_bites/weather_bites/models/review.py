from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any

from weather_bites.utils.sql_utils import get_db_connection
from weather_bites.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Review:
    id: int
    name: str #what was purchased
    location: str #where it was purchased
    rating: int #rating from 1-5
    favorite: bool #whether it's a favorite or not
    review: str #review of restaurant/purchase

    def __post_init__(self):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("Rating must be from 1-5")
        if self.favorite != True and self.favorite != False:
            raise ValueError("Review must be either added to favorites (True) or not added (False).")
        
def create_review(name: str, location: str, rating: int, favorite: bool, review:str) -> None:
    if not isinstance(rating, int):
        raise ValueError(f"Invalid rating: {rating}. Rating must be an integer from 1-5.")
    if rating < 1 or rating > 5:
        raise ValueError(f"Invalid number: {rating}. Rating must be from 1-5.")
    if location not in ["1369 Coffee House (hot chocolate)", "Soup Shack", "1369 Coffee House", "Tatte", "Blank Street Coffee", "Pavement Coffeehouse", "Boba Tea and Snow Ice House", "Tiger Sugar", "Levain", "Fomu", "JP Licks", "Kyo Matcha"]:
        raise ValueError(f"Invalid location: {location}. Must be a restaurant from the following: 1369 Coffee House (hot chocolate), Soup Shack, 1369 Coffee House, Tatte, Blank Street Coffee, Pavement Coffeehouse, Boba Tea and Snow Ice House, Tiger Sugar, Levain, Fomu, JP Licks, Kyo Matcha")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ReviewsTable (name, location, rating, favorite, review) VALUES (?, ?, ?, ?, ?)
            """, (name, location, rating, favorite, review))
            conn.commit()

            logger.info("Review successfully added to the database: %s", name)
    
    except sqlite3.IntegrityError:
        logger.error("Duplicate snack name: %s", name)
        raise ValueError(f"Snack with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def clear_reviews() -> None:
    """
    Recreates the reviews table, effectively deleting all reviews.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "/app/sql/create_snack_review_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Reviews cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing reviews: %s", str(e))
        raise e
    
def delete_review(id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM ReviewsTable WHERE id = ?", (id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Review with ID %s has already been deleted", id)
                    raise ValueError(f"Review with ID {id} has been deleted")
            except TypeError:
                logger.info("Review with ID %s not found", id)
                raise ValueError(f"Review with ID {id} not found")

            cursor.execute("UPDATE ReviewsTable SET deleted = TRUE WHERE id = ?", (id,))
            conn.commit()

            logger.info("Review with ID %s marked as deleted.", id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
def get_favorites() -> list[Review]:
    """
    Retrieves all reviews marked as favorites from the database.

    Returns:
        list[Review]: A list of Review objects that are marked as favorites.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, location, rating, favorite, review
                FROM ReviewsTable
                WHERE favorite = TRUE
            """)
            rows = cursor.fetchall()

            favorites = [
                Review(
                    id=row[0],
                    name=row[1],
                    location=row[2],
                    rating=row[3],
                    favorite=bool(row[4]),
                    review=row[5]
                )
                for row in rows
            ]

            logger.info("Retrieved %d favorite reviews.", len(favorites))
            return favorites
        
    except sqlite3.Error as e:
        logger.error("Database error while retrieving favorites: %s", str(e))
        raise e
    
def get_review_by_id(id: int) -> Review:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, location, rating, favorite, review, deleted FROM ReviewsTable WHERE id = ?", (id,))
            row = cursor.fetchone()

            if row:
                if row[6]:
                    logger.info("Review with ID %s has been deleted", id)
                    raise ValueError(f"Review with ID {id} has been deleted")
                return Review(id=row[0], name=row[1], location=row[2], rating=row[3], favorite=row[4], review=row[5])
            else:
                logger.info("Review with ID %s not found", id)
                raise ValueError(f"Review with ID {id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
def get_review_by_name(review_name: str) -> Review:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, location, rating, favorite, review, deleted FROM ReviewsTable WHERE review = ?", (review_name,))
            row = cursor.fetchone()

            if row:
                if row[6]:
                    logger.info("Meal with name %s has been deleted", review_name)
                    raise ValueError(f"Review with name {review_name} has been deleted")
                return Review(id=row[0], name=row[1], location=row[2], rating=row[3], favorite=row[4], review = row[5])
            else:
                logger.info("Review with name %s not found", review_name)
                raise ValueError(f"Review with name {review_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
def update_review(id: int, new_review: str) -> None:
    """
    Updates the review text for a specific review.

    Args:
        id (int): The ID of the review to update.
        new_review (str): The new review text.

    Raises:
        sqlite3.Error: If any database error occurs.
        ValueError: If the review ID does not exist.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ReviewsTable SET review = ? WHERE id = ?", (new_review, id))
            if cursor.rowcount == 0:
                raise ValueError(f"Review with ID {id} not found.")
            conn.commit()

            logger.info("Updated review text for ID %d.", id)

    except sqlite3.Error as e:
        logger.error("Database error while updating review: %s", str(e))
        raise e
    
def update_rating(id: int, new_rating: int) -> None:
    """
    Updates the rating for a specific review.

    Args:
        id (int): The ID of the review to update.
        new_rating (int): The new rating (1-5).

    Raises:
        sqlite3.Error: If any database error occurs.
        ValueError: If the rating is not between 1 and 5 or the review ID does not exist.
    """
    if not (1 <= new_rating <= 5):
        raise ValueError("Rating must be an integer between 1 and 5.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ReviewsTable SET rating = ? WHERE id = ?", (new_rating, id))
            if cursor.rowcount == 0:
                raise ValueError(f"Review with ID {id} not found.")
            conn.commit()

            logger.info("Updated rating for ID %d to %d.", id, new_rating)

    except sqlite3.Error as e:
        logger.error("Database error while updating rating: %s", str(e))
        raise e


def update_favorite(id: int, is_favorite: bool) -> None:
    """
    Updates the favorite status for a specific review.

    Args:
        id (int): The ID of the review to update.
        is_favorite (bool): The new favorite status (True or False).

    Raises:
        sqlite3.Error: If any database error occurs.
        ValueError: If the review ID does not exist.
    """
    if not isinstance(is_favorite, bool):
        raise ValueError("Favorite status must be a boolean value (True or False).")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ReviewsTable SET favorite = ? WHERE id = ?", (is_favorite, id))
            if cursor.rowcount == 0:
                raise ValueError(f"Review with ID {id} not found.")
            conn.commit()

            logger.info("Updated favorite status for ID %d to %s.", id, is_favorite)

    except sqlite3.Error as e:
        logger.error("Database error while updating favorite status: %s", str(e))
        raise e


    


