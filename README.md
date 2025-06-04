# Student Union Management System

A web application for managing student union data, including students, groups, divisions, and contributions.

## Features

- User authentication with JWT tokens
- Role-based access control (CHAIRMAN, DEPUTY_CHAIRMAN, DIVISION_HEAD, DORMITORY_HEAD)
- Management of students, groups, and divisions
- Tracking of student contributions
- Hostel management
- Additional student statuses tracking

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Pydantic (Data validation)
- JWT authentication

### Frontend
- React
- Material-UI
- React Router
- Axios
- Redux Toolkit

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   │   ├── core/          # Core functionality
│   │   │   ├── models/        # Database models
│   │   │   ├── repositories/  # Database operations
│   │   │   └── services/      # Business logic
│   │   ├── migrations/        # Database migrations
│   │   └── tests/            # Test files
│   ├── frontend/
│   │   ├── public/
│   │   └── src/
│   │       ├── components/   # React components
│   │       ├── pages/        # Page components
│   │       ├── services/     # API services
│   │       └── store/        # Redux store
│   └── migrations/           # SQL migrations
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/student-union-management.git
cd student-union-management
```

2. Start the services using Docker Compose:
```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Authentication
- POST /api/v1/auth/login - Login user
- GET /api/v1/auth/me - Get current user info

### Students
- GET /api/v1/students - List students
- POST /api/v1/students - Create student
- GET /api/v1/students/{id} - Get student
- PUT /api/v1/students/{id} - Update student
- DELETE /api/v1/students/{id} - Delete student
- GET /api/v1/students/{id}/contributions - Get student contributions
- GET /api/v1/students/{id}/hostel - Get student hostel info

### Groups
- GET /api/v1/groups - List groups
- POST /api/v1/groups - Create group
- GET /api/v1/groups/{id} - Get group
- PUT /api/v1/groups/{id} - Update group
- DELETE /api/v1/groups/{id} - Delete group
- GET /api/v1/groups/{id}/students - Get group students

### Divisions
- GET /api/v1/divisions - List divisions
- POST /api/v1/divisions - Create division
- GET /api/v1/divisions/{id} - Get division
- PUT /api/v1/divisions/{id} - Update division
- DELETE /api/v1/divisions/{id} - Delete division
- GET /api/v1/divisions/{id}/groups - Get division groups
- GET /api/v1/divisions/{id}/users - Get division users

## Database Schema

### Main Tables
- Subdivisions (подразделения)
- Roles (роли пользователей)
- AdditionalStatuses (доп. статусы студентов)
- Groups (группы)
- Users (пользователи)
- StudentData (данные студентов)
- Students (основная информация о студентах)
- HostelStudents (проживание в общежитии)
- Contributions (взносы)

### Junction Tables
- UserRoles (связь пользователей и ролей)
- StudentAdditionalStatuses (связь студентов и статусов)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
