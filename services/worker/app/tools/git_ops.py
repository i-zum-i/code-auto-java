# git_ops implementation placeholder
import os, subprocess, tempfile, shutil, contextlib

@contextlib.contextmanager
def with_checkout(repoRef:str):
    # repoRef: github:owner/repo#branch:subdir
    assert repoRef.startswith("github:")
    _, ref = repoRef.split(":",1)
    owner_repo, *rest = ref.split("#")
    branch_sub = rest[0] if rest else "main"
    branch, *path_part = branch_sub.split(":")
    subdir = path_part[0] if path_part else None

    tmp = tempfile.mkdtemp(prefix="jobrepo_")
    try:
        url = f"https://github.com/{owner_repo}.git"
        subprocess.check_call(["git","init"], cwd=tmp)
        subprocess.check_call(["git","remote","add","origin",url], cwd=tmp)
        subprocess.check_call(["git","fetch","--depth","1","origin",branch], cwd=tmp)
        subprocess.check_call(["git","checkout","-B",branch,f"origin/{branch}"], cwd=tmp)
        yield type("Ctx",(object,),{"repo_dir": tmp, "branch": branch, "subdir": subdir, "owner_repo": owner_repo})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def apply_patch(repo_dir: str, patch_text: str):
    """Apply a unified diff patch to the repository working tree."""
    p = subprocess.Popen([
        "git",
        "apply",
        "-"
    ], cwd=repo_dir, stdin=subprocess.PIPE, text=True)
    p.communicate(patch_text)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, "git apply")


def push_branch_and_open_pr(ctx, jobId):
    branch_name = f"auto/{jobId[:8]}"
    subprocess.check_call(["git", "checkout", "-b", branch_name], cwd=ctx.repo_dir)
    subprocess.check_call(["git", "add", "-A"], cwd=ctx.repo_dir)
    subprocess.check_call([
        "git",
        "commit",
        "-m",
        f"feat: auto changes for job {jobId}"
    ], cwd=ctx.repo_dir)

    # push (PATではなくGitHub Appの短命トークンに置換)
    subprocess.check_call(["git", "push", "origin", branch_name], cwd=ctx.repo_dir)

    # PR作成は gh CLI または GitHub API で（疑似）
    pr_url = f"https://github.com/{ctx.owner_repo}/pull/new/{branch_name}"
    return branch_name, pr_url
