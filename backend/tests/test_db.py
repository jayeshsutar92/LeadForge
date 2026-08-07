from sqlalchemy import create_engine
from app.db.base_class import Base

def test_db_connection():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        assert conn is not None
    Base.metadata.drop_all(engine)


