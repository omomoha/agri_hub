# 🌾 AgriLink - Agricultural Marketplace Platform

AgriLink is a comprehensive agricultural marketplace platform that connects farmers, buyers, aggregators, and logistics providers in Nigeria. The platform facilitates the trading of agricultural produce with integrated KYC verification, escrow services, and logistics management.

## 🚀 Features

### Core Functionality
- **User Management**: Multi-role user system (Farmers, Buyers, Aggregators, Logistics, Admins)
- **Farm Management**: Comprehensive farm profiles with soil type, irrigation, and size tracking
- **Product Listings**: Detailed produce listings with pricing, quality grades, and organic certification
- **KYC Verification**: Document verification for business compliance
- **Escrow Services**: Secure payment handling with buyer protection
- **Contract Management**: Digital contract creation and management
- **Order Tracking**: Complete order lifecycle management
- **Logistics Integration**: Delivery coordination and tracking

### Technical Features
- **Modern Tech Stack**: FastAPI backend, Next.js frontend, PostgreSQL database
- **Docker Containerization**: Easy deployment and scaling
- **RESTful API**: Comprehensive API endpoints with OpenAPI documentation
- **Authentication**: JWT-based secure authentication
- **Role-Based Access Control**: Granular permissions system
- **Real-time Updates**: WebSocket support for live updates

## 🏗️ Architecture

```
agri_hub/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality (auth, database)
│   │   ├── models/         # Database models
│   │   └── schemas/        # Pydantic schemas
│   ├── tests/              # Unit and integration tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend application
│   ├── app/                # App router pages
│   ├── components/         # Reusable UI components
│   └── package.json        # Node.js dependencies
├── nginx/                  # Reverse proxy configuration
├── docker-compose.yml      # Multi-service orchestration
└── README.md              # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL database integration with Pydantic
- **PostgreSQL**: Robust relational database
- **JWT**: Secure authentication tokens
- **Pytest**: Comprehensive testing framework

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **React Hook Form**: Form handling and validation

### Infrastructure
- **Docker**: Containerization and orchestration
- **Nginx**: Reverse proxy and load balancing
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage

## 📋 Prerequisites

Before running this project, ensure you have:

- **Docker & Docker Compose**: For containerized deployment
- **Git**: For version control
- **Node.js 18+**: For frontend development (optional)
- **Python 3.11+**: For backend development (optional)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/agri_hub.git
cd agri_hub
```

### 2. Environment Setup
```bash
# Copy environment files
cp backend/env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit environment variables as needed
nano backend/.env
nano frontend/.env.local
```

### 3. Start the Application
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx**: http://localhost:80

## 🔧 Development Setup

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch
```

## 📚 API Documentation

The API documentation is automatically generated using FastAPI's OpenAPI integration:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

#### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/` - List users (admin only)

#### Farms
- `GET /api/v1/farms/` - List farms
- `POST /api/v1/farms/` - Create farm
- `GET /api/v1/farms/{id}` - Get farm details
- `PUT /api/v1/farms/{id}` - Update farm

#### Listings
- `GET /api/v1/listings/` - List produce listings
- `POST /api/v1/listings/` - Create listing
- `GET /api/v1/listings/{id}` - Get listing details
- `PUT /api/v1/listings/{id}` - Update listing

#### KYC
- `GET /api/v1/kyc/` - List KYC records
- `POST /api/v1/kyc/` - Submit KYC application
- `PUT /api/v1/kyc/{id}/approve` - Approve KYC (admin)

## 🐳 Docker Commands

### Service Management
```bash
# Start specific service
docker compose up -d backend

# Rebuild and start
docker compose up -d --build

# View service status
docker compose ps

# View service logs
docker compose logs backend
```

### Database Operations
```bash
# Access database
docker compose exec db psql -U postgres -d agri_hub

# Backup database
docker compose exec db pg_dump -U postgres agri_hub > backup.sql

# Restore database
docker compose exec -T db psql -U postgres -d agri_hub < backup.sql
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **Role-Based Access Control**: Granular permission system
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLModel ORM protection
- **CORS Configuration**: Cross-origin request handling

## 📊 Database Schema

The application uses a comprehensive database schema with the following main entities:

- **Users**: Multi-role user management
- **Farms**: Farm profiles and management
- **Listings**: Product listings and inventory
- **Offers**: Purchase offers and negotiations
- **Contracts**: Legal agreements and terms
- **Escrow**: Payment security and handling
- **Orders**: Order management and tracking
- **KYC**: Identity verification and compliance

## 🚀 Deployment

### Production Deployment
```bash
# Set production environment
export NODE_ENV=production
export PYTHON_ENV=production

# Build and start production services
docker compose -f docker-compose.prod.yml up -d --build
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@host:port/db
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend (.env.local)
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AgriLink
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/agri_hub/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/agri_hub/wiki)
- **Email**: support@agrilink.com

## 🙏 Acknowledgments

- **FastAPI** team for the excellent web framework
- **Next.js** team for the React framework
- **SQLModel** team for the database integration
- **Tailwind CSS** team for the utility-first CSS framework

---

**AgriLink** - Connecting Agriculture, Empowering Communities 🌱
