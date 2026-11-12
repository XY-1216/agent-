from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import WikiAgentState
from nodes import (
    ingest_raw_node,
    extract_check_node,
    re_extract_node,
    merge_wiki_node,
    fact_check_node,
    refine_wiki_node,
    generate_slides_draft_node,
    human_review_node,
    revise_slides_node,
    export_html_node,
)

def route_after_extract_check(state: WikiAgentState) -> str:
    if state.get("extract_passed") or state.get("extract_retry_count", 0) >= 2:
        return "merge_wiki"
    return "re_extract"

def route_after_fact_check(state: WikiAgentState) -> str:
    if state.get("qa_passed") or state.get("merge_retry_count", 0) >= 3:
        return "generate_slides"
    return "refine_wiki"

def route_after_human_review(state: WikiAgentState) -> str:
    if state.get("human_approved"):
        return "export_html"
    return "revise_slides"

def build_wiki_graph(use_checkpointer: bool = True):
    workflow = StateGraph(WikiAgentState)

    workflow.add_node("ingest_raw", ingest_raw_node)
    workflow.add_node("extract_check", extract_check_node)
    workflow.add_node("re_extract", re_extract_node)
    workflow.add_node("merge_wiki", merge_wiki_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("refine_wiki", refine_wiki_node)
    workflow.add_node("generate_slides", generate_slides_draft_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("revise_slides", revise_slides_node)
    workflow.add_node("export_html", export_html_node)

    workflow.set_entry_point("ingest_raw")
    workflow.add_edge("ingest_raw", "extract_check")
    workflow.add_conditional_edges("extract_check", route_after_extract_check, {"re_extract": "re_extract", "merge_wiki": "merge_wiki"})
    workflow.add_edge("re_extract", "extract_check")

    workflow.add_edge("merge_wiki", "fact_check")
    workflow.add_conditional_edges("fact_check", route_after_fact_check, {"refine_wiki": "refine_wiki", "generate_slides": "generate_slides"})
    workflow.add_edge("refine_wiki", "fact_check")

    workflow.add_edge("generate_slides", "human_review")
    workflow.add_conditional_edges("human_review", route_after_human_review, {"revise_slides": "revise_slides", "export_html": "export_html"})
    workflow.add_edge("revise_slides", "human_review")
    workflow.add_edge("export_html", END)

    return workflow.compile(checkpointer=MemorySaver() if use_checkpointer else None)
