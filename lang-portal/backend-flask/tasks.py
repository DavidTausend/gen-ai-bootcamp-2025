from invoke import task

@task
def run(ctx):
    """Run the Flask development server."""
    ctx.run("flask run", pty=True)

@task
def init_db(ctx):
    """Initialize the database."""
    from app import db
    db.create_all()
