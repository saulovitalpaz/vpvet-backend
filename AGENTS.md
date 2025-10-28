# VPVET Backend - Agent Guidelines

## Commands
- **Run app**: `python app.py` or `flask run`
- **Database migrations**: `flask db migrate -m "message"` && `flask db upgrade`
- **Tests**: No testing framework currently configured - pytest recommended for Python testing
- **Lint**: No formal linting configured - follow PEP 8
- **Railway deployment**: Push to GitHub and connect to Railway, add PostgreSQL service

## Code Style
- **Imports**: Standard library first, then third-party, then local imports
- **Models**: Inherit from `BaseModel`, use UUID primary keys, include `to_dict()` methods
- **API**: Use Flask blueprints, return JSON responses with proper HTTP status codes
- **Auth**: JWT tokens with `@jwt_required()` decorator, include role-based access control
- **Database**: SQLAlchemy with PostgreSQL, use `db.session.commit()` and `db.session.rollback()`
- **Error handling**: Return JSON error responses with appropriate status codes (400, 401, 403, 404, 409)
- **Naming**: snake_case for variables/functions, PascalCase for classes, lowercase for routes
- **Security**: Password hashing with bcrypt, never expose password hashes, validate input data