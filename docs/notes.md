## `py` (Windows launcher/install manager) vs `pyenv` (UNIX)

| Task                                    | `py` (Windows)                                                | `pyenv` / `pyenv-win`                           |
| --------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------- |
| Check tool version                      | `py --version`                                                | `pyenv --version`                               |
| List installed Python versions          | `py -0p`                                                      | `pyenv versions`                                |
| List installable versions               | `py list`                                                     | `pyenv install --list`                          |
| Install Python 3.12                     | `py install 3.12`                                             | `pyenv install 3.12.0`                          |
| Uninstall Python 3.12                   | `py uninstall 3.12`                                           | `pyenv uninstall 3.12.0`                        |
| Run a specific Python version (one-off) | `py -3.12 -c "print(1)"`                                      | `pyenv shell 3.12.0` *(then `python ...`)*      |
| Run the default Python                  | `py`                                                          | `python` *(after setting pyenv global/local)*   |
| Show default Python                     | `py -c "import sys; print(sys.executable)"`                   | `python -c "import sys; print(sys.executable)"` |
| Set global default Python               | `py install default 3.12` *(if supported in your build)*      | `pyenv global 3.12.0`                           |
| Set per-project Python                  | *(no direct equivalent)*                                      | `pyenv local 3.12.0`                            |
| Show current “local” Python setting     | *(N/A)*                                                       | `pyenv local`                                   |
| Create venv with chosen Python          | `py -3.12 -m venv .venv`                                      | `python -m venv .venv` *(after `pyenv local`)*  |
| Install pip packages                    | `py -m pip install ...` *(or inside venv: `pip install ...`)* | `pip install ...` *(inside venv)*               |
| Upgrade pip                             | `py -m pip install -U pip`                                    | `pip install -U pip`                            |
| Find Python exe paths                   | `py -0p`                                                      | `pyenv which python`                            |

## uv

| Task                         | `py` way                | `pyenv` way                      |
| ---------------------------- | ----------------------- | -------------------------------- |
| Create venv with Python 3.12 | `uv venv --python 3.12` | `pyenv local 3.12.0` → `uv venv` |
| Confirm venv Python version  | `python --version`      | `python --version`               |

## Common HTTP Methods (REST-y cheat sheet)

| Method      | What it does                         | Idempotent?* | Typical use                    |
| ----------- | ------------------------------------ | ------------ | ------------------------------ |
| **GET**     | Fetch data                           |          Yes | Read a resource (`/users/12`)  |
| **POST**    | Create something / trigger an action |           No | Create resource (`/users`)     |
| **PUT**     | Replace entire resource              |          Yes | Replace user (`/users/12`)     |
| **PATCH**   | Partially update resource            |      Usually | Update one field (`/users/12`) |
| **DELETE**  | Remove resource                      |          Yes | Delete (`/users/12`)           |
| **HEAD**    | Like GET but no body                 |          Yes | Check if exists / metadata     |
| **OPTIONS** | Ask server what’s allowed            |          Yes | CORS / allowed methods         |

*Idempotent = repeating it multiple times results in the same final state (roughly).

## Common HTTP Status Codes

### 2xx Success
|               Code | Meaning                 | When you use it                               |
| -----------------: | ----------------------- | --------------------------------------------- |
|         **200 OK** | Success                 | GET success, normal success                   |
|    **201 Created** | Resource created        | POST created something                        |
|   **202 Accepted** | Accepted for processing | Async job queued                              |
| **204 No Content** | Success, no body        | DELETE success / PUT success with no response |

### 3xx Redirect
|                      Code | Meaning            | When you see it            |
| ------------------------: | ------------------ | -------------------------- |
| **301 Moved Permanently** | Permanent redirect | Old URL changed forever    |
|             **302 Found** | Temporary redirect | Temporary routing change   |
|      **304 Not Modified** | Use cached version | Browser caching with ETags |

### 4xx Client Errors
|                         Code | Meaning                   | When you use/see it                     |
| ---------------------------: | ------------------------- | --------------------------------------- |
|          **400 Bad Request** | Invalid input             | JSON wrong, validation fails            |
|         **401 Unauthorized** | Not logged in / no auth   | Missing/invalid token                   |
|            **403 Forbidden** | Logged in but not allowed | Role/permission issue                   |
|            **404 Not Found** | Doesn’t exist             | Resource ID missing                     |
|   **405 Method Not Allowed** | Wrong method              | POST on a GET-only route                |
|             **409 Conflict** | Conflict in state         | Duplicate email / version conflict      |
| **422 Unprocessable Entity** | Validation error          | Super common in FastAPI body validation |
|    **429 Too Many Requests** | Rate limited              | Too many calls                          |

### 5xx Server Errors
|                          Code | Meaning                | When you use/see it      |
| ----------------------------: | ---------------------- | ------------------------ |
| **500 Internal Server Error** | Server crashed/bug     | Unhandled exception      |
|           **502 Bad Gateway** | Bad upstream response  | Proxy/API gateway failed |
|   **503 Service Unavailable** | Down/overloaded        | Maintenance, load issues |
|       **504 Gateway Timeout** | Upstream took too long | DB/API timeout           |

## CRUD

| Opertaion  | Method    | URL           |
| ---------- | --------- | ------------- |
| **Create** | POST      | `/posts`      |
| **Read**   | GET       | `/posts/{id}` |
| **Read**   | GET       | `/posts`      |
| **Update** | PUT/PATCH | `/posts/{id}` |
| **Delete** | DELETE    | `/posts/{id}` |

## Pydantic

> Use pydantic for validation of POST body

```python
from pydantic import BaseModel
class CreatePost(BaseModel):
    title: str
    content: str
    category: str | None = None
    published: bool = True
@app.post("/createposts")
def create_post(payload: CreatePost):
    return payload
```