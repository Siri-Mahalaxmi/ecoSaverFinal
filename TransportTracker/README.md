# Carbon Footprint Tracker

A comprehensive Flask-based web application for tracking daily carbon footprint across multiple categories including transportation, electricity, diet, gas, waste, and water consumption.

## Features

- **Multi-User Authentication**: Secure sign-up/sign-in with password hashing
- **Daily Tracking**: Track CO₂ emissions across 6 major categories
- **Data Visualization**: Interactive charts and analytics
- **History & Analytics**: View trends and statistics over time
- **Personalized Suggestions**: Eco-friendly recommendations based on usage
- **Dark/Light Theme**: Toggle between themes with persistence
- **Cross-Platform**: Works on both Replit and local environments

## Local Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install Flask==3.0.0 Flask-SQLAlchemy==3.1.1 Flask-Login==0.6.3 Werkzeug==3.0.1 bcrypt==4.2.0
   ```

3. **Set environment variable (optional)**:
   ```bash
   # On Windows
   set SESSION_SECRET=your-secret-key-here
   
   # On Mac/Linux
   export SESSION_SECRET=your-secret-key-here
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the app**:
   Open your browser and go to `http://localhost:5000`

### Database

The application uses SQLite by default, which creates a `carbon_tracker.db` file automatically. This file stores all user accounts and emission data.

- **Local**: Uses `carbon_tracker.db` SQLite file
- **Replit**: Falls back to PostgreSQL if DATABASE_URL is set

### File Structure

```
├── app.py              # Main application logic
├── main.py             # Application entry point
├── models.py           # Database models (User, Emission)
├── carbon_tracker.db   # SQLite database (auto-created)
├── data/               # Static data files
│   └── eco_facts.json  # Environmental facts
├── static/             # CSS, JavaScript, images
│   ├── style.css
│   └── script.js
└── templates/          # HTML templates
    ├── signin.html     # Sign in page
    ├── signup.html     # Sign up page
    ├── base.html       # Base template
    ├── index.html      # Daily tracking form
    ├── result.html     # Results page
    └── history.html    # Analytics page
```

## Usage

1. **Create Account**: Visit `/signup` to create a new account with username, email, and password
2. **Sign In**: Visit `/signin` (or root `/`) to log in with existing credentials
3. **Track Daily Emissions**: Fill out the daily tracking form on the dashboard
4. **View Results**: See your carbon footprint breakdown and personalized suggestions
5. **Check History**: Analyze your trends and statistics over time

### Available Routes

- `/` - Main dashboard (redirects to sign-in if not authenticated)
- `/signin` - Sign in page
- `/signup` - Sign up page  
- `/dashboard` - Daily tracking form (requires authentication)
- `/history` - Analytics and history page (requires authentication)
- `/logout` - Log out and return to sign-in page

## Data Categories

- **Transportation**: Vehicle type, fuel, distance
- **Electricity**: Appliance usage and hours
- **Diet**: Meal types and meat consumption
- **Gas**: LPG usage for cooking
- **Waste**: Amount and recycling habits
- **Water**: Daily consumption

## Development

To run in development mode with debug enabled:

```bash
python main.py
```

The application will be available at `http://localhost:5000` with auto-reload enabled.

## Security Features

- Password hashing with bcrypt
- Session management with Flask-Login
- User data isolation
- CSRF protection through Flask sessions
- Secure cookie settings

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

- **Database Issues**: Delete `carbon_tracker.db` to reset the database
- **Port Conflicts**: Change the port in `main.py` if 5000 is occupied
- **Import Errors**: Ensure all dependencies are installed with pip