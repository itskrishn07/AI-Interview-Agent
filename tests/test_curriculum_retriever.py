from backend.services.curriculum_retriever import curriculum_retriever

def test_curriculum_loading():
    days = curriculum_retriever.get_all_days()
    assert len(days) >= 30

def test_get_day():
    day7 = curriculum_retriever.get_day(7)
    assert day7 is not None
    assert day7["title"] == "Embeddings Explained"
    assert "Sentence Transformers" in day7["tools"]

def test_get_module():
    mod3 = curriculum_retriever.get_module_for_day(7)
    assert mod3 is not None
    assert mod3["title"] == "Embeddings & Vector Search"

def test_format_day_summary():
    summary = curriculum_retriever.format_day_summary(7)
    assert "Embeddings Explained" in summary
    assert "Objectives:" in summary
