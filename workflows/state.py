from enum import Enum
from typing import Annotated, Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field
from core.reducer import Reducer


class ReadyState(str, Enum):
    """Explicit states used for flow control."""
    WAITING = "waiting"
    COMPLETE = "complete"
    RESET = "reset"


class GraphState(BaseModel):
    """
    State object shared between LangGraph nodes in the marketing campaign workflow.
    """
    # Validation results
    objective_is_valid: Annotated[Optional[bool], Reducer.update] = False
    persona_is_valid: Annotated[Optional[bool], Reducer.update] = False
    valid_objective: Annotated[Optional[bool], Reducer.update] = False

    # Flow control flags
    has_external_logs: Annotated[Optional[bool], Reducer.update] = False

    # Inputs
    external_user_logs: Annotated[Optional[List[Dict]], Reducer.update] = None
    query: Annotated[Optional[str], Reducer.update] = None
    vdb_query: Annotated[Optional[str], Reducer.update] = None
    user_profile: Annotated[Optional[str], Reducer.update] = None
    campaign_goal: Annotated[Optional[str], Reducer.update] = None
    campaign_objective: Annotated[Optional[str], Reducer.update] = None
    channel_constraints_approved: Annotated[Optional[bool], Reducer.update] = None


    ad_variants: Annotated[Optional[List[str]], Reducer.update] = None  # For A/B testing output
    reviewed_ads: Annotated[Optional[List[Dict]], Reducer.update] = None  # For storing human-reviewed ads
    final_ad: Annotated[Optional[str], Reducer.update] = None
    requires_revision: Annotated[Optional[bool], Reducer.update] = None

    # Conversation context
    conversation_history: Annotated[
        List[Dict[str, str]], lambda curr, new: Reducer.append_and_trim(curr, new, max_length=5)
    ] = Field(default_factory=list)

    # Segmentation outputs
    segment: Annotated[Optional[Literal["budget", "standard", "premium"]], Reducer.update] = None
    segmenter_ready: Annotated[Optional[bool], Reducer.update] = False
    user_persona: Annotated[Optional[Dict[str, Any]], Reducer.update] = None
    persona_is_enriched: Annotated[Optional[bool], Reducer.update] = False
    valid_persona: Annotated[Optional[bool], Reducer.update] = False

    # Ad generation
    ad_copy: Annotated[Optional[str], Reducer.update] = None
    ad_type: Annotated[Optional[str], Reducer.update] = None

    # Channel-specific instructions and constraints
    channel_instructions: Annotated[Optional[str], Reducer.update] = None
    channel_constraints: Annotated[Optional[Dict[str, Any]], Reducer.update] = None
    constraints_found: Annotated[Optional[bool], Reducer.update] = False
    budget_tier: Annotated[Optional[str], Reducer.update] = None

    # Recommendation engine
    strategy_recommendation: Annotated[Optional[str], Reducer.update] = None
    recommended_channels: Annotated[Optional[List[str]], Reducer.update] = Field(default_factory=list)
    campaign_recommendation: Annotated[Optional[str], Reducer.update] = None
    recommendation_diff: Annotated[Optional[str], Reducer.update] = None
    recommendation: Annotated[Optional[str], Reducer.update] = None
    previous_recommendation: Annotated[Optional[str], Reducer.update] = None


    # ab testing
    multi_variant_required: Annotated[Optional[bool], Reducer.update] = False

    # Missing for RecommendNode
    user_segment: Annotated[Optional[str], Reducer.update] = None
    recommendation_ready: Annotated[Optional[bool], Reducer.update] = False
    strategy: Annotated[Optional[str], Reducer.update] = None
    product_details: Annotated[Optional[str], Reducer.update] = None
    user_id: Annotated[Optional[str], Reducer.update] = None

    # Human feedback & routing
    requires_human_review: Annotated[Optional[bool], Reducer.update] = False
    approved_by_human: Annotated[Optional[bool], Reducer.update] = False
    feedback_notes: Annotated[Optional[str], Reducer.update] = None
    # human_review_required: Annotated[Optional[bool], Reducer.update] = False
    ad_feedback: Annotated[Optional[str], Reducer.update] = None
    feedback_ready: Annotated[Optional[bool], Reducer.update] = False
    feedback_analysis: Annotated[Optional[str], Reducer.update] = None


   # Ad generation
    ad_copy: Annotated[Optional[str], Reducer.update] = None
    ad_type: Annotated[Optional[str], Reducer.update] = None
    generated_ad: Annotated[Optional[str], Reducer.update] = None
    ad_generation_ready: Annotated[Optional[bool], Reducer.update] = False  # ✅ Add this
    ad_output: Annotated[Optional[str], Reducer.update] = None
    ad_content: Annotated[Optional[str], Reducer.update] = None


    # Control
    error: Annotated[Optional[str], Reducer.update] = None
    ready_state: Annotated[Optional[ReadyState], Reducer.update] = ReadyState.WAITING
    stream_values: Annotated[Dict, Reducer.update] = Field(default_factory=dict)

    # Budget classification
    budget_class: Annotated[Optional[str], Reducer.update] = None
    budget_hint: Annotated[Optional[str], Reducer.update] = None
    # Budget validation
    valid_budget: Annotated[Optional[bool], Reducer.update] = False


    # Recommendation-related fields
    user_segment: Annotated[Optional[str], Reducer.update] = None
    recommendation_ready: Annotated[Optional[bool], Reducer.update] = False
    strategy: Annotated[Optional[str], Reducer.update] = None
    product_details: Annotated[Optional[str], Reducer.update] = None
    user_id: Annotated[Optional[str], Reducer.update] = None

    # Ad generation fields
    generated_ad: Annotated[Optional[str], Reducer.update] = None
    ad_generation_ready: Annotated[Optional[bool], Reducer.update] = False
    ad_output: Annotated[Optional[str], Reducer.update] = None
    ad_content: Annotated[Optional[str], Reducer.update] = None

