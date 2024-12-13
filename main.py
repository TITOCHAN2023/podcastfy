import uvicorn

from routes import create_app
API_HOST="127.0.0.1"
API_PORT=8080

app = create_app()

def main() -> None:
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="critical",
    )


if __name__ == "__main__":
    main()
