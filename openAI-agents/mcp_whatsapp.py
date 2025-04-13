import asyncio
import os
import shutil # Keep for potential future path checks, though the npx check is removed.

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio

# Define the path to your WhatsApp MCP server command and directory
# IMPORTANT: Replace these placeholders with the actual paths from your Claude config
# or make them configurable (e.g., via environment variables or command-line args).
WHATSAPP_SERVER_COMMAND = "/Volumes/WDB_1TB/Documents/GitHub/whatsapp-mcp/venv/bin/uv" # From Claude config
WHATSAPP_SERVER_ARGS = [
    "--directory",
    "/Volumes/WDB_1TB/Documents/GitHub/whatsapp-mcp/whatsapp-mcp-server", # From Claude config
    "run",
    "main.py" # The script that runs mcp.run(transport='stdio')
]
WHATSAPP_SERVER_WORKING_DIR = "/Volumes/WDB_1TB/Documents/GitHub/whatsapp-mcp/whatsapp-mcp-server" # Needed for MCPServerStdio if using relative paths or if the script depends on CWD

async def run(mcp_server: MCPServer):
    """Runs example interactions with the WhatsApp agent."""
    agent = Agent(
        # --- Updated Agent Instructions ---
        name="WhatsApp Assistant",
        instructions=(
            "You are a helpful assistant integrated with WhatsApp. "
            "Use the available tools to interact with WhatsApp on behalf of the user. "
            "You can search contacts, list chats, read messages, send messages, send files, "
            "and download media. Be precise with recipient identifiers (phone numbers or JIDs)."
        ),
        mcp_servers=[mcp_server],
    )

    # --- Example Interactions (Replace with your desired tests) ---

    # CONFIG
    example_1 = False # List recent chats
    example_2 = False # Search for a contact
    example_3 = False # Send a message (IMPORTANT: Replace placeholder)
    example_4 = True # List messages in a specific chat (requires JID)


    # Example 1: List recent chats
    if example_1:
        message_list_chats = "List my 5 most recent WhatsApp chats."
        print(f"\nRunning: {message_list_chats}")
        try:
            result = await Runner.run(starting_agent=agent, input=message_list_chats)
            print("Result:", result.final_output if result else "No result")
        except Exception as e:
            print(f"Error running '{message_list_chats}': {e}")

    # Example 2: Search for a contact (replace 'John Doe' with a real name in your contacts)
    if example_2:
        contact_name_to_search = "Maiti" # Replace with a name likely in your contacts
        message_search_contact = f"Search for a WhatsApp contact named '{contact_name_to_search}'."
        print(f"\nRunning: {message_search_contact}")
        try:
            result = await Runner.run(starting_agent=agent, input=message_search_contact)
            print("Result:", result.final_output if result else "No result")
        except Exception as e:
            print(f"Error running '{message_search_contact}': {e}")


    # Example 3: Send a message (IMPORTANT: Replace placeholder)
    # Make sure the recipient exists and you have permissions.
    # Use a phone number (e.g., "1234567890") or a JID (e.g., "1234567890@s.whatsapp.net")

    if example_3:
        recipient_identifier = "+34 661 195 723" # <-- *** CHANGE THIS VALID_PHONE_OR_JID***
        if recipient_identifier == "REPLACE_WITH_VALID_PHONE_OR_JID":
            print("\nSkipping send message example: Please replace 'REPLACE_WITH_VALID_PHONE_OR_JID' in the code.")
        else:
            message_send = f"Send a message to '{recipient_identifier}' saying 'Hello from the OpenAI Agent SDK!'"
            print(f"\nRunning: {message_send}")
            try:
                result = await Runner.run(starting_agent=agent, input=message_send)
                print("Result:", result.final_output if result else "No result")
            except Exception as e:
                print(f"Error running '{message_send}': {e}")

    # Example 4: Ask about messages in a specific chat (Requires knowing a Chat JID)
    if example_4:
        chat_jid_to_query = "+34 661 195 723"
        if chat_jid_to_query == "REPLACE_WITH_VALID_CHAT_JID@g.us":
            print("\nSkipping list messages example: Please replace 'REPLACE_WITH_VALID_CHAT_JID@g.us' in the code.")
        else:
            message_list_msgs = f"Show me the last 3 messages in the chat with JID {chat_jid_to_query}."
            print(f"\nRunning: {message_list_msgs}")
            try:
                result = await Runner.run(starting_agent=agent, input=message_list_msgs)
                print("Result:", result.final_output if result else "No result")
            except Exception as e:
                print(f"Error running '{message_list_msgs}': {e}")


async def main():
    """Sets up and runs the MCP server connection and agent interactions."""

    # --- Check if the server command exists ---
    # Basic check, might need refinement based on your system/setup
    if not shutil.which(WHATSAPP_SERVER_COMMAND) and not os.path.exists(WHATSAPP_SERVER_COMMAND):
         raise RuntimeError(f"WhatsApp server command not found or not executable: {WHATSAPP_SERVER_COMMAND}")
    if not os.path.isdir(WHATSAPP_SERVER_WORKING_DIR):
         raise RuntimeError(f"WhatsApp server working directory not found: {WHATSAPP_SERVER_WORKING_DIR}")


    # --- Configure MCPServerStdio for WhatsApp Server ---
    async with MCPServerStdio(
        name="WhatsApp Server via Python", # Updated name
        params={
            "command": WHATSAPP_SERVER_COMMAND, # Command from Claude config
            "args": WHATSAPP_SERVER_ARGS,       # Args from Claude config
            # Specify the working directory if the server script needs it
            "cwd": WHATSAPP_SERVER_WORKING_DIR,
        },
        cache_tools_list=True
        # Optional: Increase timeout if the server takes longer to start
        # startup_timeout_seconds=30,
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP WhatsApp Example", trace_id=trace_id):
            print(f"Attempting to connect to WhatsApp MCP server...")
            print(f"Command: {WHATSAPP_SERVER_COMMAND}")
            print(f"Args: {' '.join(WHATSAPP_SERVER_ARGS)}")
            print(f"CWD: {WHATSAPP_SERVER_WORKING_DIR}")
            print(f"\nView trace (if tracing is configured): https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

            # Wait briefly for the server to potentially initialize if needed
            await asyncio.sleep(2) # Adjust if necessary

            await run(server)


if __name__ == "__main__":
    # --- Removed the npx check ---
    # Now runs the main async function
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")