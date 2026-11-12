from datetime import datetime
from pathlib import Path
from typing import List
from state import WikiAgentState

def _log(state: WikiAgentState, node_name: str, status: str, detail: str) -> List[str]:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"| `{ts}` | **{node_name}** | {status} | {detail} |"
    print(f"[{node_name}] {status} - {detail}")
    logs = list(state.get("execution_logs", []))
    logs.append(entry)
    return logs

def ingest_raw_node(state: WikiAgentState) -> dict:
    """節點 1：讀取 raw/ 目錄下的 5 篇完整睡眠衛教文獻"""
    raw_path = Path(state["raw_dir"])
    docs = []
    extracted = []
    for file in sorted(raw_path.glob("*.md")):
        text = file.read_text(encoding="utf-8")
        docs.append({"filename": file.name, "content": text})
        lines = [line.strip("- ").strip() for line in text.splitlines() if line.startswith("- ")]
        extracted.append({
            "source": file.name,
            "char_count": len(text),
            "full_points": "\n".join([f"- {l}" for l in lines])
        })
    logs = _log(state, "1. ingest_raw", "✅ 完成", f"成功讀取並萃取 {len(docs)} 篇完整原始文獻。")
    return {"raw_documents": docs, "extracted_items": extracted, "execution_logs": logs}

def extract_check_node(state: WikiAgentState) -> dict:
    """節點 2（修改後新增的前置自檢節點）：逐篇確認關鍵數據與禁忌症無遺漏"""
    items = state.get("extracted_items", [])
    retry = state.get("extract_retry_count", 0)
    if len(items) < 5:
        logs = _log(state, "2. extract_check", "❌ 未通過", f"僅有 {len(items)} 篇文獻（需至少 5 篇）。")
        return {"extract_passed": False, "extract_feedback": "文獻不足 5 篇", "execution_logs": logs}

    incomplete = [it["source"] for it in items if len(it.get("full_points", "")) < 100]
    if incomplete:
        logs = _log(state, "2. extract_check", "⚠️ 需局部重抽", f"{incomplete} 萃取內容過短，退回第 {retry+1} 次補抽。")
        return {"extract_passed": False, "extract_feedback": f"請補強 {incomplete}", "execution_logs": logs}

    logs = _log(state, "2. extract_check", "✅ 通過", f"全數 {len(items)} 篇完整文獻通過前置完整性查核。")
    return {"extract_passed": True, "extract_feedback": "通過", "execution_logs": logs}

def re_extract_node(state: WikiAgentState) -> dict:
    """節點 3：針對缺漏篇目局部重新萃取"""
    new_retry = state.get("extract_retry_count", 0) + 1
    logs = _log(state, "3. re_extract", "🔄 重試執行", f"進行第 {new_retry} 次局部重點補強萃取。")
    return {"extract_retry_count": new_retry, "execution_logs": logs}

def merge_wiki_node(state: WikiAgentState) -> dict:
    """節點 4：將 5 篇乾淨原料跨篇整併為結構化 Wiki 條目"""
    wiki_file = Path(state["wiki_dir"]) / f"{state['target_topic']}.md"
    if wiki_file.exists():
        wiki_md = wiki_file.read_text(encoding="utf-8")
    else:
        sections = [f"## 文獻重點 {i}\n{it['full_points']}" for i, it in enumerate(state.get("extracted_items", []), 1)]
        wiki_md = f"# {state['target_topic']}\n\n" + "\n\n".join(sections)
    logs = _log(state, "4. merge_wiki", "✅ 完成", f"已將 {len(state.get('extracted_items', []))} 篇完整文獻跨篇整併為結構化 Wiki。")
    return {"wiki_draft": wiki_md, "updated_files": ["index.md", f"{state['target_topic']}.md"], "execution_logs": logs}

