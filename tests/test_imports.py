def test_import_packages():
    # Ensure packages are importable for tests
    import bot
    import client
    assert bot is not None
    assert client is not None
