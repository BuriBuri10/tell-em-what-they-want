from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from core.utils.campaign_recs import CampaignReportSaver
from workflows.workflow import CampaignWorkflow
from workflows.state import GraphState
import asyncio

app = FastAPI(title="Campaign Workflow API", description="Endpoints for running and testing parts of the Campaign LangGraph workflow.")

campaign_workflow = CampaignWorkflow()

# ---------------------
# Request/Response Models
# ---------------------

class CampaignRequest(BaseModel):
    user_id: str = Field(..., example="user_12345")
    query: str = Field(..., example="Launch a marketing campaign for a new fitness app")

class NodeRequest(BaseModel):
    state: dict = Field(
        ..., 
        example={
            "user_id": "user_12345",
            "query": "Launch campaign for electric bikes",
            "user_persona": {"description": "eco-conscious commuter"},
            "generated_ad": "Ride green with our new e-bike!",
        }
    )

# ---------------------
# Full Workflow Endpoint
# ---------------------

@app.post("/run-campaign", summary="Run full campaign workflow", tags=["Workflow"])
async def run_campaign(req: CampaignRequest):
    """
    Executes the full campaign workflow based on a user query and user ID.

    **Example**:
    ```json
    {
        "user_id": "user_12345",
        "query": "Launch campaign for electric bikes"
    }
    ```
    """
    try:
        result = await campaign_workflow.run(query=req.query, user_id=req.user_id)

        # Save campaign report locally
        CampaignReportSaver.save(
            state=result,
            user_id=req.user_id,
            query=req.query
        )

        return result.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------
# Individual Node Endpoints (for testing/debugging)
# ---------------------

@app.post("/node/persona", summary="Run persona enrichment node", tags=["Nodes"])
async def persona_node(req: NodeRequest):
    """
    Runs the client persona node with partial state.

    **Example**:
    ```json
    {
        "state": {
            "user_id": "user_12345",
            "query": "Launch campaign for electric bikes"
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.client_persona_node.ainvoke(state)


@app.post("/node/strategy", summary="Run strategy recommendation node", tags=["Nodes"])
async def strategy_node(req: NodeRequest):
    """
    Runs the strategy recommendation node with enriched persona in state.

    **Example**:
    ```json
    {
        "state": {
            "user_persona": {"description": "eco-conscious commuter"}
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.strategy_node.ainvoke(state)


@app.post("/node/validate", summary="Run validation subgraph", tags=["Subgraphs"])
async def validate_node(req: NodeRequest):
    """
    Runs the entire validation subgraph (e.g., objective, budget, constraints checks).

    **Example**:
    ```json
    {
        "state": {
            "campaign_objective": "Boost awareness among Gen Z",
            "budget": 1500
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.validation_subgraph.ainvoke(state)


@app.post("/node/check_external_logs", summary="Check for external user behavior logs", tags=["Nodes"])
async def check_external_logs_node(req: NodeRequest):
    """
    Runs node to determine if user has historical external logs.

    **Example**:
    ```json
    {
        "state": {
            "user_id": "user_12345"
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.check_external_logs_node.process(state)


@app.post("/node/analytics", summary="Run analytics node", tags=["Nodes"])
async def analytics_node(req: NodeRequest):
    """
    Generates analytics data and feedback from external logs.

    **Example**:
    ```json
    {
        "state": {
            "external_logs_present": true
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.analytics_node.process(state)


@app.post("/node/segment", summary="Run segmentation node", tags=["Nodes"])
async def segmenting_node(req: NodeRequest):
    """
    Segments the audience based on analytics or persona.

    **Example**:
    ```json
    {
        "state": {
            "user_persona": {"description": "eco-conscious commuter"}
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.segmenting_node.process(state)


@app.post("/node/recommend", summary="Run recommendation node", tags=["Nodes"])
async def recommend_node(req: NodeRequest):
    """
    Recommends campaign strategies and content per segment/persona.

    **Example**:
    ```json
    {
        "state": {
            "segments": ["Urban bikers", "Eco activists"]
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.recommend_node.process(state)


@app.post("/node/generate_ad", summary="Run ad generation node", tags=["Nodes"])
async def generate_ad_node(req: NodeRequest):
    """
    Generates a textual ad based on the campaign strategy and persona.

    **Example**:
    ```json
    {
        "state": {
            "recommended_strategy": "Emphasize eco-friendliness and health",
            "user_persona": {"description": "fitness-focused student"}
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.generate_ad_node.process(state)


@app.post("/node/media_ad_generation", summary="Run media ad generation subgraph", tags=["Subgraphs"])
async def media_ad_subgraph(req: NodeRequest):
    """
    Generates media assets (video, social, email, etc.) based on ad copy.

    **Example**:
    ```json
    {
        "state": {
            "generated_ad": "Go green. Ride clean.",
            "preferred_channel": "social"
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.mediaAd_subgraph.ainvoke(state)


@app.post("/node/is_ab_testing_needed", summary="Check if A/B testing is needed", tags=["Nodes"])
async def is_ab_testing_needed_node(req: NodeRequest):
    """
    Determines if A/B testing is necessary based on the campaign settings.

    **Example**:
    ```json
    {
        "state": {
            "budget_tier": "high"
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.is_ab_testing_needed.process(state)


@app.post("/node/ab_testing", summary="Run A/B testing logic node", tags=["Nodes"])
async def ab_testing_node(req: NodeRequest):
    """
    Creates multiple ad variants and runs scoring for A/B testing.

    **Example**:
    ```json
    {
        "state": {
            "generated_ad": "Ride green with our e-bikes!"
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.ab_testing.process(state)


@app.post("/node/human_review", summary="Run human-in-the-loop review node", tags=["Nodes"])
async def human_review_node(req: NodeRequest):
    """
    Sends ad content for human feedback and integrates it into the campaign.

    **Example**:
    ```json
    {
        "state": {
            "ad_variants": ["Ad A", "Ad B"]
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.hitl.process(state)


@app.post("/node/feedback_loop", summary="Run feedback loop node", tags=["Nodes"])
async def feedback_loop_node(req: NodeRequest):
    """
    Final feedback evaluation and campaign readiness review.

    **Example**:
    ```json
    {
        "state": {
            "human_feedback": "Use softer tone for Gen Z"
        }
    }
    """
    state = GraphState(**req.state)
    return await campaign_workflow.feedback_node.process(state)








# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from logs.logging_config import logger

# from api.routes import user, campaign, analytics

# # Load environment variables
# load_dotenv()

# # Logger setup
# logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# # Initialize FastAPI app
# app = FastAPI(
#     title="AI Marketing Campaign Platform",
#     description="AI-powered personalized marketing & ad generation system",
#     version="1.0.0"
# )

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # TODO: Restrict in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Health check
# @app.get("/ping")
# def health_check():
#     return {"status": "ok"}

# # Register routers
# app.include_router(user.router, prefix="/api/user", tags=["User"])
# app.include_router(campaign.router, prefix="/api/campaign", tags=["Campaign"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# @app.get("/")
# async def root():
#     """
#     Basic health check endpoint to verify that the API is running.
#     """
#     logger.info("Health check endpoint '/' was called.")
#     return {"message": "AI Marketing API is up and running!"}

