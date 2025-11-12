import requests
import os

# Load GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable is not set.")
    print("Please set it before running this script:")
    print("  export GITHUB_TOKEN='your_github_token_here'")
    exit(1)

login_url = "https://api.githubcopilot.com/mcp/session"
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/json"
}

login_response = requests.post(login_url, headers=headers)

print(f"Login response status: {login_response.status_code}")
print(login_response)
    # if login_response.status_code == 200:
    #     session_id = login_response.json().get('sessionId')
    # else:
    #     print(f"Session initiation failed: {login_response.status_code} - {login_response.text}")

    # return session_id



# # MCP server URL
# url = "https://api.githubcopilot.com/mcp"

# # Authentication details (update as required)
# headers = {
#     "Authorization": f"Bearer {GITHUB_TOKEN}",
#     "Accept": "application/json"
# }

# session_id = getsession_id()

# # Typical POST data structure; customize "inputs" or other required fields as needed
# tools_payload = {
#     "action": "getTools",
#     "limit": 40,
#     "sessionId": session_id  # Use the session ID from step 1
# }

# response = requests.post(url, headers=headers, json=tools_payload)


# # Check for a valid response
# if response.status_code == 200:
#     data = response.json()
#     # Assuming 'tools' is a key in the JSON, take first 40 tools
#     tools = data.get('tools', [])[:40]
#     print(tools)
# else:
#     print(f"Failed to fetch tools: {response.status_code} - {response.text}")
