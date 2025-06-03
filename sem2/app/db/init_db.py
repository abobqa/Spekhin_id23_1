from sem2.app.db.session import engine
from sem2.app.db.base import Base


def init_db():
    Base.metadata.create_all(bind=engine)
