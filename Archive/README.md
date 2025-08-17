# TEF AI Practice Tool

A full-stack web application for practicing the Test d'évaluation de français (TEF) using artificial intelligence. The tool provides an interactive writing practice environment with AI-powered evaluation and feedback, specifically designed for TEF Canada exam preparation.

## 🚀 Features

### Core Functionality
- **Writing Module**: Complete writing practice with AI evaluation for both Task A (descriptive continuation) and Task B (argumentative letter/opinion)
- **AI-Generated Questions**: Dynamic question generation using Google Cloud AI for unlimited practice questions
- **Custom Questions**: Input your own questions for practice
- **Real-time Timer**: 60-minute countdown timer for realistic exam conditions
- **Live Word Count**: Track your writing progress in real-time
- **Multi-Run AI Evaluation**: Comprehensive feedback using the same AI evaluation criteria run twice for reliability

### User Management & Authentication
- **User Registration**: Create new accounts with email verification
- **Secure Login**: JWT-based authentication system with bcrypt password hashing
- **User Profiles**: Personalized experience for each user
- **Evaluation History**: Track all your past practice sessions with detailed feedback
- **Default Test User**: Pre-configured 'testing' user for immediate access

### AI Evaluation System
- **First AI Run**: Initial evaluation using TEF Canada official scoring rubric
- **Second AI Run**: Same evaluation criteria run again for consistency and reliability
- **Final Judge**: Consolidates both AI runs, resolving any discrepancies and providing unified feedback
- **Official Standards**: Aligned with TEF Canada's official scoring system and NCLC/CLB conversion table
- **Enhanced Scoring**: 5-category evaluation (Content & Coherence, Vocabulary & Precision, Grammar & Language Accuracy, Task Fulfillment & Structure, Adaptability & Register)
- **Detailed Error Analysis**: Comprehensive error identification in French with corrections and explanations
- **Cross-Task Analysis**: Comparative analysis between Task A and Task B performance
- **Consolidated Scoring**: Unified scoring system with task-specific performance metrics
- **Structured JSON Output**: Comprehensive feedback in machine-readable format for database storage and analysis
- **TEF Writing Score**: Final score on the official 0-450 TEF scale

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with automatic API documentation and OpenAPI schema
- **Database**: SQLAlchemy ORM with SQLite (configurable for production databases)
- **Authentication**: JWT tokens with bcrypt password hashing and secure token management
- **AI Integration**: Google Cloud Vertex AI with Gemini 2.5 Pro for advanced language evaluation
- **API Endpoints**: RESTful API with comprehensive error handling and validation
- **Configuration Management**: Centralized configuration with environment-specific settings

### Frontend (Single HTML File)
- **Technology**: Vanilla JavaScript with Bootstrap 5 for responsive design
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Real-time Updates**: Dynamic content without page refreshes
- **User Experience**: Intuitive navigation between practice modes and evaluation results

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core runtime environment
- **FastAPI**: Modern, fast web framework with automatic documentation
- **SQLAlchemy**: Database ORM and migrations with automatic schema management
- **Passlib**: Secure password hashing with bcrypt
- **Python-Jose**: JWT token handling and validation
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### AI & Cloud
- **Google Cloud Vertex AI**: AI model hosting and inference
- **Gemini 2.5 Pro**: Advanced language model for evaluation and question generation
- **Vertex AI SDK**: Python client for Google Cloud AI services
- **TEF Canada Standards**: Official scoring rubric and NCLC/CLB conversion table integration
- **Professional Evaluation**: Certified examiner-level assessment criteria
- **Dynamic Question Generation**: AI-powered creation of Task A and Task B questions following TEF Canada exam requirements

### Database
- **SQLite**: Default development database with automatic setup
- **PostgreSQL/MySQL**: Production-ready alternatives with migration support
- **Database Migrations**: Automatic schema management and version tracking

### Development & Testing
- **Testing Suite**: Comprehensive test coverage with automated testing
- **Deployment Scripts**: Production-ready deployment automation
- **Migration Tools**: Database schema management and updates
- **Configuration Management**: Environment-specific settings and validation

### Database Schema Updates
- **Migration Script**: Run `python migrations.py migrate` to add new evaluation columns
- **New Fields**: `detailed_errors`, `consolidated_scores`, `cross_task_analysis`, `final_tef_writing_score`
- **Backward Compatibility**: Existing evaluations continue to work with enhanced data display
- **Schema Status**: Check database status with `python migrations.py status`

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Google Cloud account (for AI features)
- Git (for version control)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TEFEvaluator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Main app: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Default user: `testing` / `testing`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `env_example.txt`:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=sqlite:///./tef_evaluator.db

# Application Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
```

### Google Cloud Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Vertex AI API

2. **Set up Service Account**
   - Create a service account with Vertex AI permissions
   - Download the JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env`

