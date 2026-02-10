# Chatbot API Load Testing on AWS

Simple load testing for your chatbot API using AWS EC2.

## Quick Setup

1. **Configure `.env`:**
```env
CHATBOT_URL=https://your-chatbot-url.com
LOGIN_EMAIL=your-email@example.com
LOGIN_PASSWORD=your-password
API_ENDPOINT_LOGIN=/api/auth/login
API_ENDPOINT_SEND=/api/chat
```

2. **Deploy and run:**
```bash
./aws_setup/deploy_locust.sh
# Follow SIMPLE_SETUP.md for step-by-step instructions
```

## Documentation

- **[SIMPLE_SETUP.md](SIMPLE_SETUP.md)** - Step-by-step guide for 10 concurrent users

## Project Structure

```
.
├── src/                    # Test code
│   ├── locustfile.py      # Main test
│   └── sample_questions.py
├── config/                 # Configuration
│   └── test_config.yaml   # Test parameters
├── aws_setup/             # AWS deployment
│   └── deploy_locust.sh   # Deploy script
└── .env                    # Your credentials
```

That's it!
