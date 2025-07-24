# Carbon Footprint Tracker

## Overview

A Flask-based web application that helps users track their daily carbon footprint across multiple categories including transportation, electricity usage, diet, cooking gas, waste generation, and water consumption. The application provides personalized eco-friendly suggestions and visualizes emissions data through interactive charts and analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: MVC (Model-View-Controller)
- **Data Storage**: JSON file-based storage system
- **Session Management**: Flask's built-in session handling with secret key configuration
- **Logging**: Python's built-in logging module for debugging and monitoring

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating system)
- **CSS Framework**: Bootstrap 5.3.2 for responsive design
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Charts**: Chart.js library for data visualization
- **Icons**: Font Awesome 6.5.0 for UI icons
- **Theme System**: Light/Dark mode toggle with localStorage persistence

### Data Storage Solution
- **Primary Storage**: SQLite database (cross-platform compatible) with SQLAlchemy ORM
  - `users` table: User accounts with hashed passwords and profile information
  - `emissions` table: User-specific emission records with detailed category breakdowns
  - Foreign key relationships ensuring data isolation between users
  - Database file: `carbon_tracker.db` (automatically created)
  - Falls back to PostgreSQL if DATABASE_URL environment variable is set
- **Session Storage**: Flask-Login session management for authentication
- **Client Storage**: localStorage for theme preferences
- **Legacy Support**: `data/eco_facts.json` for environmental facts and tips

### Recent Changes (July 23, 2025)
- Fixed history page calculation errors by implementing flat data structure
- Added PDF export/print functionality on results page
- Enhanced dark mode styling with proper text visibility and contrast
- Improved data storage with both flat structure for calculations and breakdown for compatibility
- Updated chart themes to adapt to light/dark mode switching
- Fixed template filter errors and improved error handling
- **Implemented Complete Multi-User Authentication System (July 24, 2025)**:
  - Cross-platform SQLite database integration with SQLAlchemy ORM
  - Compatible with both Replit and local development environments
  - User registration (Sign Up) with unique username/email validation
  - Secure login (Sign In) with bcrypt password hashing
  - User-specific data isolation - each user sees only their own emission records
  - Session management with Flask-Login and "Remember Me" functionality
  - Access control for all protected routes (index, calculate, history)
  - Separate dedicated Sign In (/signin) and Sign Up (/signup) pages
  - Updated navbar to show authenticated user info
  - Secure logout with session clearing
  - User and Emission database models with proper relationships
  - Automatic database creation on first run

## Key Components

### Core Application (app.py)
- **Emission Calculation Engine**: Pre-defined emission factors for all categories
- **Route Handlers**: RESTful endpoints for form submission and data retrieval
- **Data Processing**: Algorithms to calculate category-wise and total emissions
- **Suggestion Engine**: Logic to generate personalized eco-friendly recommendations

### Frontend Components
- **Daily Tracking Form**: Multi-category input form with dynamic fields
- **Results Dashboard**: Charts and breakdowns of calculated emissions
- **History Analytics**: Trend analysis and statistics over time
- **Theme Toggle**: Dark/light mode switcher with smooth transitions

### Data Categories
1. **Transportation**: Vehicle type, fuel type, distance tracking
2. **Electricity**: Appliance usage with time-based calculations
3. **Diet**: Meal type selection with meat consumption tracking
4. **Cooking Gas**: LPG usage monitoring
5. **Waste Management**: Recycling behavior tracking
6. **Water Usage**: Daily consumption measurement

## Data Flow

1. **Input Collection**: User fills daily tracking form with multiple category data
2. **Data Validation**: Client-side validation ensures at least one category has valid input
3. **Emission Calculation**: Backend processes input using predefined emission factors
4. **Data Persistence**: Results stored in JSON format with timestamp
5. **Visualization**: Charts generated client-side using Chart.js
6. **Recommendations**: Personalized suggestions based on highest emission categories
7. **Historical Analysis**: Trend tracking and statistics calculation for progress monitoring

## External Dependencies

### CDN Resources
- **Bootstrap 5.3.2**: UI framework and responsive design
- **Font Awesome 6.5.0**: Icon library for enhanced UX
- **Chart.js**: Data visualization and charting library

### Python Packages
- **Flask**: Web framework and routing
- **Standard Library**: datetime, json, logging, os modules

### Browser APIs
- **localStorage**: Theme preference persistence
- **Date API**: Date picker functionality
- **Custom Events**: Theme change notifications

## Deployment Strategy

### Development Environment
- **Entry Point**: `main.py` launches Flask development server
- **Configuration**: Environment variable support for session secrets
- **Debug Mode**: Enabled for development with detailed error reporting
- **Host Configuration**: Binds to all interfaces (0.0.0.0) on port 5000

### Production Considerations
- **Secret Key Management**: Environment variable configuration for security
- **Data Persistence**: JSON file storage suitable for single-user or small-scale deployments
- **Scalability**: Current architecture supports easy migration to database storage
- **Static Assets**: Served through Flask's static file handling

### File Structure
```
├── app.py                 # Main application logic
├── main.py               # Application entry point
├── data/                 # Data storage directory
│   ├── emissions.json    # User emission data
│   └── eco_facts.json    # Environmental facts
├── static/               # Static assets
│   ├── script.js         # Client-side JavaScript
│   └── style.css         # Custom styling
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Daily tracking form
    ├── result.html       # Results dashboard
    └── history.html      # Analytics page
```

The application is designed as a self-contained system with minimal external dependencies, making it suitable for rapid deployment and easy maintenance. The modular architecture allows for future enhancements such as user authentication, database integration, and advanced analytics features.