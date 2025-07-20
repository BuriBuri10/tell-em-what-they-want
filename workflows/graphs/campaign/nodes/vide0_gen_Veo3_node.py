import os
import time
from google.cloud import aiplatform
from dotenv import load_dotenv
from workflows.state import GraphState
from logs.logging_config import logger

# Load env vars
load_dotenv()

# --- Required Environment Variables ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
VEO_MODEL_NAME = os.environ.get("VEO_MODEL_ID", "veo-3.0-generate-preview")
OUTPUT_BUCKET = os.environ.get("VEO_OUTPUT_GCS_BUCKET")  # e.g., "gs://your-veo-output-bucket"

if not PROJECT_ID or not OUTPUT_BUCKET:
    raise ValueError("Missing required environment variables: GCP_PROJECT_ID or VEO_OUTPUT_GCS_BUCKET")

# --- Initialize Vertex AI Platform ---
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# --- Model Singleton ---
try:
    veo_model = aiplatform.GenerativeModel(model_name=VEO_MODEL_NAME)
    logger.info(f"Initialized Veo 3 model: {VEO_MODEL_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize Veo 3 model: {e}")
    veo_model = None


class VideoAdGeneratorNode:
    """
    Node that generates a short promotional video using Veo 3 on Vertex AI.
    """

    def __init__(self):
        if not veo_model:
            raise RuntimeError("Veo 3 model failed to initialize.")
        self.model = veo_model

    async def process(self, state: GraphState) -> GraphState:
        """
        Generates a promotional video and updates state with the GCS URI.
        """
        try:
            ad_copy = state.generated_ad_copy
            metadata = state.campaign_metadata or {}

            if not ad_copy:
                raise ValueError("Missing ad copy for video generation.")

            prompt = self._build_video_prompt(ad_copy, metadata)
            logger.debug(f"Prompt for Veo 3:\n{prompt}")

            output_filename = f"veo_output_{int(time.time())}.mp4"
            output_uri = os.path.join(OUTPUT_BUCKET, output_filename)

            generation_config = {
                "resolution": "1080p",
                "aspectRatio": "16:9",
                "personGeneration": "allow_all"
            }

            logger.info("Sending video generation request to Vertex AI Veo...")
            operation = self.model.generate_video(
                prompt=prompt,
                generation_config=generation_config,
                storage_uri=output_uri
            )

            start_time = time.time()
            timeout = 300  # seconds

            while not operation.done():
                if time.time() - start_time > timeout:
                    operation.cancel()
                    raise TimeoutError("Video generation timed out.")
                logger.info("Video generation in progress...")
                time.sleep(10)

            if operation.error:
                raise RuntimeError(f"Veo 3 generation failed: {operation.error.message}")

            result = operation.result()
            if result and result.gcs_uri:
                logger.info(f"Video generated successfully at: {result.gcs_uri}")
                state.generated_video_url = result.gcs_uri
                state.video_ready = True
            else:
                raise ValueError("No GCS URI returned after video generation.")

        except Exception as e:
            logger.error(f"Video generation error: {e}")
            state.generated_video_url = None
            state.video_ready = False
            state.error = str(e)

        return state

    def _build_video_prompt(self, ad_copy: str, metadata: dict) -> str:
        """
        Builds a prompt string for the Veo model.
        """
        tone = metadata.get("tone", "modern and energetic")
        brand = metadata.get("brand", "your brand")
        platform = metadata.get("channel", "social media")
        duration = metadata.get("duration", "15 seconds")

        prompt = (
            f"Create a {duration} branded promotional video for {brand}.\n"
            f"Tone: {tone}. Platform: {platform}.\n"
            f"Script:\n{ad_copy}\n"
            f"Include modern transitions, clean motion graphics, and end with a strong CTA."
        )
        return prompt


