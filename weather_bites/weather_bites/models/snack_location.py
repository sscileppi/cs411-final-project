# models/snack_location.py

class SnackLocation(Base):
    __tablename__ = "snack_locations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False) #name of the Snack Location
    location = Column(String, nullable=False)  # Physical address
    rating = Column(Integer, nullable = True)  # Rating of 1-5
    favorite = Column(Boolean, default=False)  # Is this a favorite snack location?
    review = Column(String, nullable=True)  # review of the snack location


    def __init__(self, name, location, rating= None, favorite=False, review = None):
        self.name = name
        self.location = location
        self.rating = rating
        self.favorite = favorite
        self.review = review

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "rating": self.rating,
            "favorite": self.favorite,
            "review": self.review,
        }
