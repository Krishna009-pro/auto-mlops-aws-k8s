"""
Synthetic Transaction Fraud Dataset Generator for MLOps Pipeline.
Generates initial dataset (v1) and retraining dataset with drift (v2).
"""

import os
import argparse
import numpy as np
import pandas as pd


def generate_fraud_data(
    num_samples: int = 5000,
    fraud_rate: float = 0.08,
    drift_factor: float = 0.0,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic credit card transaction records.
    drift_factor simulates concept drift in retraining batches.
    """
    np.random.seed(random_seed)

    # 1. Transaction Amount (log-normal distribution)
    # Fraud transactions generally skew higher
    amounts = np.random.lognormal(mean=3.5, sigma=1.0, size=num_samples)

    # 2. Daily Transaction Frequency
    frequencies = np.random.poisson(lam=4.0 + drift_factor * 1.5, size=num_samples)

    # 3. Location Risk Score (0.0 to 1.0)
    location_risks = np.random.beta(a=2.0 + drift_factor, b=5.0, size=num_samples)

    # 4. Device Trust Score (0.0 to 1.0)
    device_trust = np.random.beta(a=6.0, b=2.0 + drift_factor, size=num_samples)

    # 5. Time of Day (0 to 23 hours)
    time_of_day = np.random.randint(0, 24, size=num_samples)

    # 6. Failed Authentication Attempts (0 to 5)
    failed_attempts = np.random.binomial(n=5, p=0.08 + drift_factor * 0.05, size=num_samples)

    # Calculate synthetic fraud probability score
    logit = (
        0.003 * amounts
        + 0.15 * frequencies
        + 2.8 * location_risks
        - 3.2 * device_trust
        + 0.6 * failed_attempts
        + (0.3 if drift_factor > 0 else 0.0)
        - 1.8
    )
    prob_fraud = 1.0 / (1.0 + np.exp(-logit))

    # Assign fraud labels (0 or 1) based on calculated probabilities and target fraud rate
    cutoff = np.percentile(prob_fraud, 100 * (1.0 - fraud_rate))
    is_fraud = (prob_fraud >= cutoff).astype(int)

    df = pd.DataFrame(
        {
            "transaction_amount": np.round(amounts, 2),
            "transaction_frequency": frequencies,
            "location_risk_score": np.round(location_risks, 4),
            "device_trust_score": np.round(device_trust, 4),
            "time_of_day": time_of_day,
            "failed_attempts": failed_attempts,
            "is_fraud": is_fraud,
        }
    )

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic transaction fraud data for MLOps")
    parser.add_argument("--version", choices=["v1", "v2"], default="v1", help="Dataset version (v1=initial, v2=retraining with drift)")
    parser.add_argument("--samples", type=int, default=5000, help="Number of records to generate")
    parser.add_argument("--output-dir", type=str, default="data/raw", help="Output directory for generated CSVs")
    parser.add_argument("--s3-bucket", type=str, default=None, help="Optional S3 bucket name to upload directly")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    filename = f"transactions_{args.version}.csv"
    output_path = os.path.join(args.output_dir, filename)

    if args.version == "v1":
        print("[DATA-GEN] Generating initial dataset (v1)...")
        df = generate_fraud_data(num_samples=args.samples, fraud_rate=0.08, drift_factor=0.0, random_seed=42)
    else:
        print("[DATA-GEN] Generating retraining dataset (v2) with distribution drift...")
        df = generate_fraud_data(num_samples=args.samples, fraud_rate=0.10, drift_factor=0.4, random_seed=99)

    df.to_csv(output_path, index=False)
    print(f"[DATA-GEN] Saved {len(df)} records to {output_path}")
    print(f"[DATA-GEN] Class distribution:\n{df['is_fraud'].value_counts(normalize=True)}")

    if args.s3_bucket:
        try:
            import boto3
            s3 = boto3.client("s3")
            s3_key = f"incoming/{filename}"
            print(f"[DATA-GEN] Uploading to s3://{args.s3_bucket}/{s3_key}...")
            s3.upload_file(output_path, args.s3_bucket, s3_key)
            print("[DATA-GEN] S3 upload successful!")
        except Exception as e:
            print(f"[DATA-GEN] S3 upload failed: {e}")


if __name__ == "__main__":
    main()
