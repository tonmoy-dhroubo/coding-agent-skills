# API Test Report

| Method | Path | Status | Latency (ms) | Notes |
| --- | --- | --- | --- | --- |
| GET | /health | 200 | 12 | ok |
| POST | /auth/login | 200 | 35 | ok; payload guessed |
| POST | /users | 201 | 48 | ok; payload guessed |
| GET | /users/1 | 200 | 20 | ok |
