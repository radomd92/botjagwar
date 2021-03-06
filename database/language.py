from sqlalchemy import String, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Language(Base):
    __tablename__ = 'language'
    iso_code = Column(String(6), primary_key=True)
    english_name = Column(String(100))
    malagasy_name = Column(String(100))
    language_ancestor = Column(String(6))

    def get_schema(self):
        pass

    def serialise(self):
        return {
            'type': self.__class__.__name__,
            'iso_code': self.iso_code,
            'english_name': self.english_name,
            'malagasy_name': self.malagasy_name,
            'ancestor': self.language_ancestor
        }