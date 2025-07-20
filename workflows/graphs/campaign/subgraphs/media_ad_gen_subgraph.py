from langgraph.graph import StateGraph, END
from typing import Annotated, TypedDict

from workflows.graphs.campaign.nodes.email_ad_generator_node import EmailAdGeneratorNode
from workflows.graphs.campaign.nodes.social_ad_generator_node import SocialAdGeneratorNode
from workflows.graphs.campaign.nodes.web_ad_generator_node import WebAdGeneratorNode
# from workflows.graphs.campaign.nodes.vide0_gen_Veo3_node import VideoAdGeneratorNode
from logs.logging_config import logger
from workflows.state import GraphState

# Define the input/output schema for the subgraph
class MediaAdState(TypedDict):
    from typing_extensions import Annotated
    graph_state: Annotated[GraphState, lambda a, b: a or b]
    # graph_state: Annotated[GraphState, lambda x: x]

class MediaAdWorkflow:
    def __call__(self, state: GraphState) -> GraphState:
        # Your logic here
        state.valid_objective = True  # or False, based on your validation
        return state

    def __init__(self):
        logger.info("Initializing CampaignWorkflow...")

        self.email_ad_gen_node = EmailAdGeneratorNode()
        self.social_ad_gen_node = SocialAdGeneratorNode()
        self.web_ad_gen_node = WebAdGeneratorNode()

        self.graph = self.build_media_ad_generation_subgraph()

    # Initialize the subgraph
    def build_media_ad_generation_subgraph(self) -> StateGraph:
        media_subgraph = StateGraph(MediaAdState)

        # Nodes for generating ads in various formats
        media_subgraph.add_node("generate_email_ad", self.email_ad_gen_node.process)
        media_subgraph.add_node("generate_social_ad", self.social_ad_gen_node.process)
        media_subgraph.add_node("generate_web_ad", self.web_ad_gen_node.process)

        # Control flow
        media_subgraph.set_entry_point("generate_email_ad")
        media_subgraph.add_edge("generate_email_ad", "generate_social_ad")
        media_subgraph.add_edge("generate_social_ad", "generate_web_ad")
        media_subgraph.add_edge("generate_web_ad", END)

        return media_subgraph.compile()
