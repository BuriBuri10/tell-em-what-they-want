from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from logs.logging_config import logger

from api.routes import user, campaign, analytics

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# Initialize FastAPI app
app = FastAPI(
    title="AI Marketing Campaign Platform",
    description="AI-powered personalized marketing & ad generation system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/ping")
def health_check():
    return {"status": "ok"}

# Register routers
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(campaign.router, prefix="/api/campaign", tags=["Campaign"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """
    Basic health check endpoint to verify that the API is running.
    """
    logger.info("Health check endpoint '/' was called.")
    return {"message": "AI Marketing API is up and running!"}

