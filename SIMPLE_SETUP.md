# AWS Setup Guide – Chatbot Performance Testing

Deploy a Locust cluster on AWS EC2 to run 4 test types against your chatbot.

| Test | Concurrent Users | Duration | Purpose |
|------|----------------:|----------|---------|
| **Load** | 500 | 20 min | Baseline under expected traffic |
| **Stress** | 750 | 20 min | Beyond normal capacity |
| **Endurance** | 500 | 8 hours | Sustained load, detect memory leaks |
| **Breakpoint** | ramp to 1000 | 30 min | Find the breaking point |

---

## Prerequisites

1. AWS Account with `ec2:*` and `cloudformation:*` permissions
2. AWS CLI installed and configured (`aws configure`)
3. An EC2 Key Pair

---

## Step 1: Create an EC2 Key Pair (if you don't have one)

```bash
aws ec2 create-key-pair \
  --key-name locust-testing \
  --query 'KeyMaterial' --output text > ~/.ssh/locust-testing.pem

chmod 400 ~/.ssh/locust-testing.pem
```

---

## Step 2: Deploy the Cluster

```bash
./aws_setup/deploy_locust.sh
```

When prompted, use these recommended settings:

| Parameter | Recommended | Why |
|-----------|-------------|-----|
| Master instance | `c5.large` | Coordinates workers + web UI |
| Worker instance | `c5.xlarge` | 4 vCPU, 8 GB – generates load |
| Worker count | **3** | 3 workers handles up to 1000 users comfortably |

Wait 3-5 minutes for the stack to finish.

> **Cost note:** A 3-worker `c5.xlarge` cluster costs ~$0.68/hr. Don't forget to tear it down when done (Step 9).

---

## Step 3: Get Instance IPs

```bash
./aws_setup/get_ips_simple.sh
```

You'll get two IPs — save both:
- **Master Public IP** → for SSH and browser access (e.g. `54.226.255.173`)
- **Master Private IP** → for worker `--master-host` flag (e.g. `172.31.16.115`)

```bash
# Set these for the rest of the guide:
export MASTER_PUBLIC_IP=<your-master-public-ip>
export MASTER_PRIVATE_IP=<your-master-private-ip>
export KEY=~/.ssh/locust-testing.pem
```

---

## Step 4: Copy Project Files to EC2

```bash
# Create directory on master
ssh -i $KEY ec2-user@$MASTER_PUBLIC_IP \
  "mkdir -p ~/chatbot-performance-testing && sudo chown -R ec2-user:ec2-user ~/chatbot-performance-testing"

# Copy files
scp -i $KEY -r src/ config/ .env requirements.txt \
  ec2-user@$MASTER_PUBLIC_IP:~/chatbot-performance-testing/
```

If workers are on **separate instances**, repeat the copy for each worker IP.

---

## Step 5: Install Dependencies on EC2

SSH into the master (and each worker if separate):

```bash
ssh -i $KEY ec2-user@$MASTER_PUBLIC_IP
```

Then on the instance:

```bash
cd ~/chatbot-performance-testing
pip3 install -r requirements.txt
pip3 install "urllib3<2.0" --upgrade   # Amazon Linux 2 compatibility fix
```

---

## Step 6: Run a Test

Pick a test type and start the master, then the workers.

### Start the Master

On the master instance:

```bash
cd ~/chatbot-performance-testing

# Pick one:
TEST_TYPE=load       locust -f src/locustfile.py --master
# TEST_TYPE=stress     locust -f src/locustfile.py --master
# TEST_TYPE=endurance  locust -f src/locustfile.py --master
# TEST_TYPE=breakpoint locust -f src/locustfile.py --master
```

Keep this terminal open — you'll see "Waiting for workers to connect."

### Start Each Worker

Open a new terminal, SSH into each worker instance, and run:

```bash
cd ~/chatbot-performance-testing

# Use the SAME TEST_TYPE as the master:
TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=<MASTER_PRIVATE_IP>
```

> **Important:** Use the **private IP** for `--master-host`, not the public IP.

### Launch from the Web UI

Open your browser:

```
http://<MASTER_PUBLIC_IP>:8089
```

The settings per test type:

| Test | Users | Spawn Rate | Run Time |
|------|------:|-----------:|----------|
| Load | 500 | 25/s | 20m |
| Stress | 750 | 38/s | 20m |
| Endurance | 500 | 25/s | 8h |
| Breakpoint | *(auto-ramped by shape class)* | — | 30m |

For **load / stress / endurance**: enter the Users and Spawn Rate, click "Start swarming", and stop after the run time.

For **breakpoint**: the `BreakpointShape` class handles ramping automatically — just click Start.

---

## Step 7: Download Reports

**From your local machine** (not EC2):

```bash
mkdir -p reports

# Download the CSV
scp -i $KEY ec2-user@$MASTER_PUBLIC_IP:~/chatbot-performance-testing/reports/* ./reports/
```

---

## Step 8: Generate HTML Report

```bash
python src/generate_report.py
```

This reads each `reports/response_times_<test_type>.csv` and generates a `reports/report_<test_type>.html` file containing:

- **Summary cards** — avg, median, p95, p99, max response times
- **Per-category breakdown** — Simple vs Complex question stats
- **Full request table** — every question asked, the chatbot's answer, and the e2e response time

Open the HTML in a browser to view the report.

---

## Step 9: Cleanup (Important!)

Delete the CloudFormation stack to stop billing:

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

Verify deletion:

```bash
aws cloudformation describe-stacks --stack-name locust-cluster
# Should return "DELETE_IN_PROGRESS" or error once deleted
```

---

## Quick Reference

```bash
# SSH into master
ssh -i $KEY ec2-user@$MASTER_PUBLIC_IP

# Run all 4 tests back-to-back (on master):
cd ~/chatbot-performance-testing
for t in load stress endurance breakpoint; do
  echo "=== Starting $t test ==="
  TEST_TYPE=$t locust -f src/locustfile.py --master --headless \
    --expect-workers=3 --run-time=$(grep run_time config/test_config.yaml | grep $t -A3 | head -1 | awk '{print $2}' | tr -d '"')
done
```

## IP Summary

- **Public IP** → SSH from your machine, open web UI at `:8089`
- **Private IP** → Worker's `--master-host` value (internal AWS network)
