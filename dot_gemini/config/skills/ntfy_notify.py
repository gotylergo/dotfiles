import sys
import json
import urllib.request
import urllib.error
import os

def main():
    # Read stdin
    try:
        input_data = sys.stdin.read()
        context = json.loads(input_data) if input_data else {}
    except Exception:
        context = {}

    conversation_id = context.get("conversationId", "unknown")
    workspace_paths = context.get("workspacePaths", [])
    
    # Read from environment variables (best practice for dotfiles)
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
    topic = os.environ.get("NTFY_TOPIC", "tylerj_agent_z3HqA5xCbSe0cDVr")
    
    if not topic:
        sys.stderr.write("NTFY_TOPIC environment variable is not set.\n")
        print("{}")
        return
        
    url = f"{server}/{topic}"
    
    workspace_info = ""
    if workspace_paths:
        workspace_info = f"Workspace: {os.path.basename(workspace_paths[0])}\n"
        
    tool_call = context.get("toolCall", {})
    if tool_call:
        # PreToolUse event (attention requests)
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        
        # Only notify for tools requiring attention
        if tool_name not in ["ask_question", "ask_permission", "run_command"]:
            print("{}")
            return
            
        priority = "high"
        
        if tool_name == "ask_question":
            title = "Antigravity: Question"
            tags = "question,eyes"
            questions = tool_args.get("questions", [])
            q_texts = [q.get("question", "") for q in questions if q.get("question")]
            message = f"{workspace_info}Conversation ID: {conversation_id}\n\nQuestions:\n" + "\n".join(q_texts)
            
        elif tool_name == "ask_permission":
            title = "Antigravity: Permission Request"
            tags = "lock,eyes"
            action = tool_args.get("Action", "")
            target = tool_args.get("Target", "")
            reason = tool_args.get("Reason", "")
            message = f"{workspace_info}Conversation ID: {conversation_id}\n\nPermission needed:\nAction: {action}\nTarget: {target}\nReason: {reason}"
            
        elif tool_name == "run_command":
            title = "Antigravity: Command Approval"
            tags = "warning,eyes"
            cmd = tool_args.get("CommandLine", "")
            message = f"{workspace_info}Conversation ID: {conversation_id}\n\nCommand:\n{cmd}"
            
        else:
            title = "Antigravity Needs Attention"
            tags = "eyes"
            message = f"{workspace_info}Conversation ID: {conversation_id}\nTool: {tool_name}"
    else:
        # Stop event (task termination)
        reason = context.get("reason", "unknown")
        error = context.get("error", "")
        
        if error:
            title = f"Antigravity Task Failed ({reason})"
            priority = "high"
            tags = "warning,fire"
        elif reason == "model_stop":
            title = "Antigravity Task Finished Successfully"
            priority = "default"
            tags = "heavy_check_mark,robot"
        else:
            title = f"Antigravity Task Stopped ({reason})"
            priority = "default"
            tags = "heavy_check_mark,robot"
            
        message = f"{workspace_info}Conversation ID: {conversation_id}\nReason: {reason}"
        if error:
            message += f"\nError: {error}"
            
    headers = {
        "X-Title": title,
        "X-Priority": priority,
        "X-Tags": tags,
    }
    
    req = urllib.request.Request(
        url,
        data=message.encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            pass
    except Exception as e:
        sys.stderr.write(f"Failed to send notification: {e}\n")
        
    # Write empty JSON to stdout as expected by hooks framework
    print("{}")

if __name__ == "__main__":
    main()
