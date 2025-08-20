from app.services.langgraph.agent_react import (
    make_order_status_agent,
    make_product_reco_agent,
    make_general_qa_agent,
    make_handover_agent,
)


def test_agents_constructible():
    a1 = make_order_status_agent()
    a2 = make_product_reco_agent()
    a3 = make_general_qa_agent()
    a4 = make_handover_agent()
    assert a1 and a2 and a3 and a4
    print("✅ test_agents_constructible passed")


def test_agents_have_min_two_tools():
    a1 = make_order_status_agent()
    a2 = make_product_reco_agent()
    a3 = make_general_qa_agent()
    a4 = make_handover_agent()
    assert len(a1.tools) >= 2
    assert len(a2.tools) >= 2
    assert len(a3.tools) >= 2
    assert len(a4.tools) >= 2
    print("✅ test_agents_have_min_two_tools passed")


if __name__ == "__main__":
    try:
        test_agents_constructible()
        test_agents_have_min_two_tools()
        print("🎉 All tests passed!")
    except AssertionError as e:
        print("❌ A test failed:", e)
