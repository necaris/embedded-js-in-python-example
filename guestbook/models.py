from sqlalchemy import Column, Index, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

# Initialize database session with transaction management
DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()


class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    twitter_handle = Column(String(255))
    signed_up_at = Column(DateTime)

    def __json__(self, request=None):
        """
        Serialize this object to JSON -- convenient for both RESTful
        access and embedding in client-side code.
        """
        return {
            "id": self.id,
            "name": self.name,
            "twitter_handle": self.twitter_handle,
            "signed_up_at": self.signed_up_at.isoformat()
        }


# Set up indexes for fast access
Index('guests_by_id', Guest.id, unique=True, mysql_length=255)
Index('guests_by_twitter', Guest.twitter_handle, unique=True,
      mysql_length=255)
