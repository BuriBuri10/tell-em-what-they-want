from langgraph.graph import StateGraph
from workflows.state import GraphState

# Import fallback-related nodes
from workflows.graphs.campaign.nodes.objective_refiner_node import ObjectiveRefinerNode
from workflows.graphs.campaign.nodes.persona_enrichment_node import PersonaEnrichmentNode
from workflows.graphs.campaign.nodes.fallback_persona_node import FallbackPersonaNode
from workflows.graphs.campaign.nodes.budget_alert_node import BudgetAlertNode
from workflows.graphs.campaign.nodes.compliance_revision_node import ComplianceRevisionNode
from logs.logging_config import logger

class FallbackWorkflow:
    def __call__(self, state: GraphState) -> GraphState:
        # Your logic here
        state.valid_objective = True  # or False, based on your validation
        return state
    
    def __init__(self):
        logger.info("Initializing CampaignWorkflow...")

        self.objective_refiner_node = ObjectiveRefinerNode()
        self.persona_enrichment_node = PersonaEnrichmentNode()
        self.fallback_persona_node = FallbackPersonaNode()
        self.budget_alert_node = BudgetAlertNode()
        self.compliance_revision_node = ComplianceRevisionNode()

        self.graph = self.build_fallback_subgraph()

    def build_fallback_subgraph() -> StateGraph:
        """
        Fallback subgraph to handle recovery when validations or compliance checks fail.
        This may be called conditionally after the main validation subgraph.
        """
        fallback_subgraph = StateGraph(GraphState)

        # Nodes for handling different fallback paths
        fallback_subgraph.add_node("refine_objective", ObjectiveRefinerNode())
        fallback_subgraph.add_node("enrich_persona", PersonaEnrichmentNode())
        fallback_subgraph.add_node("fallback_persona", FallbackPersonaNode())
        fallback_subgraph.add_node("budget_alert", BudgetAlertNode())
        fallback_subgraph.add_node("compliance_revision", ComplianceRevisionNode())

        # Simple linear fallback sequence (can be made conditional later)
        fallback_subgraph.set_entry_point("refine_objective")
        fallback_subgraph.add_edge("refine_objective", "enrich_persona")
        fallback_subgraph.add_edge("enrich_persona", "fallback_persona")
        fallback_subgraph.add_edge("fallback_persona", "budget_alert")
        fallback_subgraph.add_edge("budget_alert", "compliance_revision")

        fallback_subgraph.set_finish_point("compliance_revision")

        return fallback_subgraph