3. **Configure Project ID**
   - Set `GOOGLE_CLOUD_PROJECT_ID` to your project ID
   - Set `GOOGLE_CLOUD_LOCATION` (default: us-central1)

## 🗄️ Database Setup

### Automatic Setup
The application automatically creates the database and tables on first run. A default 'testing' user is created automatically.

### Manual Database Management
```bash
# Create database tables
python -c "from models import Base, engine; Base.metadata.create_all(bind=engine)"

# Create default user
python -c "from models import create_default_user; create_default_user()"

# Run database migrations
python migrations.py

# Reset database (development only)
python migrations.py --reset
```

### Database Schema
- **Users Table**: User accounts with authentication data and active status
- **Evaluations Table**: Practice session results with comprehensive feedback storage in structured JSON format
- **Rich Data Storage**: Detailed scores, error analysis, TEF scores, and NCLC/CLB levels stored as structured data
- **Schema Version Tracking**: Automatic version management for database updates
- **Relationships**: One-to-many relationship between users and evaluations

## 🔐 Authentication System

### User Registration
- Username and email required with validation
- Secure password hashing with bcrypt
- Email validation (configurable)
- Automatic user activation

### User Login
- JWT token-based authentication
- Configurable token expiration (default: 30 minutes)
- Secure password verification
- Session management

### Protected Endpoints
- `/api/evaluate`: Writing evaluation (requires authentication)
- `/api/evaluations`: User's evaluation history
- `/api/evaluations/{id}`: Specific evaluation details
- `/api/auth/me`: Current user information

## 📊 Enhanced Evaluation System

### TEF Canada Official Standards
The application integrates with official TEF Canada Writing Module evaluation criteria:

- **Task Type Recognition**: Automatic identification of Task A (descriptive continuation ~80 words) vs Task B (argumentative letter/opinion ~200 words)
- **5-Category Scoring**: Comprehensive evaluation across Content & Coherence, Vocabulary & Precision, Grammar & Language Accuracy, Task Fulfillment & Structure, and Adaptability & Register
- **Official Scoring Scale**: 1-5 rating system (1 = poor, 5 = excellent) with detailed justification
- **NCLC/CLB Conversion**: Automatic conversion from TEF Writing Score (0-450) to Canadian Language Benchmark levels
- **Detailed Error Analysis**: Comprehensive identification of grammatical errors, coherence issues, vocabulary problems, register mismatches, and task fulfillment gaps
- **Structured Data Output**: All evaluation results provided in comprehensive JSON format for easy database storage and programmatic analysis

### How the Evaluation System Works
The system uses a **redundancy approach** for reliability:
- **First Run**: AI evaluates the writing using TEF Canada standards
- **Second Run**: Same AI model runs the identical evaluation again for consistency checking
- **Final Judge**: Consolidates both results, resolving any discrepancies and providing unified feedback

This approach reduces AI response variability and ensures more reliable, consistent evaluations.

## 🤖 AI Question Generation

### Dynamic Question Creation
The application now features AI-powered question generation for unlimited practice:

- **Task A Questions**: AI generates descriptive continuation prompts (100-200 words, 3-4 paragraphs) with advanced French tenses
- **Task B Questions**: AI creates argumentative letter/opinion prompts (250-300 words, 5 paragraphs) with advanced vocabulary
- **TEF Canada Compliance**: All generated questions follow official exam requirements and difficulty levels
- **Unlimited Practice**: Generate new questions anytime for varied practice sessions

### Question Generation Process
1. **Single Click Generation**: Click the AI generation button for instant new questions
2. **Smart Prompting**: Specialized prompts ensure questions meet TEF Canada standards
3. **Real-time Feedback**: Visual indicators show generation progress and success
4. **Seamless Integration**: Generated questions immediately available for writing practice

### Evaluation Process
1. **Redundant AI Assessment**: The same evaluation criteria run twice using the AI model for consistency and reliability
2. **Comprehensive Feedback**: Detailed comments for each evaluation criterion
3. **Actionable Recommendations**: Specific improvement suggestions for scores below 4
4. **Final Consolidation**: Judge consolidates both AI evaluations for comprehensive final assessment

## 📱 Usage Guide

### Getting Started
1. **Access the application** at http://localhost:8000
2. **Login** with default credentials: `testing` / `testing`
3. **Select Writing Module** from the main menu
4. **Choose a question** (AI-generated or custom)
5. **Start writing** with the 60-minute timer
6. **Submit your response** for AI evaluation
7. **Review feedback** and track your progress

### Practice Workflow
1. **Question Generation**: Generate new AI-powered questions for Task A or Task B with a single click
2. **Writing Phase**: Compose your response with real-time feedback
3. **AI Evaluation**: Multi-run assessment process using TEF Canada official standards (same criteria run twice for reliability)
4. **Results Review**: Comprehensive feedback with detailed scoring (1-5 scale) and NCLC/CLB level estimation
5. **Progress Tracking**: View your evaluation history with detailed error analysis

