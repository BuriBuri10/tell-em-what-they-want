from langchain_core.runnables import RunnableLambda
from core.chain import ChainAccess
from workflows.state import GraphState
from logs.logging_config import logger


from langgraph.graph import StateGraph, END
from workflows.state import GraphState

# Import your node classes
from workflows.graphs.campaign.nodes.campaign_objective_validator_node import CampaignObjectiveValidatorNode
from workflows.graphs.campaign.nodes.persona_quality_checker_node import PersonaQualityCheckerNode
# from workflows.graphs.campaign.nodes.budget_classifier_node import BudgetClassifierNode
from workflows.graphs.campaign.nodes.channel_constraints_node import ChannelConstraintsNode
from workflows.graphs.campaign.nodes.channel_strategy_node import ChannelStrategyNode
from workflows.graphs.campaign.nodes.objective_refiner_node import ObjectiveRefinerNode
from workflows.graphs.campaign.nodes.persona_enrichment_node import PersonaEnrichmentNode

from logs.logging_config import logger


class ValidationWorkflow:
    def __init__(self):
        logger.info("Initializing ValidationWorkflow...")

        # Instantiating all node classes
        self.campaign_objective_validator_node = CampaignObjectiveValidatorNode()
        self.persona_quality_checker_node = PersonaQualityCheckerNode()
        # self.budget_classifier_node = BudgetClassifierNode()
        self.channel_constraints_node = ChannelConstraintsNode()
        self.channel_strategy_node = ChannelStrategyNode()
        self.objective_refiner_node = ObjectiveRefinerNode()
        self.persona_enrichment_node = PersonaEnrichmentNode()

        # Build graph
        self.graph = self.build_validation_subgraph()

    def build_validation_subgraph(self) -> StateGraph:
        """
        Constructs the validation subgraph responsible for:
        - Validating campaign objectives
        - Checking persona quality
        - Classifying budget and channel constraints
        - Enriching/refining fallback data if necessary
        """
        validation_graph = StateGraph(GraphState)

        # Add core validation nodes
        validation_graph.add_node("objective_validator", self.campaign_objective_validator_node.process)
        validation_graph.add_node("persona_checker", self.persona_quality_checker_node.process)
        validation_graph.add_node("channel_constraints", self.channel_constraints_node.process)
        validation_graph.add_node("channel_strategy", self.channel_strategy_node.process)

        # Add fallback/refinement nodes
        validation_graph.add_node("refine_objective", self.objective_refiner_node.process)
        validation_graph.add_node("enrich_persona", self.persona_enrichment_node.process)

        # Entry point
        validation_graph.set_entry_point("objective_validator")

        # Objective validator logic
        validation_graph.add_conditional_edges(
            "objective_validator",
            lambda state: state.valid_objective,
            {
                True: "persona_checker",
                False: "refine_objective"
            }
        )

        validation_graph.add_edge("refine_objective", "persona_checker")

        # # Persona checker logic
        # validation_graph.add_conditional_edges(
        #     "persona_checker",
        #     lambda state: state.valid_persona,
        #     {
        #         True: "budget_classifier",
        #         False: "enrich_persona"
        #     }
        # )
        
        validation_graph.add_edge("persona_checker", "enrich_persona")

        # Budget classifier logic
        # validation_graph.add_conditional_edges(
        #     "budget_classifier",
        #     lambda state: state.valid_budget,
        #     {
        #         True: "channel_constraints",
        #         False: "fallback_persona"
        #     }
        # )
        # validation_graph.add_edge("fallback_persona", "channel_constraints")

        validation_graph.add_edge("enrich_persona", "channel_constraints")
        validation_graph.add_edge("channel_constraints", "channel_strategy")

        # End after channel constraint check
        validation_graph.add_edge("channel_strategy", END)

        return validation_graph.compile()







