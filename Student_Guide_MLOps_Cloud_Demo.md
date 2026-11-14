# Student Guide: Cloud-Native MLOps Platform (12-Step Lab Manual)

**Course:** 24AIH5P01: Cloud Infrastructure and Virtualization for AI Lab  
**Institution:** Indira College of Engineering and Management (ICEM), Pune | SPPU  
**Project:** SentinelOps — Cloud-Native MLOps Fraud Detection & Continuous Training Platform  
**Target AWS Region:** Asia Pacific (Mumbai) `ap-south-1`  
**Docker Hub Username:** `krishna250`  

---

## 🧭 The 12-Step Lab Journey

```
[Laptop: Step 1-4]                    [Cloud Registry: Step 5]
  Code & Test App                      Push Docker Images
  (Git, Python, Docker) ────────────►  (krishna250 on Docker Hub)
                                             │
                                             ▼
[AWS Infrastructure: Step 6-8]        [Kubernetes on EC2: Step 8]
  S3 Bucket + IAM Role  ────────────►  K3s Cluster pulls image &
                                       runs web app on port 30080
                                             │
                                             ▼ (Uploads dataset/model)
[AWS Serverless: Step 9-10]           [Amazon S3 Bucket]
  SNS Email Topic & S3 Trigger        (icem-mlops-krishna250)
  Lambda Function ◄──────────────────────────┘
         │
         ▼ (Sends Email Alert)
  [Your Email Inbox] (Step 11: Full Run)
```

---

## Step 1: Accounts, Cost Safety and Laptop Tools
1. **AWS Account:** Sign in to AWS Console with region **Asia Pacific (Mumbai) `ap-south-1`**.
2. **Docker Hub:** Log in with `docker login -u krishna250`.
3. **Laptop Tools:** Git, Python 3.11, Docker Desktop, and kubectl are installed.

---

## Step 2: Git and GitHub
1. Code committed and pushed to your GitHub repository:
   ```bash
   git status
   # Working tree clean, synced with origin/main
   ```

---

## Step 3: Run the App on the Laptop
1. Run locally:
   ```powershell
   python -m uvicorn src.serve.app:app --host 127.0.0.1 --port 8000 --reload
   ```
2. Open **`http://127.0.0.1:8000/`** in browser to verify the interactive fraud detection dashboard.

---

## Step 4: Docker — Build the Containers
Both containers have been built locally:
- `krishna250/mlops-serving:latest` (Web UI & Inference API)
- `krishna250/mlops-trainer:latest` (Model Retraining Job)

---

## Step 5: Push the Images to Docker Hub
Push both images to your Docker Hub account:
```powershell
docker push krishna250/mlops-trainer:latest
docker push krishna250/mlops-serving:latest
```

---

## Step 6: S3 Bucket & IAM Role for the Server
### 6.1 Create the S3 Bucket
1. Go to **AWS Console** $\rightarrow$ Search **S3** $\rightarrow$ **Create bucket**.
2. **Bucket Name:** `icem-mlops-krishna250` (must be unique).
3. **Region:** `Asia Pacific (Mumbai) ap-south-1`.
4. **Block Public Access:** Keep all boxes checked (Enable block public access).
5. Click **Create bucket**.
6. Inside the bucket, create three folders:
   - `datasets/`
   - `models/`
   - `metrics/`

