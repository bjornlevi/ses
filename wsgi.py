from app import create_app, db
from app.models import User, Opinion, Argument, Reasoning

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Opinion": Opinion,
        "Argument": Argument,
        "Reasoning": Reasoning,
    }


if __name__ == "__main__":
    # Convenience for local runs: python wsgi.py
    app.run(debug=True)
