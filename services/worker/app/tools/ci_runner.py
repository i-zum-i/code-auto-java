import os, subprocess
from .context_extract import detect_build_system

def _run(cmd, cwd=None, check=True):
    """実行ヘルパー"""
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\nstdout: {res.stdout}\nstderr: {res.stderr}")
    return res

def run_ci(repo_dir:str)->dict:
    """
    Maven/Gradle自動判別でbuild/test/lint実行
    """
    build_sys = detect_build_system(repo_dir)
    results = {"build_system": build_sys}
    
    if build_sys == "maven":
        # Maven
        try:
            # 権限付与
            _run("chmod +x ./mvnw", cwd=repo_dir, check=False)
            # clean compile test
            _run("./mvnw clean compile test -B --no-transfer-progress", cwd=repo_dir)
            results["build"] = "success"
            results["test"] = "success"
        except RuntimeError as e:
            results["build"] = "failed"
            results["error"] = str(e)
        
        # 静的解析（optional）
        try:
            _run("./mvnw checkstyle:check -B", cwd=repo_dir, check=False)
            results["lint"] = "success"
        except:
            results["lint"] = "skipped"
            
    elif build_sys == "gradle":
        # Gradle
        try:
            # 権限付与
            _run("chmod +x ./gradlew", cwd=repo_dir, check=False)
            # clean build test
            _run("./gradlew clean build test --no-daemon --console=plain", cwd=repo_dir)
            results["build"] = "success"
            results["test"] = "success"
        except RuntimeError as e:
            results["build"] = "failed"
            results["error"] = str(e)
        
        # Lint
        try:
            _run("./gradlew spotlessCheck --no-daemon", cwd=repo_dir, check=False)
            results["lint"] = "success"
        except:
            results["lint"] = "skipped"
    
    else:
        results["build"] = "skipped"
        results["test"] = "skipped"
        results["error"] = "No build system detected (Maven/Gradle)"
    
    return results