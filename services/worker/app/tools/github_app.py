import os, time, jwt, requests

GITHUB_API = os.environ.get("GITHUB_API", "https://api.github.com")

APP_ID = os.environ["GITHUB_APP_ID"]
# Secrets Managerで保管し、起動時に環境変数へ注入してもOK。長期保持は厳禁
APP_PRIVATE_KEY_PEM = os.environ["GITHUB_APP_PRIVATE_KEY_PEM"]

def _jwt_for_app():
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 9*60, "iss": APP_ID}
    return jwt.encode(payload, APP_PRIVATE_KEY_PEM, algorithm="RS256")

def installation_token(owner_repo:str)->str:
    """
    owner_repo: "owner/repo"
    1) App JWTでインストールIDを取得
    2) インストールトークンを発行（5〜60分寿命）
    """
    app_jwt = _jwt_for_app()
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"})
    # どのインストールかをowner/repoで解決
    owner, repo = owner_repo.split("/", 1)
    r = s.get(f"{GITHUB_API}/repos/{owner}/{repo}/installation")
    r.raise_for_status()
    inst_id = r.json()["id"]
    r2 = s.post(f"{GITHUB_API}/app/installations/{inst_id}/access_tokens")
    r2.raise_for_status()
    return r2.json()["token"]