import json, os, uuid, time
import boto3

SQS_URL = os.environ["QUEUE_URL"]
DDB_TABLE = os.environ["JOBS_TABLE"]

sqs = boto3.client("sqs")
ddb = boto3.resource("dynamodb").Table(DDB_TABLE)

def _response(code, body): 
    return {"statusCode": code, "headers": {"Content-Type":"application/json"}, "body": json.dumps(body)}

def post_jobs(event, ctx):
    payload = json.loads(event["body"] or "{}")
    for k in ["repoRef","instruction"]:
        if k not in payload: 
            return _response(400, {"error": f"missing {k}"})
    job_id = str(uuid.uuid4())
    now = int(time.time())
    ddb.put_item(Item={
        "jobId": job_id, "status": "queued", "createdAt": now,
        "repoRef": payload["repoRef"], "callbackUrl": payload.get("callbackUrl"),
        "userId": payload.get("userId"), "instruction": payload["instruction"]
    })
    sqs.send_message(QueueUrl=SQS_URL, MessageGroupId="jobs", MessageDeduplicationId=job_id,
                     MessageBody=json.dumps({"jobId": job_id}))
    return _response(202, {"jobId": job_id})

def get_job(event, ctx):
    job_id = event["pathParameters"]["jobId"]
    res = ddb.get_item(Key={"jobId": job_id})
    if "Item" not in res: return _response(404, {"error":"not found"})
    item = res["Item"]
    return _response(200, {
        "jobId": job_id, "status": item["status"],
        "prUrl": item.get("prUrl"), "startedAt": item.get("startedAt"),
        "finishedAt": item.get("finishedAt"), "summary": item.get("summary")
    })

def cancel_job(event, ctx):
    job_id = event["pathParameters"]["jobId"]
    # Best-effort: statusをcancelled_requested等に更新し、Worker側でチェック
    ddb.update_item(
        Key={"jobId": job_id},
        UpdateExpression="SET #s = :v",
        ExpressionAttributeNames={"#s":"status"},
        ExpressionAttributeValues={":v":"cancelled"}
    )
    return _response(202, {"jobId": job_id, "status":"cancelled"})