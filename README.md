# Las Vegas Slot Machine - Django Implementation

A full-stack slot machine game built with Django and vanilla JavaScript that ensures "the house always wins" through clever server-side logic and tricky UI elements.

## 🎰 Game Features

### Core Functionality
- **Session Management**: Each player gets a unique session with 10 starting credits
- **Slot Machine**: 3-reel slot machine with 4 symbols (Cherry, Lemon, Orange, Watermelon)
- **Credit System**: Players spend 1 credit per roll, win credits based on symbol values
- **Cash Out**: Players can attempt to cash out their winnings (with a twist!)

### The House Always Wins Features

#### Server-Side Cheating
The server implements sophisticated cheating logic based on player credits:

- **< 40 credits**: Fair play (0% chance of cheating)
- **40-60 credits**: 30% chance to re-roll winning combinations
- **> 60 credits**: 60% chance to re-roll winning combinations

#### Client-Side Trickery
The "Cash Out" button has mischievous behavior:
- **50% chance**: Button moves randomly by 300px when hovered
- **40% chance**: Button becomes unclickable temporarily
- **10% chance**: Actually allows cash out

## 🚀 Setup and Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Clone and Navigate**
   ```bash
   cd The-House-Always-Wins
   ```

2. **Set up Virtual Environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Game**
   Open your browser and navigate to: `http://127.0.0.1:8000/`

## 🎮 How to Play

1. **Start**: A new session automatically creates when you load the page
2. **Roll**: Click "Pull Lever" to spin the slots (costs 1 credit)
3. **Win**: Match 3 identical symbols to win credits:
   - 🍒 Cherry = 10 credits
   - 🍋 Lemon = 20 credits  
   - 🍊 Orange = 30 credits
   - 🍉 Watermelon = 40 credits
4. **Cash Out**: Try to click "Cash Out" to move credits to your account... if you can! 😈

## 🏗️ Architecture

### Backend (Django)
- **Models**: `GameSession` and `GameRoll` for data persistence
- **Views**: RESTful API endpoints for game operations
- **Business Logic**: Server-side cheating and game mechanics

### Frontend (Vanilla JavaScript)
- **Single Page Application**: All interactions via AJAX
- **Animations**: CSS animations for spinning slots and visual feedback
- **Responsive Design**: Works on desktop and mobile devices

### API Endpoints
- `POST /api/create-session/` - Create new game session
- `POST /api/roll/` - Roll the slot machine
- `POST /api/cash-out/` - Attempt to cash out
- `GET /api/session/<id>/` - Get session status

## 🧪 Testing

Run the comprehensive test suite:

```bash
python manage.py test
```

### Test Coverage
- **Model Tests**: Session management, credit handling
- **Logic Tests**: Winning combinations, cheating algorithms
- **API Tests**: All endpoints and error conditions
- **Integration Tests**: Complete game flow

## 📁 Project Structure

```
the-house-always-wins-rdeyqm/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── slotmachine/             # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── game/                    # Main game application
│   ├── models.py           # Database models
│   ├── views.py            # API endpoints and logic
│   ├── urls.py             # URL routing
│   ├── tests.py            # Comprehensive tests
│   └── templates/game/
│       └── index.html      # Game interface
└── README_IMPLEMENTATION.md
```

## 🎯 Game Logic Details

### Cheating Algorithm
```python
def should_server_cheat(current_credits, potential_win_credits):
    future_credits = current_credits + potential_win_credits
    
    if future_credits < 40:
        return False  # Fair play
    elif 40 <= future_credits <= 60:
        return random.random() < 0.3  # 30% cheat chance
    else:
        return random.random() < 0.6  # 60% cheat chance
```

### Cash Out Trickery
The cash out button implements client-side interference:
- Uses `Math.random()` to determine behavior
- CSS transforms for button movement
- Temporary state changes for "unclickable" mode
- Visual feedback to frustrate players appropriately

## 🔧 Configuration

### Django Settings
- **Database**: SQLite (default, no additional setup required)
- **Debug Mode**: Enabled for development
- **CSRF**: Exempt for API endpoints (game-specific)

### Customization Options
- Modify symbol rewards in `views.py`
- Adjust cheating percentages in `should_server_cheat()`
- Change cash out button behavior probabilities
- Customize UI colors and animations in `index.html`

## 🐛 Troubleshooting

### Common Issues

1. **"django-admin not found"**
   - Ensure Django is installed: `pip install django`
   - Activate virtual environment if using one

2. **Database errors**
   - Run migrations: `python manage.py migrate`
   - Delete `db.sqlite3` and run migrations again if needed

3. **Port already in use**
   - Use different port: `python manage.py runserver 8001`

4. **Static files not loading**
   - Run: `python manage.py collectstatic`

## 🎲 Game Balance

The game is carefully balanced to ensure the house advantage:

- **Early Game**: Fair play to hook players
- **Mid Game**: Moderate cheating to slow down big wins
- **Late Game**: Heavy cheating to prevent massive payouts
- **Cash Out**: Extremely difficult to actually cash out

This creates an engaging but ultimately frustrating experience that demonstrates how "the house always wins" in gambling.

## 📝 Development Notes

- All game state is server-side to prevent client manipulation
- Comprehensive logging via `GameRoll` model for audit trails  
- Responsive design works on mobile devices
- Clean separation between game logic and presentation
- Extensive test coverage for reliability

## 🎭 Easter Eggs

- Watch for the cheeky messages when the cash out button misbehaves
- The server tracks whether it cheated (check the API response)
- Winning combinations get special visual effects
- The game subtly gets harder as you win more

Enjoy the game, and remember... the house always wins! 🎰😈 
