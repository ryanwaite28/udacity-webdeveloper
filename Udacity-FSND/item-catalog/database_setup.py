import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    menuitems = relationship("MenuItem",
                            cascade="delete, delete-orphan",
                            backref="MenuItem")

    @property
    def serialize(self):
        # Returns Data Object In Proper Format
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    @property
    def serialize(self):
        # Returns Data Object In Proper Format
        return {
            'name': self.name,
            'id': self.id,
            'course': self.course,
            'price': self.price,
            'description': self.description,
            'restaurant': self.restaurant.name,
            'restaurantID': self.restaurant_id,
        }



### INSERT AT END OF FILE ###
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
