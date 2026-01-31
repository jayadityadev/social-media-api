# Social Media API

## This FastAPI backend application uses PostgreSQL to allow CRUD operations for posts, users, and voting system on posts. Also, it provided protected endpoints so that UD (from CRUD) can be performed on posts/user belonging to the logged in user only. It handles all the edge cases neatly with proper response codes.

## To get started:

1. Clone the repository
   ```bash
   git clone https://github.com/jayadityadev/social-media-api
   ```

2. Build the python environment
   ```bash
   cd social-media-api
   python -m venv .venv
   pip install -r requirements.txt
   ```

3. PostgreSQL should be up and running (either local or remote), and the credentials are to be put up in the `.env` file (.env.example is available for reference)

4. Run the app
   - Development
     ```bash
     fastapi dev app/main.py
     ```
   - Production
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
     ```

> Notes:
>  - You must be logged in as a user to perform any operations (except creating a user, obv).
>  - Voting system works on direction (upvote and un-vote), ie to vote on a post, `dir: 1`, and to remove an existing vote, `dir: 0`.
>  - Authentication uses JWT, so the JWT credentials are also to be provided in the `.env` file.
