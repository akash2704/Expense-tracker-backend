from sqlalchemy import inspect


def test_db_tables(db):
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    assert 'users' in tables, "Users table not found"
    assert 'expenses' in tables, "Expenses table not found"
