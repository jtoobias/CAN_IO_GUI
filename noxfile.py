import nox

@nox.session
def tests(session):
    session.install(".")  # Install package in environment
    session.install("pytest")
    session.run("pytest", "tests")

@nox.session
def lint(session):
    session.install("flake8", "black")
    session.run("flake8", "can_io", "tests")  # Linting
    session.run("black", "--check", "can_io", "tests")  # Formatting check

@nox.session
def format(session):
    session.install("black")
    session.run("black", "can_io", "tests")  # Auto-format
