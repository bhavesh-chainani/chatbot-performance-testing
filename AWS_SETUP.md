# AWS Setup – Full-Scale Locust (Master + Workers)

All commands in this guide use the key **`~/.ssh/locust-testing.pem`**. Save your key there, or replace that path in the commands below.

Run everything from your **project directory** (where `src/`, `config/`, `.env`, and `requirements.txt` are) unless a step says you are on the master or a worker.

---

## Test profiles

| Test        | Users  | Duration |
|------------|--------|----------|
| Load       | 500    | 20 min   |
| Stress     | 750    | 20 min   |
| Endurance  | 500    | 2 hours  |
| Breakpoint | to 1000| 30 min   |

**Infrastructure:** 1 master + 2–5 workers. **Cost:** ~$5–$6 for all 4 tests in one go. See [docs/AWS_COSTS.md](docs/AWS_COSTS.md).

---

## Prerequisites

- AWS account, AWS CLI configured (`aws configure`)
- EC2 key pair named `locust-testing` (key file at `~/.ssh/locust-testing.pem`)

**Create the key if needed:**

```bash
aws ec2 create-key-pair --key-name locust-testing --query 'KeyMaterial' --output text > ~/.ssh/locust-testing.pem
chmod 400 ~/.ssh/locust-testing.pem
```

---

## Step 0: Session cookie

1. Log in at **https://cfoti.org** in your browser.
2. DevTools (F12) → Application → Cookies → `https://cfoti.org` → copy the **`session`** cookie value.
3. Put it in `.env` in the project root:

```env
CHATBOT_URL=https://cfoti.org
SESSION_COOKIE=<paste-session-cookie-here>
```

Cookie lasts ~24 hours; refresh if you get 401s.

---

## Step 1: Deploy

From the project directory:

```bash
./aws_setup/deploy_locust.sh
```

When prompted: stack name (Enter for `locust-cluster`), **EC2 Key Pair name: `locust-testing`**, then Enter for the rest (master/worker types, 5 workers). Wait ~3–5 min.

If the stack fails (ROLLBACK_COMPLETE), fix the cause, then:

```bash
aws cloudformation delete-stack --stack-name locust-cluster --region us-east-1
```

Wait until the stack is gone, then run `./aws_setup/deploy_locust.sh` again.

---

## Step 2: Get IPs

From the project directory:

```bash
./aws_setup/get_ips_simple.sh
```

Set these variables (replace with the values from the script output):

```bash
export MASTER_IP=3.87.139.5
export MASTER_PRIVATE=172.31.40.17
export WORKER_IP=3.88.136.146
```

Use your **Master Public IP**, **Master Private IP**, and **Worker IP** (from “Worker instances only”). If you have multiple workers, set `WORKER_IP` for the first; run the worker steps once per worker IP. Keep this terminal open so the variables are set for the next steps.

---

## Step 3: Copy files to master

From the project directory (after setting the variables in Step 2):

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$MASTER_IP "mkdir -p ~/chatbot-performance-testing"
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env requirements.txt ec2-user@$MASTER_IP:~/chatbot-performance-testing/
```

---

## Step 4: Copy files to each worker

For **each** worker, run (replace `$WORKER_IP` with that worker’s IP if you have more than one):

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER_IP "mkdir -p ~/chatbot-performance-testing"
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env requirements.txt ec2-user@$WORKER_IP:~/chatbot-performance-testing/
```

---

## Step 5: Install dependencies

From the project directory:

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$MASTER_IP "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER_IP "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"
```

If you have multiple workers, run the second line for each worker (set `WORKER_IP` to that worker’s IP, or run with the IP in the command).

---

## Step 6: Start the master

From the project directory:

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$MASTER_IP
```

On the master:

```bash
cd ~/chatbot-performance-testing
TEST_TYPE=load locust -f src/locustfile.py --master
```

Leave this terminal open. In your browser open **http://$MASTER_IP:8089** (or paste the master public IP: e.g. http://3.87.139.5:8089).

---

## Step 7: Start the workers

From the project directory (in a **new** terminal, so `$WORKER_IP` and `$MASTER_PRIVATE` are still set from Step 2), for **each** worker run:

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER_IP "cd ~/chatbot-performance-testing && TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
```

Start every worker, then in the Locust web UI click **Start swarming**.

For other test types, change `TEST_TYPE` (e.g. `TEST_TYPE=stress`, `TEST_TYPE=endurance`, `TEST_TYPE=breakpoint`).

---

## Step 8: Download reports

Run metadata is on the **master**; response-time CSV is on the **workers**. From the project directory:

```bash
mkdir -p reports
scp -i ~/.ssh/locust-testing.pem "ec2-user@$MASTER_IP:~/chatbot-performance-testing/reports/run_meta_*.json" ./reports/
scp -i ~/.ssh/locust-testing.pem ec2-user@$WORKER_IP:~/chatbot-performance-testing/reports/response_times_load.csv ./reports/response_times_load.csv
python src/generate_report.py
```

If you have multiple workers, run the second `scp` for each worker (change the local filename if needed so you don’t overwrite). Use `--exclude-empty` to skip rows with no answer: `python src/generate_report.py --exclude-empty`

---

## Step 9: Cleanup

From the project directory:

```bash
aws cloudformation delete-stack --stack-name locust-cluster
```

---

## Quick reference

| Step            | What you do |
|-----------------|-------------|
| 1 Deploy        | `./aws_setup/deploy_locust.sh` → key name `locust-testing` |
| 2 IPs           | `./aws_setup/get_ips_simple.sh` → note master public, master private, worker IP(s) |
| 3–4 Copy        | `scp -i ~/.ssh/locust-testing.pem ...` to master and each worker |
| 5 Install       | `ssh -i ~/.ssh/locust-testing.pem ec2-user@<IP> "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"` for master and each worker |
| 6 Master        | SSH to master, then `TEST_TYPE=load locust -f src/locustfile.py --master` |
| 7 Workers       | `ssh -i ~/.ssh/locust-testing.pem ec2-user@<WORKER_IP> "cd ... && TEST_TYPE=load locust ... --worker --master-host=<MASTER_PRIVATE>"` for each worker |
| 8 Reports       | `scp` run_meta from master, response_times CSV from each worker, then `python src/generate_report.py` |
| 9 Cleanup       | `aws cloudformation delete-stack --stack-name locust-cluster` |

**Web UI:** http://&lt;master-public-ip&gt;:8089