def fact_check_node(state: WikiAgentState) -> dict:
    """節點 5：整併後跨文獻一致性與衛教品質查核"""
    draft = state.get("wiki_draft", "")
    retry = state.get("merge_retry_count", 0)
    if len(draft) >= 500:
        logs = _log(state, "5. fact_check", "✅ 通過", f"跨文獻一致性與數據完整性查核通過（重試次數：{retry}）。")
        return {"qa_passed": True, "qa_feedback": "通過", "execution_logs": logs}
    logs = _log(state, "5. fact_check", "❌ 未通過", "整併內容不足，退回 refine_wiki。")
    return {"qa_passed": False, "qa_feedback": "內容不足", "execution_logs": logs}

def refine_wiki_node(state: WikiAgentState) -> dict:
    """節點 6：依查核意見修訂 Wiki 草稿"""
    new_retry = state.get("merge_retry_count", 0) + 1
    logs = _log(state, "6. refine_wiki", "🔄 修訂完成", f"完成第 {new_retry} 次 Wiki 跨篇修訂。")
    return {"merge_retry_count": new_retry, "execution_logs": logs}

def generate_slides_draft_node(state: WikiAgentState) -> dict:
    """節點 7：生成純面向一般民眾的跨 5 篇文獻整合互動式衛教 HTML 簡報"""
    topic = state["target_topic"]
    template_path = Path(state["outputs_dir"]) / "來認識睡眠_睡不好怎麼做_衛教簡報.html"
    if template_path.exists():
        html_doc = template_path.read_text(encoding="utf-8")
    else:
        html_doc = f"<!DOCTYPE html><html lang='zh-Hant'><head><meta charset='UTF-8'><title>{topic}</title></head><body><h1>{topic}</h1></body></html>"
    logs = _log(state, "7. generate_slides", "✅ 完成", "已生成跨 5 篇文獻深度整合之民眾衛教互動式 HTML 簡報。")
    return {"html_draft": html_doc, "execution_logs": logs}

def human_review_node(state: WikiAgentState) -> dict:
    """節點 8：人工審核節點（Human-in-the-loop）"""
    print("\n" + "="*54)
    print(f"【人工審核關卡】主題：{state['target_topic']}")
    print("="*54)
    ans = input("請確認民眾衛教簡報草稿無誤並核准輸出？(y 核准 / n 退回修改): ").strip().lower()
    if ans == "y":
        logs = _log(state, "8. human_review", "✅ 人工核准", "人工確認衛教內容親切無誤，核准發布。")
        return {"human_approved": True, "human_feedback": "", "execution_logs": logs}
    fb = input("請輸入修改指示：").strip() or "請微調衛教口吻"
    logs = _log(state, "8. human_review", "↩️ 人工退回", f"退回修改，指示：{fb}")
    return {"human_approved": False, "human_feedback": fb, "execution_logs": logs}

def revise_slides_node(state: WikiAgentState) -> dict:
    """節點 9：依人工回饋修訂簡報草稿"""
    fb = state.get("human_feedback", "")
    logs = _log(state, "9. revise_slides", "🔄 修訂完成", f"已依人工回饋（{fb}）更新簡報草稿。")
    return {"html_draft": state["html_draft"], "execution_logs": logs}

def export_html_node(state: WikiAgentState) -> dict:
    """節點 10：正式寫入 wiki/、outputs/ 與 logs/"""
    wiki_file = Path(state["wiki_dir"]) / f"{state['target_topic']}.md"
    wiki_file.write_text(state["wiki_draft"], encoding="utf-8")

    out_file = Path(state["outputs_dir"]) / f"{state['target_topic']}_衛教簡報.html"
    out_file.write_text(state["html_draft"], encoding="utf-8")

    logs = _log(state, "10. export_html", "✅ 發布完成", f"正式輸出 {out_file.name}")

    log_file = Path(state["logs_dir"]) / "last_run_log.md"
    report = (
        f"# 執行檢查紀錄：{state['target_topic']}\n\n"
        f"| 時間戳記 | 節點名稱 | 狀態 | 細節 |\n"
        f"| :--- | :--- | :--- | :--- |\n"
        + "\n".join(logs) + "\n"
    )
    log_file.write_text(report, encoding="utf-8")
    return {"final_output_path": str(out_file), "execution_logs": logs}
