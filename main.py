import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")

@app.command()
def info():
    print("An agentic LLM loop for coding")



if __name__ == "__main__":
    app()
