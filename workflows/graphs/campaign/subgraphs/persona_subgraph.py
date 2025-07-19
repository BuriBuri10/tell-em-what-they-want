# from langgraph.graph import StateGraph, END
# from workflows.state import GraphState
# from workflows.graphs.campaign.nodes.segment_node import UserSegmenter


# def build_persona_subgraph() -> StateGraph:
#     """
#     Constructs the persona generation subgraph.

#     This subgraph focuses on user segmentation, transforming raw user data
#     into segments that can be used downstream for campaign strategy and personalization.

#     Returns:
#         StateGraph: Configured persona subgraph.
#     """
#     graph = StateGraph(GraphState)

#     # Add the segmentation node
#     graph.add_node("segment", UserSegmenter().process)

#     # Set the entry and exit points
#     graph.set_entry_point("segment")
#     graph.set_finish_point("segment")

#     return graph.compile()


# # Manual test
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         state = GraphState(
#             query="Promote eco-friendly skincare products",
#             conversation_history=[],
#             user_data={"age": 25, "interests": ["sustainability", "beauty"]}
#         )

#         subgraph = build_persona_subgraph()
#         result = await subgraph.invoke(state)
#         print("Segmentation result:", result.segment)

#     asyncio.run(test())




from langgraph.graph import StateGraph, END
from workflows.state import GraphState
from langchain_core.runnables import RunnableLambda
from workflows.graphs.campaign.nodes.segment_node import UserSegmenter


def build_persona_subgraph(user_segmenter: UserSegmenter) -> StateGraph:
    """
    Constructs the persona generation subgraph.

    This subgraph focuses on user segmentation, transforming raw user data
    into segments that can be used downstream for campaign strategy and personalization.

    Args:
        user_segmenter (UserSegmenter): Instance of the segmentation node.

    Returns:
        StateGraph: Configured persona subgraph.
    """
    # graph = StateGraph(GraphState)

    # # Add the segmentation node (reusing the passed instance)
    # graph.add_node("segment", user_segmenter.process)

    # # Set the entry and exit points
    # graph.set_entry_point("segment")
    # graph.set_finish_point("segment")

    # # return graph.compile()
    # return graph

    builder = StateGraph(GraphState)
    segment_node = RunnableLambda(lambda state: user_segmenter(state))
    builder.add_node("segment", segment_node)  # ✅ wrap it!

    builder.set_entry_point("segment")
    builder.set_finish_point("segment")
    return builder  # NOT builder.compile()



# Manual test
if __name__ == "__main__":
    import asyncio

    async def test():
        state = GraphState(
            query="Promote eco-friendly skincare products",
            conversation_history=[],
            user_data={"age": 25, "interests": ["sustainability", "beauty"]}
        )

        segmenter = UserSegmenter()
        subgraph = build_persona_subgraph(segmenter)
        result = await subgraph.invoke(state)
        print("Segmentation result:", result.segment)

    asyncio.run(test())

