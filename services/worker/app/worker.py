# Worker implementation placeholder
import os, json, time, subprocess, tempfile, shutil
import boto3
from tools.git_ops import with_checkout, push_branch_and_open_pr
from tools.context_extract import build_min_context
from tools.ci_runner import run_ci
from tools.claude_client import plan_and_apply

REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
SQS_URL = os.environ["QUEUE_URL"]
DDB_TABLE = os.environ["JOBS_TABLE"]
ARTIFACTS_BUCKET = os.environ["ARTIFACTS_BUCKET"]
GIT_APP_ISSUER_ARN = os.environ["GIT_APP_ISSUER_ARN"]   # GitHub Appなどの短命トークン発行用
CLAUDE_API_KEY_SECRET_ARN = os.environ["CLAUDE_API_KEY_SECRET_ARN"]

sqs = boto3.client("sqs", region_name=REGION)
ddb = boto3.resource("dynamodb", region_name=REGION).Table(DDB_TABLE)
sm  = boto3.client("secretsmanager", region_name=REGION)

def poll():
    msgs = sqs.receive_message(QueueUrl=SQS_URL, MaxNumberOfMessages=1, WaitTimeSeconds=20, VisibilityTimeout=120)
    return msgs.get("Messages", [])

def update_status(jobId, **kv):
    expr = "SET " + ", ".join([f"#{k}=:{k}" for k in kv.keys()])
    ddb.update_item(
        Key={"jobId": jobId},
        UpdateExpression=expr,
        ExpressionAttributeNames={f"#{k}":k for k in kv.keys()},
        ExpressionAttributeValues={f":{k}":v for k,v in kv.items()}
    )

def main():
    while True:
        for m in poll():
            receipt = m["ReceiptHandle"]
            body = json.loads(m["Body"])
            jobId = body["jobId"]
            try:
                item = ddb.get_item(Key={"jobId": jobId})["Item"]
                repoRef = item["repoRef"]; instruction = item["instruction"]
                cb = item.get("callbackUrl")
                update_status(jobId, status="running", startedAt=int(time.time()))

                # Secrets
                claude_key = sm.get_secret_value(SecretId=CLAUDE_API_KEY_SECRET_ARN)["SecretString"]

                with with_checkout(repoRef) as ctx:
                    target_files = build_min_context(ctx)
                    plan, patch = plan_and_apply(
                        repo_dir=ctx.repo_dir,
                        instruction=instruction,
                        target_files=target_files,
                        claude_api_key=claude_key
                    )
                    stage = run_ci(ctx.repo_dir)   # build/test/lint

                    branch, pr_url = push_branch_and_open_pr(ctx, jobId, patch)

                update_status(jobId, status="pr-open", prUrl=pr_url, summary=plan)
                # 後段でCIが通れば succeeded（別ルートでアップデート）

            except Exception as e:
                update_status(jobId, status="failed", finishedAt=int(time.time()), summary=str(e))
            finally:
                sqs.delete_message(QueueUrl=SQS_URL, ReceiptHandle=receipt)

if __name__ == "__main__":
    main()
