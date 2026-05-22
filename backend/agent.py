import os
import sys
from google.adk import Agent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from dotenv import load_dotenv

load_dotenv()

# Model is passed directly as a string in newer ADK versions

# Define the command to run the MCP server
mcp_server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
from mcp import StdioServerParameters

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[mcp_server_path]
        )
    )
)

github_card_agent = Agent(
    name="github_card_agent",
    instruction="""
    You are a GitHub profile analyst and dev card generator. 
    When a user gives you a GitHub username, you ALWAYS follow this exact sequence:
    1. Call 'scrape_github' with the username.
    2. Call 'analyze_profile' with the result from step 1.
    3. Call 'generate_card_html' with the username, the scraped data, and the analysis result.
    
    Never skip steps.
    After step 3 is complete, output ONLY the URL string returned by generate_card_html as your final text response. Do not include any other text or conversational filler.
    If the profile is private or doesn't exist, say so clearly.
    """,
    model="gemini-2.5-flash-lite",
    tools=[mcp_toolset]
)
