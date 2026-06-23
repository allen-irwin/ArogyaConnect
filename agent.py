# pyrefly: ignore [missing-import]
import sys
import os
from dotenv import load_dotenv
load_dotenv()

from google.adk import Agent, Workflow, Event
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
# pyrefly: ignore [missing-import]
from google.genai import Client, types

# Configure robust client-side retries to handle transient 503 Service Unavailable errors
http_retry_config = types.HttpOptions(
    retry_options=types.HttpRetryOptions(initial_delay=2.0, attempts=5)
)

# Initialize Gemini Client with retry configuration
client = Client(http_options=http_retry_config)

# 1. Classification Router Function (Internal, does not print user messages)
async def classifier_function(node_input: str):
    response = await client.aio.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"""You are a healthcare classification assistant.
Analyze the user's query and classify it into exactly one of the following categories:
- "EMERGENCY": If the query indicates a critical emergency, severe pain, unresponsiveness, breathing difficulty, chest pain, heavy bleeding, or any life-threatening symptoms.
- "ROUTINE": If the query is a routine medical inquiry, general health question, symptom checker for mild issues, scheduling/matching request, OR a diagnostic/prescription question (e.g. 'Do I have diabetes?', 'What pill should I take?').

User query: {node_input}

Respond with ONLY the category name ("EMERGENCY" or "ROUTINE"), nothing else. Do not add markdown, quotes, or explanation.""",
    )
    category = response.text.strip().upper()
    if "EMERGENCY" in category:
        return Event(route="EMERGENCY", output=node_input)
    else:
        return Event(route="ROUTINE", output=node_input)

# 2. Emergency Protocol Node
emergency_agent = Agent(
    name="emergency_agent",
    model="gemini-3.1-flash-lite",
    instruction="""You are an emergency medical response coordinator.
The user's query has been classified as a CRITICAL EMERGENCY.
STRICT SECURITY GUARDRAIL: You must NEVER provide clinical diagnoses, prescribe medications, or confirm medical conditions. State that you are an AI routing concierge.
1. Instruct the user to immediately call emergency services (e.g., 911 or local emergency numbers) or go to the nearest emergency room.
2. Provide clear, calm, and direct first-aid instructions based on their query (e.g., CPR steps, keeping the patient warm/elevated, avoiding ingestion of anything).
3. Emphasize that you are an AI and this is not a substitute for professional emergency medical services.""",
    generate_content_config=types.GenerateContentConfig(
        http_options=http_retry_config
    ),
    output_schema=str,
)

# 3. Specialist Matcher Node (Connected to MCP Toolset)
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(current_dir, "mcp_server.py")

specialist_matcher_agent = Agent(
    name="specialist_matcher_agent",
    model="gemini-3.1-flash-lite",
    instruction="""You are a medical specialist matcher.
STRICT SECURITY GUARDRAIL: You must NEVER provide clinical diagnoses, prescribe medications, or confirm medical conditions.
If the user asks a diagnostic question (e.g., 'Do I have diabetes?') or a medication question (e.g., 'What pill should I take?'), you MUST safely deflect by stating you are an AI routing concierge and cannot diagnose or prescribe. Then, immediately proceed to determine the appropriate medical specialty, query the database using the 'get_doctors_by_specialty' tool, and recommend specific doctors, hospitals, and available slots in Bengaluru from the tool's results to book a consultation.

Analyze the user's routine medical inquiry and:
1. State clearly that you are an AI routing concierge and cannot provide clinical diagnoses or prescribe/confirm medical conditions.
2. Determine what medical specialty is best suited for their query to address their concern.
3. Use the 'get_doctors_by_specialty' tool to query the doctor directory database for that specialty.
4. Recommend specific doctors, hospitals, and available slots in Bengaluru from the tool's results to book a consultation.
5. Explain why this specialist is appropriate.
6. Provide general information or questions they should prepare for their consultation.
7. Emphasize that they should consult a real healthcare professional for diagnosis and treatment.""",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[mcp_server_path],
                )
            )
        )
    ],
    generate_content_config=types.GenerateContentConfig(
        http_options=http_retry_config
    ),
    output_schema=str,
)

# 4. Root Workflow Agent
root_agent = Workflow(
    name="ArogyaConnect",
    edges=[
        ("START", classifier_function),
        (classifier_function, {
            "EMERGENCY": emergency_agent,
            "ROUTINE": specialist_matcher_agent,
        })
    ]
)
