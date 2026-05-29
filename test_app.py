from app import greeting


def test_greeting_returns_hello_world() -> None:
    assert greeting() == "Hello, world!"
