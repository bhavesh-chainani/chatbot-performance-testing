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

**Multiple workers:** When you have more than one worker, every “worker” step (copy files, install deps, start worker, download reports) is run **once per worker**, using that worker’s IP. Master steps are always done once.

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

Cookie lasts ~24 hours; refresh if you get 401s. If the cookie expires or `.env` fails during a run, see [Update .env only](#update-env-only-when-session-expires-or-env-fails) below.

---

## Update .env only (when session expires or .env fails)

When you update `.env` locally (e.g. new session cookie) and need to push it to the cluster **without** re-copying `src/`, `config/`, or reinstalling dependencies:

1. **Get IPs** (if needed): `./aws_setup/get_ips_simple.sh` and set `MASTER_IP`, `MASTER_PRIVATE`, and each worker IP (e.g. `WORKER1_IP`, `WORKER2_IP`, …).

2. **Upload .env to master:**
   ```bash
   scp -i ~/.ssh/locust-testing.pem .env ec2-user@$MASTER_IP:~/chatbot-performance-testing/
   ```

3. **Upload .env to each worker** (run once per worker IP):
   ```bash
   scp -i ~/.ssh/locust-testing.pem .env ec2-user@$WORKER1_IP:~/chatbot-performance-testing/
   scp -i ~/.ssh/locust-testing.pem .env ec2-user@$WORKER2_IP:~/chatbot-performance-testing/
   # ... repeat for each worker
   ```

4. **Restart Locust** so the new `.env` is loaded:
   - On the master: stop the running Locust (Ctrl+C), then start again: `TEST_TYPE=load locust -f src/locustfile.py --master`.
   - On each worker: stop the worker process (Ctrl+C or kill), then start again (run once per worker):
     ```bash
     ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER1_IP "cd ~/chatbot-performance-testing && TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
     ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER2_IP "cd ~/chatbot-performance-testing && TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
     # ... repeat for each worker
     ```

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

From the output: note **Master Public IP**, **Master Private IP**, and under **“Worker instances only”** each worker’s name and IP (one line per worker). Set variables (replace with your values):

**One master + one worker:**
```bash
export MASTER_IP=3.87.139.5
export MASTER_PRIVATE=172.31.40.17
export WORKER_IP=3.88.136.146
```

**One master + multiple workers (e.g. 3):** set a variable per worker so you can repeat the worker steps for each:
```bash
export MASTER_IP=3.80.105.151
export MASTER_PRIVATE=172.31.27.162
export WORKER1_IP=<first-worker-ip>
export WORKER2_IP=<second-worker-ip>
export WORKER3_IP=<third-worker-ip>
```

Keep this terminal open so the variables are set for the next steps.

---

## Step 3: Copy files to master

From the project directory (after setting the variables in Step 2):

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$MASTER_IP "mkdir -p ~/chatbot-performance-testing"
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env requirements.txt ec2-user@$MASTER_IP:~/chatbot-performance-testing/
```

---

## Step 4: Copy files to each worker

Run the following **once per worker** (use that worker’s IP). Example for three workers:

```bash
# Worker 1
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER1_IP "mkdir -p ~/chatbot-performance-testing"
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env requirements.txt ec2-user@$WORKER1_IP:~/chatbot-performance-testing/

# Worker 2
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER2_IP "mkdir -p ~/chatbot-performance-testing"
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env requirements.txt ec2-user@$WORKER2_IP:~/chatbot-performance-testing/

# Worker 3
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER3_IP "mkdir -p ~/chatbot-performance-testing"
scp -i ~/.ssh/locust-testing.pem -r src/ config/ .env requirements.txt ec2-user@$WORKER3_IP:~/chatbot-performance-testing/
```

If you have only one worker, use `$WORKER_IP` and run the pair of commands once.

---

## Step 5: Install dependencies

From the project directory, install on the master once, then on **each** worker (once per worker). Example for three workers:

```bash
# Master (once)
ssh -i ~/.ssh/locust-testing.pem ec2-user@$MASTER_IP "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"

# Each worker (once per worker)
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER1_IP "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER2_IP "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER3_IP "cd ~/chatbot-performance-testing && pip3 install -r requirements.txt"
```

If you have only one worker, run the master line and one worker line with `$WORKER_IP`.

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

From the project directory, in a **new** terminal (so `$MASTER_PRIVATE` and worker IPs are still set from Step 2). Run **one** of these for **each** worker—each worker can run in its own terminal, or you can run them in the background. Use the **master private IP** (`$MASTER_PRIVATE`) so workers talk to the master inside the VPC.

Example for three workers:

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER1_IP "cd ~/chatbot-performance-testing && TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
```

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER2_IP "cd ~/chatbot-performance-testing && TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
```

```bash
ssh -i ~/.ssh/locust-testing.pem ec2-user@$WORKER3_IP "cd ~/chatbot-performance-testing && TEST_TYPE=load locust -f src/locustfile.py --worker --master-host=$MASTER_PRIVATE"
```

Start every worker, then in the Locust web UI click **Start swarming**.

For other test types, change `TEST_TYPE` (e.g. `TEST_TYPE=stress`, `TEST_TYPE=endurance`, `TEST_TYPE=breakpoint`).

---

## Step 8: Download reports

Run metadata is on the **master** (one `scp`). Response-time CSV is on **each worker**—download from every worker and use different local filenames so you don’t overwrite. From the project directory:

**One worker:**
```bash
mkdir -p reports
scp -i ~/.ssh/locust-testing.pem "ec2-user@$MASTER_IP:~/chatbot-performance-testing/reports/run_meta_*.json" ./reports/
scp -i ~/.ssh/locust-testing.pem ec2-user@$WORKER_IP:~/chatbot-performance-testing/reports/response_times_load.csv ./reports/response_times_load.csv
python src/generate_report.py --exclude-empty
```

**Multiple workers (e.g. 3):** run one `scp` per worker with a distinct local filename:
```bash
mkdir -p reports
scp -i ~/.ssh/locust-testing.pem "ec2-user@$MASTER_IP:~/chatbot-performance-testing/reports/run_meta_*.json" ./reports/
scp -i ~/.ssh/locust-testing.pem ec2-user@$WORKER1_IP:~/chatbot-performance-testing/reports/response_times_load.csv ./reports/response_times_load_worker1.csv
scp -i ~/.ssh/locust-testing.pem ec2-user@$WORKER2_IP:~/chatbot-performance-testing/reports/response_times_load.csv ./reports/response_times_load_worker2.csv
scp -i ~/.ssh/locust-testing.pem ec2-user@$WORKER3_IP:~/chatbot-performance-testing/reports/response_times_load.csv ./reports/response_times_load_worker3.csv
python src/generate_report.py --exclude-empty
```

If your report generator expects a single combined CSV, concatenate the worker CSVs first or point it at the files you need.

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
| **Update .env only** | `scp` .env to master and to **each** worker IP; then restart master and every worker. |
| 1 Deploy        | `./aws_setup/deploy_locust.sh` → key name `locust-testing` |
| 2 IPs           | `./aws_setup/get_ips_simple.sh` → set `MASTER_IP`, `MASTER_PRIVATE`, and one variable per worker (e.g. `WORKER1_IP`, `WORKER2_IP`, …) |
| 3 Copy (master) | One `scp` to master only |
| 4 Copy (workers)| One `scp` **per worker** to that worker’s IP |
| 5 Install       | One `pip3 install` on master; one **per worker** on each worker IP |
| 6 Master        | SSH to master, then `TEST_TYPE=load locust -f src/locustfile.py --master` |
| 7 Workers       | Run `locust ... --worker --master-host=$MASTER_PRIVATE` **once per worker** (each worker’s IP) |
| 8 Reports       | `scp` run_meta from master; `scp` response_times CSV from **each** worker (use different local filenames); then `python src/generate_report.py --exclude-empty` |
| 9 Cleanup       | `aws cloudformation delete-stack --stack-name locust-cluster` |

**Web UI:** http://&lt;master-public-ip&gt;:8089
