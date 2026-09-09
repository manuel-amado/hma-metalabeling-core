import sys
import os
import subprocess
import datetime

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}': {e.stderr}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2 or sys.argv[1] != '--milestone':
        print("Usage: python git_auto_push.py --milestone")
        sys.exit(1)
        
    print("=== Nexus Protocol: Automated Milestone Push ===")
    
    # Add files
    run_command("git add Alpha_Sniper.mq5 AHMA_Math.mqh *.mq5 *.mqh")
    
    # Check if there are changes to commit
    status = run_command("git status --porcelain")
    if not status:
        print("No relevant changes detected. Skipping push.")
        return
        
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"build: Alpha_Sniper automated milestone push [{timestamp}]"
    
    print(f"Committing changes: {commit_msg}")
    run_command(f'git commit -m "{commit_msg}"')
    
    print("Pushing to remote...")
    try:
        run_command("git push origin HEAD")
        print("Push successful.")
    except Exception as e:
        print("Push failed. Authentication might be required or network is down.")

if __name__ == "__main__":
    main()
