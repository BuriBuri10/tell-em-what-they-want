# from langgraph.graph import StateGraph, END
# from workflows.state import GraphState
# from workflows.graphs.campaign.nodes.recommend_node import RecommendNode


# def build_strategy_subgraph() -> StateGraph:
#     """
#     Constructs the strategy planning subgraph.

#     This subgraph recommends campaign strategies based on
#     segmented user data, past performance, and intent.

#     Returns:
#         StateGraph: The compiled strategy planning subgraph.
#     """
#     graph = StateGraph(GraphState)

#     # Add the recommendation node
#     graph.add_node("recommend", RecommendNode().process)

#     # Set entry and exit points
#     graph.set_entry_point("recommend")
#     graph.set_finish_point("recommend")

#     return graph.compile()


# # Manual test
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         state = GraphState(
#             query="Promote eco-friendly skincare products",
#             segment="eco-conscious millennials",
#             past_campaigns=["eco boost summer campaign", "organic beauty drop"],
#             conversation_history=[],
#         )

#         subgraph = build_strategy_subgraph()
#         result = await subgraph.invoke(state)
#         print("Recommendation result:", result.recommendation)

#     asyncio.run(test())


from langgraph.graph import StateGraph, END
from workflows.state import GraphState
from langchain_core.runnables import RunnableLambda
from workflows.graphs.campaign.nodes.recommend_node import RecommendNode


def build_strategy_subgraph(recommend_node: RecommendNode) -> StateGraph:
    """
    Constructs the strategy planning subgraph.

    This subgraph recommends campaign strategies based on
    segmented user data, past performance, and intent.

    Args:
        recommend_node (RecommendNode): Instance of the recommendation node.

    Returns:
        StateGraph: The compiled strategy planning subgraph.
    """
    # graph = StateGraph(GraphState)

    # # Add the recommendation node (reused from outside)
    # graph.add_node("recommend", recommend_node.process)

    # # Set entry and exit points
    # graph.set_entry_point("recommend")
    # graph.set_finish_point("recommend")

    # # return graph.compile()
    # return graph

    builder = StateGraph(GraphState)
    recommend = RunnableLambda(lambda state: recommend_node(state))  # ✅ wrap it!
    builder.add_node("recommend_node", recommend)
    builder.set_entry_point("recommend_node")
    builder.set_finish_point("recommend_node")
    return builder  # NOT builder.compile()


# Manual test
if __name__ == "__main__":
    import asyncio

    async def test():
        state = GraphState(
            query="Promote eco-friendly skincare products",
            segment="eco-conscious millennials",
            past_campaigns=["eco boost summer campaign", "organic beauty drop"],
            conversation_history=[],
        )

        recommender = RecommendNode()
        subgraph = build_strategy_subgraph(recommender)
        result = await subgraph.invoke(state)
        print("Recommendation result:", result.recommendation)

    asyncio.run(test())
