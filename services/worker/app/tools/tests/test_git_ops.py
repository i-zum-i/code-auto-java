import os
import tempfile
import subprocess
import types
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.git_ops import apply_patch, push_branch_and_open_pr


def _init_repo():
    repo = tempfile.mkdtemp(prefix="repo_")
    subprocess.check_call(["git", "init"], cwd=repo, stdout=subprocess.DEVNULL)
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=repo)
    subprocess.check_call(["git", "config", "user.name", "Tester"], cwd=repo)
    # create initial file
    with open(os.path.join(repo, "file.txt"), "w") as f:
        f.write("hello\n")
    subprocess.check_call(["git", "add", "file.txt"], cwd=repo)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=repo, stdout=subprocess.DEVNULL)
    # setup bare remote
    origin = tempfile.mkdtemp(prefix="origin_")
    subprocess.check_call(["git", "init", "--bare"], cwd=origin, stdout=subprocess.DEVNULL)
    subprocess.check_call(["git", "remote", "add", "origin", origin], cwd=repo)
    return repo, origin


def test_apply_patch_and_push_branch():
    repo, origin = _init_repo()

    # generate patch modifying file.txt
    with open(os.path.join(repo, "file.txt"), "w") as f:
        f.write("hello world\n")
    patch = subprocess.check_output(["git", "diff"], cwd=repo, text=True)
    subprocess.check_call(["git", "checkout", "--", "file.txt"], cwd=repo)

    apply_patch(repo, patch)
    with open(os.path.join(repo, "file.txt")) as f:
        assert "hello world" in f.read()

    ctx = types.SimpleNamespace(repo_dir=repo, branch="main", subdir=None, owner_repo="owner/repo")
    branch, pr_url = push_branch_and_open_pr(ctx, "job123456")
    assert branch.startswith("auto/")
    assert "owner/repo" in pr_url

    # ensure branch pushed to origin
    refs = subprocess.check_output(["git", "ls-remote", "--heads", origin], text=True)
    assert branch in refs