# --- Manual Test Execution ---
if __name__ == "__main__":
    import asyncio

    async def test():
        test_state = GraphState(
            generated_ad_copy="Experience the next-gen hydration with AquaSmart bottles. Track, sync, hydrate — intelligently.",
            campaign_metadata={
                "brand": "AquaSmart",
                "tone": "clean and futuristic",
                "channel": "YouTube Shorts",
                "duration": "10 seconds"
            }
        )

        node = VideoAdGeneratorNode()
        updated = await node.process(test_state)

        print(f"\nGenerated Video URL: {updated.generated_video_url or updated.error}")

    asyncio.run(test())


# from langchain_core.runnables import RunnableLambda
# from workflows.state import GraphState
# from logs.logging_config import logger
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# # Load API key
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY)


# class VideoAdGeneratorNode:
#     """
#     Node that generates a short promotional video based on ad copy and campaign metadata,
#     using Google's Veo 3 via the Gemini API.
#     """

#     def __init__(self):
#         """
#         Initializes the Gemini API model for video generation.
#         """
#         self.model = genai.GenerativeModel(model_name="video-vae-1")  # adjust model name as needed
#         logger.info("VideoAdGeneratorNode initialized with Gemini Veo model.")

#     async def process(self, state: GraphState) -> GraphState:
#         """
#         Generates a short video ad from campaign data and stores the video URL in state.

#         Args:
#             state (GraphState): Current graph state containing ad copy and campaign metadata.

#         Returns:
#             GraphState: Updated state with generated video URL.
#         """
#         try:
#             ad_copy = state.generated_ad_copy
#             metadata = state.campaign_metadata or {}

#             if not ad_copy:
#                 raise ValueError("Missing ad copy for video generation.")

#             logger.debug("Generating video for ad copy: %s", ad_copy)

#             prompt = self._build_video_prompt(ad_copy, metadata)
#             response = await self.model.generate_content_async(prompt)
#             video_url = self._extract_video_url(response)

#             if not video_url:
#                 raise ValueError("No video URL returned from Gemini.")

#             state.generated_video_url = video_url
#             state.video_ready = True
#             logger.info(f"Video generated and stored at: {video_url}")

#         except Exception as e:
#             logger.error(f"Video generation failed: {str(e)}")
#             state.video_ready = False
#             state.generated_video_url = None
#             state.error = str(e)

#         return state

#     def _build_video_prompt(self, ad_copy: str, metadata: dict) -> str:
#         """
#         Builds a natural language prompt for the video generation model.
#         """
#         tone = metadata.get("tone", "modern and engaging")
#         brand = metadata.get("brand", "your brand")
#         platform = metadata.get("channel", "social media")
#         duration = metadata.get("duration", "15 seconds")

#         prompt = (
#             f"Create a {duration} branded promotional video for {brand}.\n"
#             f"Tone: {tone}. Target platform: {platform}.\n"
#             f"Content:\n{ad_copy}\n"
#             f"Include visual transitions, clean typography, and a CTA at the end."
#         )

#         return prompt

#     def _extract_video_url(self, response) -> str:
#         """
#         Extracts video URL from Gemini response.
#         """
#         try:
#             for candidate in response.candidates:
#                 content = candidate.content.parts[0].text
#                 if "http" in content:
#                     return content.strip()
#         except Exception as e:
#             logger.warning(f"Error parsing video response: {e}")
#         return ""


# # Manual test runner
# if __name__ == "__main__":
#     import asyncio

#     async def test():
#         test_state = GraphState(
#             generated_ad_copy="Discover the future of wellness with our AI-powered fitness ring. Stay fit, stay smart.",
#             campaign_metadata={
#                 "brand": "PulseTech",
#                 "tone": "energetic and innovative",
#                 "channel": "Instagram Reels",
#                 "duration": "10 seconds"
#             }
#         )

#         node = VideoAdGeneratorNode()
#         updated = await node.process(test_state)

#         print(f"\nVideo URL:\n{updated.generated_video_url or updated.error}")

#     asyncio.run(test())
