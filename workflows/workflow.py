import logging
import asyncio
import os
from datetime import datetime
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables.graph import CurveStyle

from workflows.state import GraphState
from workflows.graphs.campaign.nodes.segmenting_node import UserSegmenter
from workflows.graphs.campaign.nodes.recommend_node import RecommendNode
from workflows.graphs.campaign.nodes.generate_ad_node import GenerateAdNode
from workflows.graphs.campaign.nodes.human_in_the_loop_node import HumanReviewRouter
from workflows.graphs.campaign.nodes.feedback_loop_node import FeedbackLoopNode
from logs.logging_config import logger


class CampaignWorkflow:
    """
    Defines and compiles the LangGraph workflow for Campaign Generation
    """
    def __init__(self):
        logger.info("Initializing CampaignWorkflow...")

        self.segment_node = UserSegmenter()
        self.recommend_node = RecommendNode()
        self.generate_ad_node = GenerateAdNode()
        self.hitl = HumanReviewRouter()
        self.feedback_node = FeedbackLoopNode()

        self.graph = self._build_graph()

        logger.info("CampaignOrchestrator initialized successfully")

    def _build_graph(self):
        """
        Creates and compiles the LangGraph workflow for ad campaign generation.
        """
        workflow = StateGraph(GraphState)

        # Define nodes
        workflow.add_node("segment", self.segment_node.process)
        workflow.add_node("recommend", self.recommend_node.process)
        workflow.add_node("generate_ad", self.generate_ad_node.process)
        workflow.add_node("human_review", self.hitl.process)
        workflow.add_node("feedback_loop", self.feedback_node.process)

        # Connect the flow
        workflow.add_edge(START, "segment")
        workflow.add_edge("segment", "recommend")
        workflow.add_edge("recommend", "generate_ad")
        workflow.add_edge("generate_ad", "human_review")
        workflow.add_edge("human_review", "feedback_loop")
        workflow.add_edge("feedback_loop", END)

        logger.info("Workflow graph defined.")

        return workflow.compile()

    async def get_graph_structure(self, use_pyppeteer: bool = True) -> bytes:
        """
        Get graph structure visualization as PNG bytes.
        """
        graph = self.graph.get_graph()
        mermaid_string = graph.draw_mermaid(curve_style=CurveStyle.LINEAR)

        if use_pyppeteer:
            try:
                from langchain_core.runnables.graph_mermaid import _render_mermaid_using_pyppeteer
                return await _render_mermaid_using_pyppeteer(mermaid_string)
            except ImportError:
                logger.warning("Pyppeteer not installed. Run: pip install pyppeteer")
            except Exception as e:
                logger.warning(f"Pyppeteer render failed: {e}")

        # Fallback: use local renderer
        try:
            return graph.draw_mermaid_png(curve_style=CurveStyle.LINEAR)
        except Exception as e:
            logger.error(f"Mermaid PNG rendering failed: {e}")
            raise
    
    def _save_campaign_report(self, state: GraphState, user_id: str, query: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"campaign_outputs/{user_id}_{timestamp}.txt"
        os.makedirs("campaign_outputs", exist_ok=True)

        report = f"""📊 CAMPAIGN REPORT
                ────────────────────────────
                User ID: {user_id}
                Timestamp: {timestamp}
                Campaign Query: {query}

                User Segment: {state.user_segment or 'N/A'}
                Campaign Objective: {state.campaign_objective or 'N/A'}

                Recommendation:
                {state.campaign_recommendation or 'N/A'}

                Generated Ad Copy:
                {state.generated_ad or 'N/A'}

                Human Feedback:
                {state.ad_feedback or 'No feedback provided.'}
                """
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Campaign report saved: {filename}")

    async def run(self, query: str, user_id: str) -> dict:
        """
        Runs the campaign workflow asynchronously.

        Args:
            query (str): Campaign goal or theme.
            user_id (str): Identifier of the user/owner.

        Returns:
            dict: Final output state from the workflow.
        """
        try:
            logger.info(f"Running CampaignWorkflow for user_id={user_id}, query='{query}'")
            initial_state = GraphState(
                query=query,
                user_id=user_id
                # ad_output=None,
                # recommendations=None,
                # segmentation=None,
                # human_feedback=None,
            )
            result_raw = await self.graph.ainvoke(initial_state)

            # 🛠️ Convert dict back to GraphState
            result = GraphState(**result_raw)

            # Save formatted report
            self._save_campaign_report(result, user_id, query)

            return result
        
        except Exception as e:
            logger.error(f"Workflow run failed: {e}")
            return {"error": str(e)}


# if __name__ == "__main__":
#     async def main():
#         query = input("Enter campaign query (e.g. 'Launch summer sale campaign for Gen Z'): ").strip()
#         user_id = input("Enter user ID: ").strip()

#         workflow = CampaignWorkflow()
#         result = await workflow.run(query=query, user_id=user_id)

#         if result is None:
#             print("Workflow returned no result")
#             return

#         # if isinstance(result):
#         #     if "ad_output" in result:
#         #         print("\nGenerated Ad Output:\n")
#         #         print(result["ad_output"])
#         #     elif "error" in result:
#         #         print("\nWorkflow failed:")
#         #         print(result["error"])
#         #     else:
#         #         print("\nUnknown result format:")
#         #         print(result)
#         else:
#             print("\nUnexpected result type:")
#             print(result)

#         # Save visual representation of the graph
#         try:
#             graph_bytes = await workflow.get_graph_structure()
#             with open("campaign_graph_structure.png", "wb") as f:
#                 f.write(graph_bytes)
#             logger.info("Saved campaign graph structure as campaign_graph_structure.png")
#         except Exception as e:
#             logger.error(f"Could not save graph structure: {e}")

#     asyncio.run(main())


if __name__ == "__main__":
    async def main():
        query = input("Enter campaign query (e.g. 'Launch summer sale campaign for Gen Z'): ").strip()
        user_id = input("Enter user ID: ").strip()

        workflow = CampaignWorkflow()

        try:
            result = await workflow.run(query=query, user_id=user_id)

            print("\n🎯 CAMPAIGN WORKFLOW RESULT\n─────────────────────────────")
            print(f"🧑 User Segment: {result.user_segment or 'N/A'}")
            print(f"🎯 Campaign Objective: {result.campaign_objective or 'N/A'}")
            print(f"\n💡 Recommendation:\n{result.campaign_recommendation or 'N/A'}")
            print(f"\n📝 Generated Ad:\n{result.generated_ad or 'N/A'}")
            print(f"\n💬 Human Feedback:\n{result.ad_feedback or 'No feedback provided.'}")

        except Exception as e:
            print("\n🚨 Workflow failed:")
            print(str(e))
            return

        # Save visual representation of the graph
        try:
            graph_bytes = await workflow.get_graph_structure()
            with open("campaign_graph_structure.png", "wb") as f:
                f.write(graph_bytes)
            logger.info("Saved campaign graph structure as campaign_graph_structure.png")
        except Exception as e:
            logger.error(f"Could not save graph structure: {e}")

    asyncio.run(main())