### 6.2 Create the IAM Role for EC2
1. Search **IAM** $\rightarrow$ **Roles** $\rightarrow$ **Create role**.
2. **Trusted entity:** `AWS service` $\rightarrow$ Use case: `EC2` $\rightarrow$ Next.
3. Click **Create policy** $\rightarrow$ **JSON** tab $\rightarrow$ Paste:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::icem-mlops-krishna250",
           "arn:aws:s3:::icem-mlops-krishna250/*"
         ]
       }
     ]
   }
   ```
4. Name the policy: `MLOpsEC2S3Policy` $\rightarrow$ **Create policy**.
5. Back in Role creation, select `MLOpsEC2S3Policy`.
6. Name the role: **`MLOpsEC2Role`** $\rightarrow$ Click **Create role**.

---

## Step 7: Launch the EC2 Server
1. Go to **EC2** $\rightarrow$ **Launch instance**.
2. **Name:** `mlops-k3s-server`.
3. **OS Image:** `Ubuntu Server 24.04 LTS` (64-bit x86).
4. **Instance type:** `t3.small` (recommended for K3s) or `t3.micro`.
5. **Key pair:** Create a new key pair named `mlops-key` (type: RSA, `.pem`). Save `mlops-key.pem` to your laptop.
6. **Network / Security Group:** Create security group with inbound rules:
   | Type | Port | Source | Purpose |
   | :--- | :--- | :--- | :--- |
   | SSH | 22 | My IP | Secure login |
   | Custom TCP | 30080 | Anywhere (0.0.0.0/0) | Kubernetes NodePort Web UI |
   | Custom TCP | 8000 | Anywhere (0.0.0.0/0) | Direct API access |
7. **Advanced Details (IAM Instance Profile):**
   - Select **`MLOpsEC2Role`** from the dropdown!
8. Click **Launch instance**.
9. Note down the **Public IPv4 address** (e.g. `13.233.xxx.xxx`).

---

## Step 8: Install K3s and Deploy the App
1. **Connect via SSH** from your laptop (Git Bash or PowerShell):
   ```bash
   ssh -i mlops-key.pem ubuntu@<EC2-PUBLIC-IP>
   ```

2. **Install K3s (Lightweight Kubernetes)** on EC2 with 1 command:
   ```bash
   curl -sfL https://get.k3s.io | sh -
   ```

3. **Verify K3s is Running:**
   ```bash
   sudo kubectl get nodes
   # STATUS should be 'Ready'
   ```

4. **Deploy the MLOps Serving App:**
   On the EC2 server, create `k8s-app.yaml`:
   ```bash
   cat << 'EOF' > k8s-app.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mlops-serving-api
     labels:
       app: fraud-detector
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: fraud-detector
     template:
       metadata:
         labels:
           app: fraud-detector
       spec:
         containers:
           - name: inference-api
             image: krishna250/mlops-serving:latest
             imagePullPolicy: Always
             ports:
               - containerPort: 8000
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mlops-serving-service
   spec:
     type: NodePort
     ports:
       - port: 8000
         targetPort: 8000
         nodePort: 30080
     selector:
       app: fraud-detector
   EOF
   ```

5. **Apply Manifest:**
   ```bash
   sudo kubectl apply -f k8s-app.yaml
   ```

6. **Check Pod Status:**
   ```bash
   sudo kubectl get pods -o wide
   # Wait until STATUS becomes 'Running'
   ```

7. **Open in Your Browser:**
   Visit: **`http://<EC2-PUBLIC-IP>:30080/`**
   *(Your full-stack MLOps Fraud Detection dashboard is now running live on Kubernetes in the cloud!)*

---

## Step 9: SNS Email Topic
1. Go to **AWS Console** $\rightarrow$ Search **SNS** $\rightarrow$ **Topics** $\rightarrow$ **Create topic**.
2. **Type:** `Standard`.
3. **Name:** `mlops-alerts`.
4. Click **Create topic**.
5. Note the **Topic ARN** (e.g. `arn:aws:sns:ap-south-1:123456789012:mlops-alerts`).
6. Click **Create subscription**:
   - **Protocol:** `Email`
   - **Endpoint:** `your-email@gmail.com`
7. Check your email inbox $\rightarrow$ Open the confirmation email from AWS $\rightarrow$ Click **"Confirm subscription"**!

---

## Step 10: Lambda Function and S3 Trigger
### 10.1 Create Lambda Function
1. Go to **AWS Console** $\rightarrow$ Search **Lambda** $\rightarrow$ **Create function**.
2. **Function Name:** `MLOpsProcessor`.
3. **Runtime:** `Python 3.11`.
4. **Architecture:** `x86_64`.
5. Under **Change default execution role**, choose **Create a new role with basic Lambda permissions**.
6. Click **Create function**.

