# Chatbot Performance Testing Suite

A comprehensive load testing suite for chatbots built with [Locust](https://locust.io/). Designed for testing chatbot performance with authentication support and Time To First Token (TTF) tracking.

## Features

- ✅ **4 Test Types**: Load, Endurance, Stress, and Breakpoint testing
- ✅ **Load Testing**: Simulate normal expected load conditions
- ✅ **Endurance Testing**: Long duration tests to identify memory leaks and degradation
- ✅ **Stress Testing**: High load beyond normal capacity to find breaking points
- ✅ **Breakpoint Testing**: Gradually increase load until system fails
- ✅ **Authentication Support**: Automatic login flow handling
- ✅ **TTF Tracking**: Time To First Token metrics per question category (Simple, Common, Complex)
- ✅ **Question Categories**: Separate performance metrics for different question types
- ✅ **Detailed Reports**: HTML and CSV reports with comprehensive metrics
- ✅ **Customizable**: Easy to configure test parameters and sample questions
- ✅ **Locust Free Tier Compatible**: Configurations start small and are easily adjustable

## Project Structure

```
.
├── locustfile.py              # Main Locust test file
├── test_config.py             # Centralized test configuration
├── sample_questions.py        # Sample questions organized by category
├── config_load_test.py        # Load test configuration (uses test_config.py)
├── config_endurance_test.py   # Endurance test configuration
├── config_stress_test.py      # Stress test configuration
├── config_breakpoint_test.py  # Breakpoint test configuration
├── run_tests.py               # Test runner script (supports all 4 test types)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Example environment configuration
├── README.md                  # This file
└── reports/                   # Generated test reports
    ├── load_test_report.html  # HTML report
    ├── load_test_report_*.csv # CSV statistics
    └── ttf_data.csv          # TTF metrics per question
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd chatbot_performance_testing
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# CHATBOT_URL=https://your-chatbot-url.com
# LOGIN_EMAIL=your-email@example.com
# LOGIN_PASSWORD=your-password
# API_ENDPOINT_LOGIN=/api/auth/login
# API_ENDPOINT_SEND=/api/chat
```

**Important**: 
- Replace placeholder values in `.env` with your actual credentials
- Never commit `.env` to version control (it's in `.gitignore`)
- The chatbot requires authentication - users login before accessing chat functionality

## Quick Start

### Running Tests

The test suite supports **4 different test types**. All configurations are easily accessible and start small for Locust free tier.

**Basic Usage:**
```bash
# Run load test with defaults
python run_tests.py load

# Run endurance test with defaults
python run_tests.py endurance

# Run stress test with defaults
python run_tests.py stress

# Run breakpoint test with defaults
python run_tests.py breakpoint
```

**With Custom Parameters:**
```bash
# Override defaults (users spawn_rate duration)
python run_tests.py load 10 2 5m
python run_tests.py endurance 5 1 15m
python run_tests.py stress 15 3 5m

# Breakpoint test uses its own configuration (see config_breakpoint_test.py)
python run_tests.py breakpoint
```

**Show Help:**
```bash
python run_tests.py
```

### Test Types Explained

#### 1. Load Test (`load`)
**Purpose**: Test normal expected load conditions - baseline performance testing.

**Default Configuration** (`config_load_test.py`):
- Users: 5 concurrent users
- Spawn Rate: 1 user/second
- Duration: 2 minutes

**Use Case**: Regular performance testing, baseline metrics, production-like load.

**Run:**
```bash
python run_tests.py load
# or with custom parameters
python run_tests.py load 10 2 5m
```

#### 2. Endurance Test (`endurance`)
**Purpose**: Long duration test with moderate load to identify:
- Memory leaks
- Performance degradation over time
- Resource exhaustion issues
- Stability problems

**Default Configuration** (`config_endurance_test.py`):
- Users: 3 concurrent users
- Spawn Rate: 0.5 users/second (slow ramp-up)
- Duration: 10 minutes

**Use Case**: Testing system stability, finding memory leaks, checking for degradation.

**Run:**
```bash
python run_tests.py endurance
# or with custom parameters
python run_tests.py endurance 5 1 30m
```

#### 3. Stress Test (`stress`)
**Purpose**: High load beyond normal capacity to identify:
- Maximum capacity limits
- Performance bottlenecks under stress
- Error handling under high load
- System recovery capabilities

**Default Configuration** (`config_stress_test.py`):
- Users: 10 concurrent users
- Spawn Rate: 2 users/second (faster ramp-up)
- Duration: 5 minutes

**Use Case**: Finding breaking points, testing error handling, capacity planning.

**Run:**
```bash
python run_tests.py stress
# or with custom parameters
python run_tests.py stress 20 3 5m
```

#### 4. Breakpoint Test (`breakpoint`)
**Purpose**: Gradually increase load until system fails - finds exact breaking point.

**How it works**: Starts with low load and gradually increases users at each step until failure is detected.

**Default Configuration** (`config_breakpoint_test.py`):
- Start Users: 1
- Max Users: 15
- Spawn Rate: 1 user/second
- Step Duration: 1 minute per load level
- User Increment: +2 users per step

**Use Case**: Finding exact capacity limits, testing graceful degradation.

**Run:**
```bash
python run_tests.py breakpoint
```

**Note**: Breakpoint test uses its own configuration. Edit `config_breakpoint_test.py` to customize.

**Consolidated Report**: The breakpoint test generates a single `breakpoint_test_summary.html` report that shows:
- All steps in a single table
- Key metrics for each step (requests, failures, response times, RPS)
- Visual highlighting of the breaking point
- Easy comparison across load levels

Open `reports/breakpoint_test_summary.html` to see the complete analysis at a glance!

### Configuration Files

All test configurations are easily accessible:

- **`test_config.py`**: Centralized configuration (all test types)
- **`config_load_test.py`**: Load test specific config
- **`config_endurance_test.py`**: Endurance test specific config
- **`config_stress_test.py`**: Stress test specific config
- **`config_breakpoint_test.py`**: Breakpoint test specific config

**Easy Configuration**: Edit any config file or set environment variables. All configs start small for Locust free tier and can be easily adjusted.

### Using Locust Directly

You can also run tests directly with Locust:

```bash
# Load test
locust -f locustfile.py --users 5 --spawn-rate 1 --run-time 2m --host https://cfoti.org --headless --html reports/load_test_report.html --csv reports/load_test_report

# Interactive Web UI
locust -f locustfile.py --host https://cfoti.org
```
Then open `http://localhost:8089` in your browser to configure and run tests interactively.

### What Gets Tested

The load test will:
1. Login with your credentials from `.env`
2. Navigate to the chat page
3. Send random chat messages (Simple, Common, Complex questions)
4. Track Time To First Token (TTF) for each question
5. Generate performance reports

### Test Configuration

**Easy Configuration**: All test settings are centralized in `test_config.py` and individual config files for easy management.

**Default Parameters by Test Type:**

| Test Type | Users | Spawn Rate | Duration | Purpose |
|-----------|-------|------------|----------|---------|
| **Load** | 5 | 1/sec | 2m | Normal expected load |
| **Endurance** | 3 | 0.5/sec | 10m | Long duration, moderate load |
| **Stress** | 10 | 2/sec | 5m | High load beyond capacity |
| **Breakpoint** | 1→15 | 1/sec | 1m/step | Gradual increase until failure |

**Common Settings** (all test types):
- **Wait Time**: 2-5 seconds between tasks
- **Task Weights**: Chat page (3), Send message (5)

**Configuration Options:**
1. Edit config files: `config_*_test.py` for test-specific settings
2. Edit `test_config.py` for global settings
3. Set environment variables (takes precedence)
4. Pass command-line arguments (overrides config)

**Example - Customizing Load Test:**
```python
# Edit config_load_test.py or test_config.py
LOAD_TEST_USERS = 10
LOAD_TEST_SPAWN_RATE = 2
LOAD_TEST_RUN_TIME = "5m"
```

**Example - Using Environment Variables:**
```bash
export LOAD_TEST_USERS=10
export LOAD_TEST_SPAWN_RATE=2
export LOAD_TEST_RUN_TIME=5m
python run_tests.py load
```

## API Structure

The chatbot requires authentication:

1. **Login Flow**:
   - **GET**: `/` - Load login page
   - **POST**: `/api/login` (or `/api/auth/login`, `/login`, etc.) - Authenticate user
   - **GET**: `/chat` - Access chat page (after login)

2. **Chat API**:
   - **POST**: `/api/chat` - Send messages to the chatbot
   - **GET**: `/chat` - Load the chat page

**Login Request Format**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Chat Request Format**:
```json
{
  "message_content": "Your message here"
}
```

**Response**: The API returns JSON with the chatbot's response. The exact structure may vary.

**Note**: Authentication is handled automatically. The test suite logs in each user before accessing the chat functionality.

## Reports

Test reports are saved in the `reports/` directory:

**Report Files by Test Type:**
- **Load Test**: 
  - `reports/load_test_report.html`
  - `reports/load_test_report_*.csv`
- **Endurance Test**: 
  - `reports/endurance_test_report.html`
  - `reports/endurance_test_report_*.csv`
- **Stress Test**: 
  - `reports/stress_test_report.html`
  - `reports/stress_test_report_*.csv`
- **Breakpoint Test**: 
  - `reports/breakpoint_test_summary.html` - **Consolidated summary report** (shows all steps and breaking point)
  - `reports/breakpoint_test_step_{N}_{users}users.html` (individual step reports)
  - `reports/breakpoint_test_step_{N}_{users}users_*.csv` (individual step CSVs)

**Shared Data:**
- **TTF Data**: `reports/ttf_data.csv` - Time To First Token metrics per question (shared across all tests)

### Time To First Token (TTF) Tracking

The test suite automatically tracks **Time To First Token (TTF)** for each question category:

**TTF CSV File** (`reports/ttf_data.csv`):
- **Timestamp**: When the question was asked
- **Question_Category**: Simple, Common, or Complex
- **Question_Text**: The actual question asked (truncated to 100 chars)
- **TTF_ms**: Time to first token in milliseconds
- **Total_Response_Time_ms**: Complete response time
- **Status**: Success or error status

**Locust Statistics**:
- Separate metrics for each question category:
  - `Send Chat Message - Simple`
  - `Send Chat Message - Common`
  - `Send Chat Message - Complex`

**Use Cases**:
- Compare TTF across question types (Simple vs Complex)
- Identify performance bottlenecks for specific question categories
- Generate reports showing average TTF per category
- Analyze if complex questions take significantly longer to start responding

**Example Analysis**:
```python
import pandas as pd

# Load TTF data
df = pd.read_csv('reports/ttf_data.csv')

# Average TTF by category
avg_ttf = df.groupby('Question_Category')['TTF_ms'].mean()
print(avg_ttf)

# TTF percentiles by category
percentiles = df.groupby('Question_Category')['TTF_ms'].describe()
print(percentiles)
```

## Understanding Load Test Metrics

### Key Metrics Tracked

1. **Response Times**: 
   - Median, 95th percentile, 99th percentile
   - Average response time
   - Min/Max response times

2. **Time To First Token (TTF)**:
   - TTF for Simple questions
   - TTF for Common questions  
   - TTF for Complex questions
   - Available in `reports/ttf_data.csv`

3. **Throughput**:
   - Requests per second (RPS)
   - Current RPS during test

4. **Error Rates**:
   - Number of failed requests
   - Failure rate percentage

### What to Look For

- **Response Times**: Should be consistent and within acceptable limits
- **TTF Differences**: Compare TTF between Simple vs Complex questions
- **Error Rates**: Should be low (< 1% ideally)
- **Throughput**: How many requests the system can handle per second

## Customization

### How Sample Questions Work

**Yes, you provide sample questions!** The test suite uses a pool of sample messages that simulate real user interactions:

1. **Random Selection**: Each virtual user randomly picks a question from the combined sample messages
2. **Realistic Distribution**: Questions are weighted by frequency:
   - Simple messages (greetings): 2x weight
   - Common questions: 3x weight (most realistic)
   - Complex questions: 3x weight
3. **Wait Times**: Users wait 2-5 seconds between messages (simulating reading responses)

**Current Setup** (`sample_questions.py`):
- `SIMPLE_MESSAGES`: Quick greetings ("Hello", "Hi", "Thanks")
- `COMMON_QUESTIONS`: Typical user queries (trade certificates, FTA eligibility)
- `COMPLEX_QUESTIONS`: Detailed multi-part questions

### Modifying Test Scenarios

**1. Change Sample Questions** (Edit `sample_questions.py`):

This is now super easy! Just edit `sample_questions.py`:

```python
# Simple/Greeting Messages
SIMPLE_MESSAGES = [
    "Hello",
    "Hi",
    "Good morning",
    # Add your custom simple messages here
]

# Common Questions
COMMON_QUESTIONS = [
    "What are your business hours?",
    "Tell me about your services",
    # Add your custom common questions here
]

# Complex Questions
COMPLEX_QUESTIONS = [
    "Your complex multi-part question here",
    # Add your custom complex questions here
]

# Adjust weights (how frequently each category appears)
SIMPLE_WEIGHT = 2      # Simple messages appear 2x more often
COMMON_WEIGHT = 3      # Common questions appear 3x more often
COMPLEX_WEIGHT = 3     # Complex questions appear less frequently
```

**2. Configure Test Settings** (Edit `test_config.py`):

All test configuration is centralized in `test_config.py`:

```python
# API Configuration
CHATBOT_URL = "https://your-chatbot-url.com"
API_ENDPOINT_LOGIN = "/api/auth/login"
API_ENDPOINT_SEND = "/api/chat"

# User Behavior Configuration
WAIT_TIME_MIN = 2      # Minimum wait time between tasks (seconds)
WAIT_TIME_MAX = 5      # Maximum wait time between tasks (seconds)

# Task Weights Configuration
TASK_WEIGHT_CHAT_PAGE = 3      # How often to load chat page
TASK_WEIGHT_SEND_MESSAGE = 5   # How often to send messages (higher = more frequent)

# Load Test Configuration
DEFAULT_USERS = 5              # Number of concurrent users
DEFAULT_SPAWN_RATE = 1         # Users spawned per second
DEFAULT_RUN_TIME = "2m"         # Test duration
```

**3. API Endpoints:**
- Update environment variables in `.env` file

### Adjusting Test Parameters

Modify test parameters in config files or pass them via command line (see examples above).

## Troubleshooting

### API Endpoint Issues
1. Verify `API_ENDPOINT_SEND` in `.env` file (defaults to `/api/chat`)
2. Check if API structure matches expected format
3. Modify request payloads in `locustfile.py` if needed
4. Check browser Network tab to see the exact request format

### Connection Errors
- Verify `CHATBOT_URL` is correct in `.env` (defaults to `https://cfoti.org`)
- Check network connectivity
- Ensure the chatbot service is running

### Authentication Issues
- **404 Not Found on Login**: 
  - The login endpoint might be different from the defaults
  - **How to find the correct login endpoint:**
    1. Open your browser and go to `https://cfoti.org`
    2. Open DevTools (F12 or Right-click → Inspect)
    3. Go to the **Network** tab
    4. Clear the network log
    5. Enter your credentials and click Submit/Login
    6. Look for the POST request that succeeds (status 200 or 302)
    7. Copy the endpoint URL (e.g., `/api/auth/login` or `/auth/signin`)
    8. Update `API_ENDPOINT_LOGIN` in your `.env` file with the correct endpoint
  - The code tries multiple common endpoints automatically, but if none work, you need to find the exact one
- **401 Unauthorized Errors**: 
  - Verify `LOGIN_EMAIL` and `LOGIN_PASSWORD` are set correctly in `.env`
  - Check if credentials are correct
- **422 Validation Error on Chat Messages**:
  - **Fixed**: The code now uses `message_content` instead of `message` in the payload
  - If you still see 422 errors, check the browser Network tab to see the exact payload format expected
  - Update the payload format in `locustfile.py` if needed
- **Session Expired**:
  - The code automatically re-authenticates if a session expires
  - Check logs for re-authentication attempts

## Example Output

After running a test, you'll see output like:

```
============================================================
CHATBOT LOAD TEST
============================================================
Users: 5
Spawn Rate: 1 users/second
Duration: 2m
Host: https://cfoti.org
------------------------------------------------------------

This test will:
  • Login with credentials from .env
  • Send chat messages (Simple, Common, Complex questions)
  • Track Time To First Token (TTF) for each question
  • Generate performance reports

Starting test...
```

## Analyzing Results

### HTML Report
Open `reports/load_test_report.html` in your browser to view:
- Response time statistics (median, 95th percentile, 99th percentile)
- Requests per second (RPS)
- Error rates
- Separate metrics for each question category

### TTF Analysis
Use the `reports/ttf_data.csv` file to analyze Time To First Token:

```python
import pandas as pd

# Load TTF data
df = pd.read_csv('reports/ttf_data.csv')

# Average TTF by category
avg_ttf = df.groupby('Question_Category')['TTF_ms'].mean()
print("Average TTF by Category:")
print(avg_ttf)

# TTF statistics
stats = df.groupby('Question_Category')['TTF_ms'].describe()
print("\nDetailed Statistics:")
print(stats)

# Compare Simple vs Complex
simple_avg = df[df['Question_Category'] == 'Simple']['TTF_ms'].mean()
complex_avg = df[df['Question_Category'] == 'Complex']['TTF_ms'].mean()
print(f"\nSimple questions: {simple_avg:.2f}ms avg TTF")
print(f"Complex questions: {complex_avg:.2f}ms avg TTF")
```

## Customization

### Sample Questions

The test suite includes sample questions for **Singapore Business Federation - Centre for the Future of Trade and Investment**, covering:
- Certificate of Origin (PCO, OCO, Back-to-back)
- Free Trade Agreements (FTA)
- Preferential tariffs
- Product eligibility

**Edit `sample_questions.py` to customize questions for your domain** - it's now super easy!

```python
# Simple messages
SIMPLE_MESSAGES = [
    "Hello",
    "Hi",
    # Add your simple questions
]

# Common questions
COMMON_QUESTIONS = [
    "Your common question here",
    # Add domain-specific questions
]

# Complex questions
COMPLEX_QUESTIONS = [
    "Your complex multi-part question here",
    # Add detailed questions
]

# Adjust weights to control frequency
SIMPLE_WEIGHT = 2
COMMON_WEIGHT = 3
COMPLEX_WEIGHT = 3
```

### Test Parameters

**Edit `test_config.py` to change test configuration** - all settings in one place:

```python
# Load Test Configuration
DEFAULT_USERS = 10           # Number of concurrent users
DEFAULT_SPAWN_RATE = 2      # Users spawned per second
    "run_time": "5m",      # Test duration
}
```

## Troubleshooting

### Common Issues

**Login fails with 404:**
- Check browser Network tab to find the correct login endpoint
- Update `API_ENDPOINT_LOGIN` in `.env`

**422 Validation Error:**
- Verify the chat API expects `message_content` (not `message`)
- Check browser Network tab for exact payload format

**Session expired:**
- The code automatically re-authenticates
- Check `.env` credentials are correct

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is provided as-is for performance testing purposes.

## Acknowledgments

- Built with [Locust](https://locust.io/) - An open source load testing tool
- Designed for chatbot performance testing with authentication support
