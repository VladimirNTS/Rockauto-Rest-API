import uvicorn


def main():
    uvicorn.run(app='app.app:app', host=0.0.0.0, port=8000, reload=true)


if __name__=='__main__':
    main()


