if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run('server:app', host="81.94.150.224", port=8002, reload=True)
    #uvicorn.run('server:app', host="81.94.158.27", port=8001, workers = 2)

