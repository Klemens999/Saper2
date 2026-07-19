"""Uruchamia serwer aplikacji: python run.py [--host 0.0.0.0] [--port 8000]"""

import argparse

import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polski Dubbing AI - serwer webowy")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run("app.main:app", host=args.host, port=args.port)
