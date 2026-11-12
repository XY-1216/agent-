from typing import TypedDict, List, Dict

class WikiAgentState(TypedDict):
    target_topic: str
    raw_dir: str
    wiki_dir: str
    outputs_dir: str
    logs_dir: str

    raw_documents: List[Dict[str, str]]
    extracted_items: List[Dict[str, str]]
    extract_retry_count: int
    extract_passed: bool
    extract_feedback: str

    wiki_draft: str
    updated_files: List[str]
    merge_retry_count: int
    qa_passed: bool
    qa_feedback: str

    html_draft: str
    human_approved: bool
    human_feedback: str
    final_output_path: str

    execution_logs: List[str]
