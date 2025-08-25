# Valora Earth Assignment - A Django app where users enter land details and receive an AI-generated property valuation using OpenAI's GPT-4.1-mini.

## 📋 Assumptions Made

- The "Name of Project" in results page is created by GPT/AI model, not by user
- The homepage is the "Estimate Your Earnings" page (base / url, not /estimate url)
- The tab selection in the results page changes from Projected 10-Year Cash Flow to Revenue and Cost (doesn't change on the designs)
- The image in the results page is not AI-generated, using same image for all results
- Included AI Analysis Logs model in addition to Estimates and Inquiries models
- Included simulated loading bar for loading page, pretend progress bar updates
- Included default blue border highlighting for inputs, potential improvement use valora earth coloring
- Included Cost Chart with Operational Costs, Infrastructure, Maintenance sections
- Saved additional non-user interfacing AI response fields for admin usage. Recommendations, timeline, risk assessment, etc
- USD support only

## 🔮 Future Enhancements/Improvements

- Google Places API integration for landing page location text field
- User authentication / user accounts
- Connect/attach users to the estimates and inquiry model
- Prevent user ability to increment/decrement estimate results page to see everyone's results (per account or per IP address access only)
- GPT-5 support with fallback models
- Better curate AI prompting and its context
- Generate custom farm image for results page based on user input
- Save questionnaire at every step instead of at completion to understand if users drop-off before estimate generation.
- Animate between each questionnaire step instead of simply appearing
- Better loading page API usage, call generate estimate API first before progress bar updates
- Progressive image loading and a default color for homepage background image
- If user selects the nav bar homepage button or tries to navigate away from questionnaire, alert user if they really want to leave
- Enhance the chart to include millions abbreviation $2M instead of $2000K
- Enhance the chart mouse-over/tap on bars to include more detail
- Include multi-currency support instead of just USD
- API rate limiting
- Caching
- Sentry integration and overall prod features (PostgresDB, Redis caching)
- More user-friendly / better designed error messages
- Better styling for the hectares/acres selector on homepage
- Clean up debug prints
- Add nav bar hamburger menu

## 🌟 Main Features

### 1. **Multi-Step Property Analysis Flow**
- **Landing Page**: Initial property information collection
- **Questionnaire**: Detailed property analysis questions
- **Loading Screen**: Real-time AI processing status
- **Results Page**: Comprehensive AI-generated estimates

### 2. **Data Models**
- **PropertyInquiry**: Detailed property information storage
- **PropertyEstimate**: AI-generated analysis results
- **AIAnalysisLog**: Complete audit trail of AI requests/responses

## 📁 Project Structure

```
valora_earth/
├── main_app/
│   ├── models.py              # Django data models
│   ├── views.py               # View logic and AI integration
│   ├── ai_service.py          # OpenAI API service
│   ├── ai_models.py           # Pydantic validation models
│   ├── admin.py               # Django admin interface
│   ├── urls.py                # App URL routing
│   └── templates/
│       ├── main_app/
│           ├── index.html              # Landing page
│           ├── estimate_questionnaire.html  # Analysis questions
│           ├── loading_screen.html     # AI processing
│           └── estimate_results.html   # Results display
├── valora_earth/
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI application
├── static/
│   ├── valora_earth_logo.svg  # Brand assets
│   ├── ai_chat_bubble.svg     # UI elements
│   ├── farm_background_image.jpg # Background images
│   └── homepage_*.svg         # Icon assets
├── manage.py                   # Django management
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker services (development)
├── Dockerfile                  # Development container
├── pytest.ini                 # Test configuration
├── run_tests.sh               # Test runner script
├── env.example                # Environment template
└── .gitignore                 # Git exclusions
```

## 🛠️ Setup Instructions

### **Prerequisites**
- Python 3.11+
- pip (Python package manager)
- OpenAI API key
- Docker (optional, for containerized deployment)

### **Option 1: Local Development Setup**

#### **1. Clone Repository**
```bash
git clone <repository-url>
cd valora_earth_django
```

#### **2. Create Virtual Environment**
```bash
python -m venv valora_virtual_env
source valora_virtual_env/bin/activate  # On Windows: valora_virtual_env\Scripts\activate
```

#### **3. Install Dependencies**
```bash
cd valora_earth
pip install -r requirements.txt
```

#### **4. Environment Configuration**
Create a `.env` file in the `valora_earth/` directory:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Django Configuration
DEBUG=True
SECRET_KEY=your_secret_key_here
```

#### **5. Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

#### **6. Create Superuser**
```bash
python manage.py createsuperuser
```

#### **7. Run Development Server**
```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

### **Option 2: Docker Setup**

#### **1. Clone and Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd valora_earth

# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

#### **2. Environment Configuration**
Edit `.env` file with your configuration:
```bash
DEBUG=True

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here
```

#### **3. Start Development Environment**
```bash
# Start development environment
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f
```

#### **4. Database Operations (Docker)**
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell
```

### **Docker Configuration**

#### **Services**
- **Web Application**: Django development server
- **Database**: SQLite (file-based, no separate service needed)

## 🧪 Testing

### **Test Structure**
```
main_app/
├── test_main.py          # Main test suite (models, views, AI service)
├── test_ai_models.py     # AI model validation tests
└── ...
```

### **Running Tests**

#### **Using pytest (Recommended)**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest -k "TestPropertyInquiryModel" -v
pytest -k "TestPropertyEstimateViews" -v
pytest -k "TestValoraEarthAIService" -v
```

## 🔌 API Endpoints

### **Core Views**
- `GET /`: Landing page (property estimate form)
- `GET /estimate/`: Property analysis questionnaire
- `GET /loading-estimate/`: AI processing screen
- `GET /estimate-results/<id>/`: Results view

### **API Endpoints**
- `POST /api/generate-estimate/<id>/`: Generate AI estimate

## 📊 Data Models in Detail

### **PropertyInquiry**
- `id`: Auto-generated primary key (BigAutoField)
- `address`: Property location (max 500 chars)
- `lot_size`: Land area as decimal (max 10 digits, 2 decimal places)
- `lot_size_unit`: Unit choice ('acres' or 'hectares', defaults to 'acres')
- `current_property`: Current land description (TextField)
- `property_goals`: Development objectives (TextField)
- `investment_capacity`: Budget and timeline (TextField)
- `preferences_concerns`: Specific requirements (TextField)
- `region`: Geographic location (max 100 chars)
- `created_at`: Timestamp (auto-generated, defaults to timezone.now)

### **PropertyEstimate**
- `id`: Auto-generated primary key (BigAutoField)
- `inquiry`: One-to-one relationship with PropertyInquiry (CASCADE delete)
- `project_name`: AI-generated project title (max 200 chars)
- `project_description`: Detailed analysis (TextField)

- `confidence_score`: AI confidence (0.0-1.0, FloatField)
- `factors_considered`: Analysis factors (JSONField)
- `recommendations`: AI suggestions (JSONField)
- `timeline`: Implementation schedule (max 200 chars)
- `risk_assessment`: Risk analysis and mitigation (TextField)
- `processing_time`: AI processing duration in seconds (FloatField)
- `cash_flow_projection`: 10-year net cash flow projection in USD (JSONField, default=list)
- `revenue_breakdown`: 10-year revenue breakdown by category (JSONField, default=dict)
- `cost_breakdown`: 10-year cost breakdown by category (JSONField, default=dict)
- `ai_response_raw`: Raw AI response data (JSONField)
- `created_at`: Timestamp (auto-generated, defaults to timezone.now)

### **AIAnalysisLog**
- `id`: Auto-generated primary key (BigAutoField)
- `inquiry`: Foreign key to PropertyInquiry (CASCADE delete, related_name='ai_logs')
- `request_data`: Input sent to AI (JSONField)
- `response_data`: AI response (JSONField)
- `model_used`: AI model version (max 100 chars)
- `tokens_used`: API consumption (IntegerField)
- `processing_time`: Analysis duration in seconds (FloatField)
- `success`: Operation status (BooleanField, defaults to True)
- `error_message`: Error details (TextField, blank=True, optional)
- `created_at`: Timestamp (auto-generated, defaults to timezone.now)

### **Model Relationships**
- **PropertyInquiry** → **PropertyEstimate**: One-to-one relationship via `inquiry` field
- **PropertyInquiry** → **AIAnalysisLog**: One-to-many relationship via `inquiry` field (related_name='ai_logs')
- **PropertyEstimate** → **PropertyInquiry**: One-to-one relationship via `inquiry` field (related_name='estimate')