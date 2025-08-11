import os, glob, json

JAVA_EXTS = (".java",".kt",".kts",".xml",".properties",".gradle",".md")

def build_min_context(ctx)->dict:
    """
    Java初期対応：
    - ルート/サブディレクトリに pom.xml or build.gradle[.kts] があれば、その周辺（src/**）を対象に
    - 付随設定ファイル（application*.yml/properties, .editorconfig, checkstyle等）も候補
    - 将来: 言語検出で拡張
    """
    root = ctx.repo_dir if not ctx.subdir else os.path.join(ctx.repo_dir, ctx.subdir)
    files = []

    def add_if_exists(patterns):
        for p in patterns:
            files.extend(glob.glob(os.path.join(root, p), recursive=True))

    # build files
    add_if_exists(["pom.xml","build.gradle","build.gradle.kts"])
    # main/test sources
    add_if_exists(["src/**/*.java","src/**/*.kt"])
    # config files
    add_if_exists(["src/**/application*.yml","src/**/application*.yaml","src/**/application*.properties"])
    # docs
    add_if_exists(["README.md","CHANGELOG.md","*.md"])

    # filter + relative path
    rel_files = []
    for f in files:
        if os.path.isfile(f) and any(f.endswith(ext) for ext in JAVA_EXTS):
            rel_path = os.path.relpath(f, ctx.repo_dir)
            rel_files.append(rel_path)

    return {
        "project_root": root,
        "target_files": rel_files[:50],  # 最大50ファイル制限
        "build_system": detect_build_system(root)
    }

def detect_build_system(root:str)->str:
    if os.path.exists(os.path.join(root, "pom.xml")):
        return "maven"
    elif any(os.path.exists(os.path.join(root, f)) for f in ["build.gradle","build.gradle.kts"]):
        return "gradle"
    return "unknown"