### Question Types
- **AI-Generated Questions**: Click "Générer Question IA A/B" to get new questions automatically generated by AI
- **Custom Questions**: Click "Saisir une Question" to input your own specific topics or exam questions
- Both question types fully integrate with the AI evaluation system

## 🔧 Development

### Project Structure
```
TEFEvaluator/
├── main.py              # FastAPI application and API endpoints
├── models.py            # Database models and ORM setup
├── auth.py              # Authentication utilities and JWT handling
├── prompt.py            # AI evaluation and question generation prompts
├── config.py            # Configuration management and settings
├── deploy.py            # Production deployment automation
├── migrations.py        # Database migration and management
├── test_app.py          # Comprehensive testing suite
├── run.py               # Application startup script
├── index.html           # Frontend interface (single file)
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables template
├── config.env           # Configuration template
├── README.md            # Project documentation
└── .env                 # Environment configuration (create from template)
```

### Running in Development
```bash
# Start with auto-reload
python run.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_app.py

# Run database migrations
python migrations.py
```

### API Development
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Testing
```bash
# Run comprehensive test suite
python test_app.py

# Test specific components
python test_app.py --health
python test_app.py --auth
python test_app.py --evaluation
```

## 🚀 Production Deployment

### Automated Deployment
```bash
# Run production deployment
python deploy.py

# Check deployment prerequisites
python deploy.py --check

# Create production configuration
python deploy.py --config
```

### Environment Considerations
- **SECRET_KEY**: Use a strong, unique secret key (minimum 32 characters)
- **Database**: Consider PostgreSQL or MySQL for production
- **HTTPS**: Enable SSL/TLS for secure communication
- **CORS**: Configure allowed origins for production domains
- **Logging**: Comprehensive logging with file and console output

### Deployment Options
- **Docker**: Containerized deployment with provided scripts
- **Cloud Platforms**: Google Cloud Run, AWS Lambda, Azure Functions
- **Traditional Servers**: Nginx + Gunicorn + FastAPI
- **Systemd Service**: Automatic startup and management

### Security Best Practices
- Change default SECRET_KEY
- Use environment-specific database URLs
- Implement rate limiting
- Enable HTTPS
- Regular security updates
- Secure environment variable management

## 🔮 Future Enhancements

### Implemented Features ✅
- **AI Question Generation**: Dynamic creation of Task A and Task B questions using Google Cloud AI
- **Unlimited Practice Questions**: No more static question lists - generate new questions anytime

### Planned Features 🚧
- **Speaking Module**: AI-powered oral expression practice
- **Progress Analytics**: Detailed performance tracking and visualization
- **Customizable Prompts**: User-defined evaluation criteria
- **Multi-language Support**: Additional language options
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Performance trends and improvement recommendations

### AI Improvements
- **Model Fine-tuning**: Custom training for TEF Canada-specific evaluation
- **Real-time Feedback**: Live writing suggestions based on official TEF standards
- **Adaptive Difficulty**: Question difficulty based on user's NCLC/CLB level
- **Personalized Learning**: AI-driven study recommendations aligned with TEF Canada requirements
- **Enhanced Evaluation**: Integration with latest TEF Canada scoring rubrics and standards

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check database file permissions
ls -la tef_evaluator.db

# Recreate database
rm tef_evaluator.db
python -c "from models import Base, engine; Base.metadata.create_all(bind=engine)"

# Run migrations
python migrations.py
```

**Authentication Issues**
```bash
# Verify JWT configuration
echo $SECRET_KEY

# Check user creation
python -c "from models import create_default_user; create_default_user()"

# Test authentication endpoints
python test_app.py --auth
```

**Google Cloud Errors**
```bash
# Verify credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $GOOGLE_CLOUD_PROJECT_ID

# Test authentication
gcloud auth application-default login

# Check API status
python test_app.py --health
```

### Logs and Debugging
- **Application Logs**: Check console output and log files
- **API Errors**: Review FastAPI automatic error responses
- **Database Issues**: SQLAlchemy error messages in logs
- **Testing**: Use comprehensive test suite for diagnostics

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `python test_app.py`
6. Submit a pull request

### Code Standards
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Include error handling for edge cases
- Maintain test coverage

### Testing Requirements
- All new features must include tests
- Run full test suite before submitting
- Ensure tests pass in both development and production environments

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern web framework for building APIs
- **Google Cloud**: AI and cloud infrastructure
- **Bootstrap**: Frontend framework for responsive design
- **Font Awesome**: Icon library for enhanced UI
- **TEF Canada**: Official exam standards and scoring criteria

## 📞 Support

For questions, issues, or contributions:
- **Issues**: Use the GitHub issue tracker
- **Documentation**: Check this README and API docs
- **Community**: Join our development discussions
- **Testing**: Use the comprehensive test suite for diagnostics

---

**Happy practicing! 🎓✨**