### 10.2 Add Permissions to Lambda Role
1. In the Lambda function page, click **Configuration** $\rightarrow$ **Permissions** $\rightarrow$ Click the **Role name** link.
2. Under **Permissions policies**, click **Add permissions** $\rightarrow$ **Attach policies**:
   - Attach: `AmazonS3FullAccess`
   - Attach: `AmazonSNSFullAccess`

### 10.3 Paste Lambda Code
1. In Lambda $\rightarrow$ **Code** tab $\rightarrow$ double-click `lambda_function.py`.
2. Replace all content with:
   ```python
   import json
   import urllib.parse
   import boto3
   import os

   s3 = boto3.client('s3')
   sns = boto3.client('sns')

   SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', '')

   def lambda_handler(event, context):
       for record in event.get('Records', []):
           bucket = record['s3']['bucket']['name']
           key = urllib.parse.unquote_plus(record['s3']['object']['key'])
           size = record['s3']['object'].get('size', 0)
           
           print(f"New file uploaded: s3://{bucket}/{key} ({size} bytes)")
           
           subject = f"[MLOps Cloud Alert] New File Processed: {key}"
           message = (
               f"=== SentinelOps Cloud Notification ===\n\n"
               f"Bucket: {bucket}\n"
               f"File Key: {key}\n"
               f"Size: {size} bytes\n"
               f"Status: VALIDATED & INGESTED\n\n"
               f"Action: Kubernetes continuous retraining job dispatched."
           )
           
           if SNS_TOPIC_ARN:
               sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject[:100], Message=message)
               print(f"Sent email alert to SNS Topic: {SNS_TOPIC_ARN}")
               
       return {"status": "success"}
   ```
3. Click **Deploy**.

### 10.4 Configure Environment Variable & S3 Trigger
1. **Environment Variables:**
   - Go to **Configuration** $\rightarrow$ **Environment variables** $\rightarrow$ **Edit**.
   - Key: `SNS_TOPIC_ARN` | Value: `arn:aws:sns:ap-south-1:XXXXXX:mlops-alerts`.
   - Save.
2. **Add S3 Trigger:**
   - Click **Add trigger** $\rightarrow$ Select **S3**.
   - **Bucket:** `icem-mlops-krishna250`.
   - **Event types:** `All object create events` (`s3:ObjectCreated:*`).
   - Click **Add**.

---

## Step 11: Full Run (End-to-End Demo)
1. Open your browser: **`http://<EC2-PUBLIC-IP>:30080/`**.
2. Test a transaction:
   - Click `🛒 Normal Grocery ($35)` $\rightarrow$ **Score Transaction** $\rightarrow$ Result: **APPROVED**.
   - Click `🚨 3 AM Wire Transfer ($2,890)` $\rightarrow$ **Score Transaction** $\rightarrow$ Result: **FRAUD DETECTED**.
3. Trigger Retraining / Upload:
   - Click **"Simulate S3 Upload & Automated Retraining"**.
   - A new file is uploaded to `s3://icem-mlops-krishna250/datasets/`.
4. **Check Your Email:**
   - Within seconds, you will receive an automated email from **AWS SNS**:
     > `[MLOps Cloud Alert] New File Processed: datasets/transactions_v2.csv`
5. **Check CloudWatch Logs:**
   - Go to **Lambda** $\rightarrow$ **Monitor** $\rightarrow$ **View CloudWatch logs** to see your print statements.

---

## Step 12: Clean Up So Nothing is Billed
When finished or after your practical submission:
1. **Stop or Terminate EC2:** Go to **EC2** $\rightarrow$ Select `mlops-k3s-server` $\rightarrow$ **Instance state** $\rightarrow$ **Stop** (or Terminate).
2. **Empty S3 Bucket:** Go to **S3** $\rightarrow$ Select `icem-mlops-krishna250` $\rightarrow$ Click **Empty** $\rightarrow$ Click **Delete**.
3. **Delete Lambda:** Delete function `MLOpsProcessor`.
4. **Delete SNS Topic:** Delete `mlops-alerts`.
