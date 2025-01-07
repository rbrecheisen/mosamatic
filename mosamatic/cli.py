import typer

app = typer.Typer()


@app.command()
def greet(name: str, age: int = typer.Option(30, help='Your age')):
    """
    Greet a user by their name and age
    """
    typer.echo(f'Hello, {name}! You are {age} years old.')


if __name__ == '__main__':
    app()