from pathlib import Path
from graph import build_wiki_graph

def main():
    root = Path(__file__).resolve().parent.parent
    topic = input("請輸入衛教主題 (預設: 來認識睡眠，睡不好怎麼做): ").strip() or "來認識睡眠，睡不好怎麼做"

    app = build_wiki_graph(use_checkpointer=True)
    initial_state = {
        "target_topic": topic,
        "raw_dir": str(root / "raw"),
        "wiki_dir": str(root / "wiki"),
        "outputs_dir": str(root / "outputs"),
        "logs_dir": str(root / "logs"),
        "raw_documents": [],
        "extracted_items": [],
        "extract_retry_count": 0,
        "extract_passed": False,
        "extract_feedback": "",
        "wiki_draft": "",
        "updated_files": [],
        "merge_retry_count": 0,
        "qa_passed": False,
        "qa_feedback": "",
        "html_draft": "",
        "human_approved": False,
        "human_feedback": "",
        "final_output_path": "",
        "execution_logs": [],
    }
    config = {"configurable": {"thread_id": "sleep-wiki-complete"}}
    app.invoke(initial_state, config=config)
    print("\n完成！簡報已存於 outputs/，檢查紀錄已存於 logs/。")

if __name__ == "__main__":
    main()
