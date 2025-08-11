import os, json
import anthropic

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
CLAUDE_MAX_TOKENS = int(os.environ.get("CLAUDE_MAX_TOKENS", "8192"))

def plan_and_apply(repo_dir:str, instruction:str, target_files:dict, claude_api_key:str):
    """
    Claude Code SDK経由で実装プランと差分パッチを生成
    """
    client = anthropic.Anthropic(api_key=claude_api_key)
    
    # プロンプトテンプレート読み込み
    template_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "implement.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # ファイル内容を収集
    file_contents = {}
    for file_path in target_files.get("target_files", []):
        full_path = os.path.join(repo_dir, file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    file_contents[file_path] = f.read()
            except:
                file_contents[file_path] = "[Binary or unreadable file]"
    
    # プロンプト構築
    context_section = "\n\n".join([
        f"### {path}\n```\n{content}\n```" 
        for path, content in file_contents.items()
    ])
    
    scope = ", ".join(target_files.get("target_files", []))
    
    prompt = template.replace("{{INSTRUCTION}}", instruction)
    prompt = prompt.replace("{{TARGET_SCOPE}}", scope)
    prompt += f"\n\n## Current Codebase Context\n{context_section}"
    prompt += f"\n\n## Build System\n{target_files.get('build_system', 'unknown')}"
    
    # Claude API呼び出し
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            temperature=0.1,
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        response = message.content[0].text if message.content else ""
        
        # レスポンス解析（プランと差分の抽出）
        plan = extract_plan(response)
        patch = extract_diff_patch(response)
        
        return plan, patch
        
    except Exception as e:
        raise RuntimeError(f"Claude API error: {e}")

def extract_plan(response:str)->str:
    """レスポンスからプラン部分を抽出"""
    lines = response.split('\n')
    plan_lines = []
    in_plan = False
    
    for line in lines:
        if 'plan' in line.lower() or 'step' in line.lower():
            in_plan = True
        elif line.startswith('```') or line.startswith('diff'):
            break
        elif in_plan:
            plan_lines.append(line)
    
    return '\n'.join(plan_lines[:20])  # 最大20行

def extract_diff_patch(response:str)->str:
    """レスポンスから diff パッチを抽出"""
    # ```diff または diff --git から始まるセクションを探す
    lines = response.split('\n')
    patch_lines = []
    in_diff = False
    
    for line in lines:
        if line.startswith('```diff') or line.startswith('diff --git'):
            in_diff = True
            if line.startswith('```diff'):
                continue  # マークダウン記号はスキップ
        elif line.startswith('```') and in_diff:
            break
        elif in_diff:
            patch_lines.append(line)
    
    patch = '\n'.join(patch_lines)
    if not patch.strip():
        # フォールバック: 単純なファイル置換として処理
        return "# No unified diff found - manual implementation required"
    
    return patch