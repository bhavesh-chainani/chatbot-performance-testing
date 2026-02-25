# AWS Setup – Full-Scale Locust (Master + Workers)

Deploy 1 master + 5 workers for load / stress / endurance / breakpoint tests at 500–1000 users.

| Test | Users | Duration |
|------|------:|----------|
| **Load** | 500 | 20 min |
| **Stress** | 750 | 20 min |
| **Endurance** | 500 | 2 hours (fits 70M token budget) |
| **Breakpoint** | ramp to 1000 | 30 min |

**Infrastructure:** 1× `c5.large` (master) + 5× `c5.xlarge` (workers). ~200–250 users per worker.

**Cost:** Running all 4 tests in one session is roughly **$11–$14** (on-demand, us-east-1). See **[docs/AWS_COSTS.md](docs/AWS_COSTS.md)** for a full breakdown.

---

## Prerequisites

1. AWS Account  
2. AWS CLI configured (`aws configure`)  
3. EC2 Key Pair  

---

## Step 0: Get Your Session Cookie

The chatbot uses SSO. Locust authenticates with a **session cookie** from the browser.

1. Open **https://cfoti.org** and log in.  
2. DevTools (F12) → **Application** → **Cookies** → `https://cfoti.org`  
3. Copy the **`session`** cookie value.  
4. Put it in `.env`:

```env
CHATBOT_URL=https://cfoti.org
SESSION_COOKIE=paste-your-session-cookie-value-here
```

Session lasts ~24 hours; refresh if you get 401s.

---

## Step 1: Deploy

```bash
./aws_setup/deploy_locust.sh
```

Use defaults (master `c5.large`, workers `c5.xlarge`, 5 workers) or change as prompted. Enter your key pair name.

---

## Step 2: Get IPs

```bash
./aws_setup/get_ips_simple.sh
```

Set:

```bash
export MASTER_IP=<master-public-ip>
export MASTER_PRIVATE=<master-private-ip>
export KEY=~/.ssh/<your-key>.pem
```

---

## Step 3: Copy files to master

```bash
ssh -i $KEY ec2-user@$MASTER_IP "mkdir -p ~/chatbot-performance-testing"
scp -i $KEY -r src/ config/ .env requirements.txt ec2-user@$MASTER_IP:~/chatbot-performance-testing/
```

---

## Step 4: Copy files to every worker

Use the worker IPs printed by `get_ips_simple.sh`, or:

```bash
aws ec2 describe-instances \
  --filters "Name=tag:aws:cloudformation:stack-name,Values=locust-cluster" "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value|[0],PublicIpAddress]' --output text
```

For each worker IP:

```bash
ssh -i $KEY ec2-user@<worker-ip> "mkdir -p ~/chatbot-performance-testing"
scp -i $KEY -r src/ config/ .env requirements.txt ec2-user@<worker-ip>:~/chatbot-performance-testing/
```

---

## Step 5: Install deps on master and all workers

On **master** and on **each worker**:

```bash
cd ~/chatbot-performance-testing
pip3 install -r requirements.txt
```

---

## Step 6: Start master

SSH to master:

```bash
ssh -i $KEY ec2-user@$MASTER_IP
cd ~/chatbot-performance-testing

TEST_TYPE=load locust -f src/locustfile.py --master
```

Leave this running. Web UI: **http://\<MASTER_IP\>:8089**

---

## Step 7: Start workers

On **each worker** (separate SSH sessions), run:

```bash
cd ~/chatbot-performance-testing
TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE
```

Use **Master Private IP** for `--master-host`. Start all 5 workers, then in the master UI click **Start swarming**.

| Test type | Master | Each worker |
|-----------|--------|-------------|
| Load | `TEST_TYPE=load locust -f src/locustfile.py --master` | `TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE` |
| Stress | `TEST_TYPE=stress ... --master` | `TEST_TYPE=stress ... --worker --master-host=$MASTER_PRIVATE` |
| Endurance | `TEST_TYPE=endurance ... --master` | `TEST_TYPE=endurance ... --worker --master-host=$MASTER_PRIVATE` |
| Breakpoint | `TEST_TYPE=breakpoint ... --master` | `TEST_TYPE=breakpoint ... --worker --master-host=$MASTER_PRIVATE` |

---

## Step 8: Download reports

Reports are on the **master**. From your local machine:

```bash
mkdir -p reports
scp -i $KEY "ec2-user@$MASTER_IP:~/chatbot-performance-testing/reports/*" ./reports/
```

Generate HTML:

```bash
python src/generate_report.py
```

Use `--exclude-empty` to drop rows with no answer.

---

## Step 9: Cleanup

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

---

## Quick reference

| | |
|---|--|
| Deploy | `./aws_setup/deploy_locust.sh` |
| IPs | `./aws_setup/get_ips_simple.sh` |
| Web UI | http://\<master-public-ip\>:8089 |
| Master | `locust -f src/locustfile.py --master` |
| Workers | `locust -f src/locustfile.py --worker --master-host=\<master-private-ip\>` |
