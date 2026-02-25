# AWS Setup Guide – Simple Tests

Deploy a single EC2 instance to run all 4 test types against your chatbot.

| Test | Users | Duration |
|------|------:|----------|
| **Load** | 10 | 5 min |
| **Stress** | 10 | 5 min |
| **Endurance** | 10 | 10 min |
| **Breakpoint** | ramp to 20 | 5 min |

**Infrastructure:** 1x `t3.small` (~$0.02/hr). No workers needed.

---

## Prerequisites

1. AWS Account
2. AWS CLI configured (`aws configure`)
3. EC2 Key Pair

---

## Step 1: Create EC2 Key Pair (if you don't have one)

```bash
aws ec2 create-key-pair \
  --key-name locust-testing \
  --query 'KeyMaterial' --output text > ~/.ssh/locust-testing.pem

chmod 400 ~/.ssh/locust-testing.pem
```

---

## Step 2: Deploy the Instance

```bash
./aws_setup/deploy_locust.sh
```

When prompted:
- Stack name: `locust-cluster` (default)
- Key Pair: your key name (e.g. `locust-testing`)
- Instance type: `t3.small` (default, plenty for 10-20 users)

Wait 2-3 minutes.

---

## Step 3: Get Instance IP

```bash
./aws_setup/get_ips_simple.sh
```

Save the IP:

```bash
export IP=<your-instance-ip>
export KEY=~/.ssh/locust-testing.pem
```

---

## Step 4: Copy Files to EC2

```bash
ssh -i $KEY ec2-user@$IP \
  "mkdir -p ~/chatbot-performance-testing && sudo chown -R ec2-user:ec2-user ~/chatbot-performance-testing"

scp -i $KEY -r src/ config/ .env requirements.txt \
  ec2-user@$IP:~/chatbot-performance-testing/
```

---

## Step 5: Install Dependencies

```bash
ssh -i $KEY ec2-user@$IP
```

On the instance:

```bash
cd ~/chatbot-performance-testing
pip3 install -r requirements.txt
pip3 install "urllib3<2.0" --upgrade
```

---

## Step 6: Run a Test

Still on the EC2 instance — pick a test type and run Locust directly (no master/worker):

```bash
cd ~/chatbot-performance-testing

# Load test (10 users, 5 min)
TEST_TYPE=load locust -f src/locustfile.py

# Stress test (10 users, 5 min)
TEST_TYPE=stress locust -f src/locustfile.py

# Endurance test (10 users, 10 min)
TEST_TYPE=endurance locust -f src/locustfile.py

# Breakpoint test (ramp to 20 users, 5 min)
TEST_TYPE=breakpoint locust -f src/locustfile.py
```

Open the web UI in your browser:

```
http://<your-instance-ip>:8089
```

| Test | Users | Spawn Rate |
|------|------:|-----------:|
| Load | 10 | 2/s |
| Stress | 10 | 2/s |
| Endurance | 10 | 2/s |
| Breakpoint | *(auto-ramped)* | — |

Click **Start swarming**. For breakpoint, the shape class handles ramping automatically.

### Headless mode (no browser)

Run all 4 tests back-to-back without the web UI:

```bash
cd ~/chatbot-performance-testing

TEST_TYPE=load locust -f src/locustfile.py --headless -u 10 -r 2 --run-time 5m
TEST_TYPE=stress locust -f src/locustfile.py --headless -u 10 -r 2 --run-time 5m
TEST_TYPE=endurance locust -f src/locustfile.py --headless -u 10 -r 2 --run-time 10m
TEST_TYPE=breakpoint locust -f src/locustfile.py --headless --run-time 5m
```

---

## Step 7: Download Reports

**From your local machine:**

```bash
mkdir -p reports
scp -i $KEY ec2-user@$IP:~/chatbot-performance-testing/reports/* ./reports/
```

---

## Step 8: Generate HTML Report

```bash
python src/generate_report.py
```

Generates `reports/report_<test_type>.html` with:
- Summary stats (avg, median, p95, p99, max response times)
- Per-category breakdown (Simple vs Complex)
- Full table — every question asked, chatbot answer, and e2e response time

---

## Step 9: Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

---

## Quick Reference

```bash
# SSH in
ssh -i $KEY ec2-user@$IP

# Web UI
http://<IP>:8089

# Tear down
aws cloudformation delete-stack --stack-name locust-cluster
```
