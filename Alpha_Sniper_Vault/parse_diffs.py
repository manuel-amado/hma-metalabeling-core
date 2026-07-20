import json
import re

log_path = r"C:\Users\Manuel\.gemini\antigravity\brain\cb6503f8-f051-41b7-ac20-8fa79020986e\.system_generated\logs\transcript.jsonl"
out_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\orchestrator_diffs.md"

with open(log_path, "r", encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out:
    out.write("# Orchestrator Changes History\n\n")
    for line in f:
        try:
            data = json.loads(line)
        except:
            continue
            
        step = data.get("step_index", 0)
        content = data.get("content", "")
        tool_calls = data.get("tool_calls", [])
        
        # Look at tool calls
        for call in tool_calls:
            if call.get("name") in ["multi_replace_file_content", "write_to_file"]:
                args = call.get("args", {})
                target = str(args.get("TargetFile", ""))
                if "HMA_ML_Orchestrator.mq5" in target:
                    out.write(f"## Step {step} - Tool Call: {call.get('name')}\n")
                    if "Instruction" in args:
                        out.write(f"**Instruction:** {args['Instruction']}\n")
                    if "Description" in args:
                        out.write(f"**Description:** {args['Description']}\n")
                    out.write("\n```json\n" + json.dumps(args, indent=2) + "\n```\n\n")
                    
        # Look at responses (CODE_ACTION)
        if data.get("type") == "CODE_ACTION" and "HMA_ML_Orchestrator.mq5" in content:
            out.write(f"## Step {step} - Tool Response\n")
            # Extract diff block
            diff_match = re.search(r'\[diff_block_start\](.*?)\[diff_block_end\]', content, re.DOTALL)
            if diff_match:
                out.write("```diff\n" + diff_match.group(1).strip() + "\n```\n\n")
            else:
                out.write("```\n" + content[:500] + "...\n```\n\n")
