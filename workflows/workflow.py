# Subgraph imports
from workflows.graphs.campaign.subgraphs.validation_subgraph import ValidationWorkflow
from workflows.graphs.campaign.subgraphs.media_ad_gen_subgraph import MediaAdWorkflow

import logging
import asyncio
import os
from datetime import datetime
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables.graph import CurveStyle

from workflows.state import GraphState
from workflows.graphs.campaign.nodes.persona_node import UserPersonaNode
from workflows.graphs.campaign.nodes.strategy_node import StrategyNode
from workflows.graphs.campaign.nodes.check_external_logs_node import CheckExternalLogsNode
from workflows.graphs.campaign.nodes.analytics_node import AnalyticsNode
from workflows.graphs.campaign.nodes.segmenting_node import UserSegmenter
from workflows.graphs.campaign.nodes.recommend_node import RecommendNode
from workflows.graphs.campaign.nodes.is_ab_testing_needed_node import MultiVariantTestNode
from workflows.graphs.campaign.nodes.multi_variant_test_branching_node import ABTestingNode
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
        
        self.client_persona_node = UserPersonaNode()
        self.strategy_node = StrategyNode()
        self.check_external_logs_node = CheckExternalLogsNode()
        self.analytics_node = AnalyticsNode()
        self.segmenting_node = UserSegmenter()
        self.recommend_node = RecommendNode()
        self.is_ab_testing_needed = MultiVariantTestNode()
        self.ab_testing = ABTestingNode()
        self.generate_ad_node = GenerateAdNode()
        self.hitl = HumanReviewRouter()
        self.feedback_node = FeedbackLoopNode()

        self.validation_subgraph = ValidationWorkflow().graph
        self.mediaAd_subgraph = MediaAdWorkflow().graph

        self.graph = self._build_graph()

        logger.info("CampaignOrchestrator initialized successfully")

    def _build_graph(self):
        """
        Builds the complete campaign workflow using modular subgraphs and key decision/action nodes.
        """
        campaign_graph = StateGraph(GraphState)

        # Attach subgraphs
        campaign_graph.add_node("validation", self.validation_subgraph)
        campaign_graph.add_node("media_ad_generation", self.mediaAd_subgraph)

        # Attach standalone nodes
        campaign_graph.add_node("client persona", self.client_persona_node.process)
        campaign_graph.add_node("proto-strategy", self.strategy_node.process)
        campaign_graph.add_node("check_external_logs", self.check_external_logs_node.process)
        campaign_graph.add_node("analytics", self.analytics_node.process)
        campaign_graph.add_node("segmenting", self.segmenting_node.process)
        campaign_graph.add_node("recommend", self.recommend_node.process)
        campaign_graph.add_node("is_ab_testing_needed", self.is_ab_testing_needed.process)
        campaign_graph.add_node("ab_testing", self.ab_testing.process)
        campaign_graph.add_node("generate_ad", self.generate_ad_node.process)
        campaign_graph.add_node("human_review", self.hitl.process)
        campaign_graph.add_node("feedback_loop", self.feedback_node.process)

        # Set entry point and edges
        campaign_graph.add_edge(START, "client persona")
        campaign_graph.add_edge("client persona", "proto-strategy")
        campaign_graph.add_edge("proto-strategy", "validation")
        campaign_graph.add_edge("validation", "check_external_logs")
        campaign_graph.add_conditional_edges(
            "check_external_logs",
            lambda state: state.has_external_logs,
            {
                True: "analytics",
                False: "segmenting"
            }
        )
        campaign_graph.add_edge("analytics", "recommend")
        campaign_graph.add_edge("segmenting", "recommend")
        campaign_graph.add_edge("recommend", "generate_ad")
        campaign_graph.add_edge("generate_ad", "media_ad_generation")
        campaign_graph.add_edge("media_ad_generation", "is_ab_testing_needed")

        campaign_graph.add_conditional_edges(
                "is_ab_testing_needed",
                lambda state: state.multi_variant_required,
                {
                    True: "ab_testing",
                    False: END
                }
            )
        campaign_graph.add_conditional_edges("ab_testing", lambda x: x.requires_revision, {True: "recommend", False: END})

        # campaign_graph.add_conditional_edges(
        #         "is_ab_testing_needed",
        #         lambda state: state.multi_variant_required,
        #         {
        #             True: "ab_testing",
        #             False: "human_review"
        #         }
        #     )
        # campaign_graph.add_edge("ab_testing", "human_review")
        # campaign_graph.add_conditional_edges("human_review", lambda x: x.requires_revision, {True: "recommend", False: "feedback_loop"})
        # campaign_graph.add_edge("feedback_loop", END)

        return campaign_graph.compile()


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


if __name__ == "__main__":
    async def main():
        query = input("Enter campaign query (e.g. 'Launch summer sale campaign for Gen Z'): ").strip()
        user_id = input("Enter user ID: ").strip()

        workflow = CampaignWorkflow()

        try:
            result = await workflow.run(query=query, user_id=user_id)

            print("\n CAMPAIGN WORKFLOW RESULT\n─────────────────────────")
            print(f"User Segment: {result.user_segment or 'N/A'}")
            print(f"Campaign Objective: {result.campaign_objective or 'N/A'}")
            print(f"\nRecommendation:\n{result.campaign_recommendation or 'N/A'}")
            print(f"\nGenerated Ad:\n{result.generated_ad or 'N/A'}")
            print(f"\nHuman Feedback:\n{result.ad_feedback or 'No feedback provided.'}")

        except Exception as e:
            print("\nWorkflow failed:")
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
