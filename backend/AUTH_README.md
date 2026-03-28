# Backend Authentication (MongoDB + JWT)

This project now includes basic user authentication in the backend.

## Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me` (Bearer token required)

## Request/Response Shapes

### Register
`POST /api/v1/auth/register`

```json
{
  "email": "user@example.com",
  "full_name": "Demo User",
  "password": "StrongPass123"
}
```

### Login
`POST /api/v1/auth/login`

```json
{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

Returns:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "...",
    "email": "user@example.com",
    "full_name": "Demo User",
    "created_at": "..."
  }
}
```

### Current user
`GET /api/v1/auth/me`

Header:

`Authorization: Bearer <access_token>`

## Configuration

Set in `backend/.env`:

- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `MONGODB_USERS_COLLECTION`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## Notes

- Passwords are hashed using `bcrypt` via `passlib`.
- JWT tokens are signed with `python-jose`.
- `email` has a unique index in MongoDB.
