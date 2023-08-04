#!/usr/bin/python
""" holds class City"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class City(BaseModel, Base):
    """Representation of city"""

    if models.storage_t == "db":
        __tablename__ = "cities"
        state_id = Column(
            String(60),
            ForeignKey("states.id", ondelete="CASCADE"),
            nullable=False
        )
        name = Column(String(128), nullable=False)
        places = relationship(
            "Place",
            backref="cities",
            passive_deletes=True,
            cascade="all, delete-orphan",
        )
    else:
        state_id = ""
        name = ""

    def __init__(self, *args, **kwargs):
        """initializes city"""
        super().__init__(*args, **kwargs)

    if models.storage_t != "db":

        @property
        def places(self):
            """Get all places in the City"""

            from models import storage
            from models.place import Place

            places = storage.all(Place)
            return [
                place
                for place in places.values()
                if place.city_id == self.id
            ]
