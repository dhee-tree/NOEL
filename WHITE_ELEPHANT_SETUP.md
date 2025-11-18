# White Elephant - The Snatcher Feature 🎲🐘

## Phase 2: Automated Snatcher Selection

### Overview
When a group has `is_white_elephant=true`, the system automatically selects one random member as "The Snatcher" 24 hours before the `gift_exchange_deadline`.

### How It Works

1. **Periodic Check**: Celery Beat runs every hour to check for White Elephant groups
2. **Selection Window**: Groups with gift exchange 23-25 hours away get a Snatcher selected
3. **Random Selection**: One member is randomly chosen (including the organizer)
4. **Notifications**:
   - The Snatcher receives a special email with their power
   - All other members receive a mystery notification

### Setup Instructions

#### 1. Install Redis
You need Redis as the message broker for Celery.

**Windows:**
```bash
# Download Redis from: https://github.com/microsoftarchive/redis/releases
# Or use Windows Subsystem for Linux (WSL)
```

**Mac:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run Celery Worker
Open a new terminal and run:
```bash
source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate
celery -A noelProject worker --loglevel=info
```

#### 4. Run Celery Beat (Scheduler)
Open another terminal and run:
```bash
source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate
celery -A noelProject beat --loglevel=info
```

#### 5. Django Server
In your main terminal:
```bash
source .venv/Scripts/activate
python manage.py runserver
```

### Environment Variables

Add to your `.env` file (optional, defaults to localhost):
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Database Fields Added

**SantaGroup Model:**
- `is_white_elephant` (Boolean) - Enable White Elephant mode
- `snatcher_user_id` (Integer) - The chosen Snatcher's user ID
- `snatch_revealed_at` (DateTime) - When they were notified
- `snatcher_notified` (Boolean) - Notification status

### API Response Example

```json
{
  "group_id": "...",
  "group_name": "Office Party 2024",
  "is_white_elephant": true,
  "snatcher_user_id": 42,  // null until selected
  "snatch_revealed_at": "2024-12-24T10:00:00Z",  // null until selected
  "snatcher_notified": true,
  ...
}
```

### Testing

To manually trigger Snatcher selection for a group:
```python
from Group.tasks import select_snatcher_for_group
select_snatcher_for_group.delay('group-uuid-here')
```

### Email Templates

The system sends two types of emails:

**To The Snatcher:**
- Subject: 🎲 YOU ARE THE SNATCHER! - {group_name}
- Tells them they have the power to steal a gift

**To Everyone Else:**
- Subject: 🕵️ The Snatcher Has Been Chosen - {group_name}
- Mystery notification that someone was chosen

---

**Note**: Make sure Redis is running before starting Celery workers!
