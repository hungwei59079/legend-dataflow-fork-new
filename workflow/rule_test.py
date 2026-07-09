import argparse
import subprocess
import sys
import re

def summarize_items(item_list, max_display=2):
    """
    Flattens comma-separated lines and truncates the list if it exceeds 
    max_display, providing a clean summary for verbose Snakemake outputs.
    """
    flattened = []
    for line in item_list:
        # Split by comma and strip whitespace to isolate individual files
        flattened.extend([item.strip() for item in line.split(',') if item.strip()])
    
    if not flattened:
        return "None"
        
    if len(flattened) <= max_display:
        return ', '.join(flattened)
        
    return f"{flattened[0]}, {flattened[1]}\n   ... (+ {len(flattened) - max_display} more items)"

def parse_snakemake_output(output_text):
    """
    Parses the dry-run output from Snakemake and extracts 
    rules, inputs, outputs, and scripts.
    """
    lines = output_text.splitlines()
    steps = []
    current_step = None
    current_block = None
    
    known_keys = [
        "input:", "output:", "log:", "jobid:", "wildcards:", 
        "resources:", "params:", "benchmark:", "reason:", 
        "priority:", "threads:", "script:", "shell:", "conda:"
    ]
    
    # State machine to parse snakemake text output
    for line in lines:
        stripped = line.strip()
        
        # Blank lines separate rule properties from the actual shell command in `-p` output
        if not stripped:
            if current_step and current_block in ["input", "output", "ignore"]:
                current_block = "shell"
            continue
            
        # Detect new rule
        if stripped.startswith("rule ") or stripped.startswith("localrule "):
            if current_step:
                steps.append(current_step)
            rule_name = stripped.replace("rule ", "").replace("localrule ", "").replace(":", "")
            current_step = {"rule": rule_name, "input": [], "output": [], "script": []}
            current_block = None
            continue
            
        # Job statistics table signals the end of the DAG breakdown
        if stripped.startswith("Job stats:"):
            if current_step:
                steps.append(current_step)
                current_step = None
            continue
        
        # Inside a rule block
        if current_step:
            is_key = False
            for key in known_keys:
                if stripped.startswith(key):
                    is_key = True
                    if key.startswith("input"):
                        current_block = "input"
                        val = stripped.replace(key, "").strip()
                        if val: current_step["input"].append(val)
                    elif key.startswith("output"):
                        current_block = "output"
                        val = stripped.replace(key, "").strip()
                        if val: current_step["output"].append(val)
                    else:
                        current_block = "ignore"
                    break
            
            if not is_key:
                # Continuation of input/output
                if current_block in ["input", "output"]:
                    current_step[current_block].append(stripped)
                # Raw text after blank lines or not matching anything (likely the shell command)
                elif current_block == "shell" or (current_block == "ignore" and not line.startswith("        ")):
                    current_step["script"].append(stripped)
                
    if current_step:
        steps.append(current_step)
        
    return steps

def expand_files(item_lines):
    """
    Flattens a list of possibly comma-separated lines into a set of the
    individual file paths they contain.
    """
    files = set()
    for line in item_lines:
        for item in line.split(','):
            item = item.strip()
            if item:
                files.add(item)
    return files

def compute_job_depths(steps):
    """
    Reconstructs the dependency DAG from each job's input/output files and
    returns the topological "stage" of every job (aligned with `steps`).

    A job's depth is the longest chain of producing jobs leading into it:
    a job whose inputs all pre-exist (no scheduled job produces them, e.g. raw
    tier files) is stage 0; a job that consumes another job's output is one
    stage deeper than its deepest producer. The job-level graph is guaranteed
    acyclic by Snakemake, so this is always well defined even though the
    rule-aggregated view can look cyclic.
    """
    job_inputs = [expand_files(step.get('input', [])) for step in steps]
    job_outputs = [expand_files(step.get('output', [])) for step in steps]

    # Map each produced file -> index of the (single) job that produces it.
    producer = {}
    for idx, outs in enumerate(job_outputs):
        for f in outs:
            producer[f] = idx

    depths = [None] * len(steps)
    in_progress = [False] * len(steps)

    def depth_of(idx):
        if depths[idx] is not None:
            return depths[idx]
        if in_progress[idx]:
            # Defensive guard; a valid Snakemake job DAG has no cycles.
            return 0
        in_progress[idx] = True
        d = 0
        for f in job_inputs[idx]:
            p = producer.get(f)
            if p is not None and p != idx:
                d = max(d, depth_of(p) + 1)
        in_progress[idx] = False
        depths[idx] = d
        return d

    for idx in range(len(steps)):
        depth_of(idx)
    return depths

def aggregate_steps(steps, depths):
    """
    Combines steps that run the same rule, merging their inputs and outputs,
    and deduplicating them. Keeps a count of how many jobs the rule spawns and
    the range of dependency stages those jobs occupy.
    """
    aggregated = []
    rule_map = {}

    for step, depth in zip(steps, depths):
        rule_name = step.get('rule', 'unknown')

        # Combine the script array into a single string
        script_text = " ".join(step.get('script', [])) if step.get('script') else 'None'

        if rule_name not in rule_map:
            rule_data = {
                'rule': rule_name,
                'input': set(),
                'output': set(),
                'script': script_text, # Just keep the first variant to avoid clutter
                'count': 0,
                'min_depth': depth,
                'max_depth': depth,
            }
            rule_map[rule_name] = rule_data
            aggregated.append(rule_data)

        rule_data = rule_map[rule_name]
        rule_data['count'] += 1
        rule_data['min_depth'] = min(rule_data['min_depth'], depth)
        rule_data['max_depth'] = max(rule_data['max_depth'], depth)

        for item_line in step.get('input', []):
            rule_data['input'].add(item_line)

        for item_line in step.get('output', []):
            rule_data['output'].add(item_line)

    # Convert sets back to lists
    for rule_data in aggregated:
        rule_data['input'] = sorted(list(rule_data['input']))
        rule_data['output'] = sorted(list(rule_data['output']))

    # Order rules chronologically: earliest stage first, then by the stage the
    # rule finishes, then by name for a stable, deterministic tie-break.
    aggregated.sort(key=lambda r: (r['min_depth'], r['max_depth'], r['rule']))

    return aggregated

def main():
    parser = argparse.ArgumentParser(description="Evaluate Snakemake dependencies for a target.")
    parser.add_argument("target", help="Target file (e.g. all-l200-p03-r001-phy-skm.gen)")
    args = parser.parse_args()

    cmd = [
        "snakemake", 
        "--profile", "workflow/profiles/default", 
        "-n", "-p",
        args.target
    ]
    
    print(f"Resolving DAG for target: {args.target}...\n")
    try:
        # Run snakemake dry-run
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error invoking Snakemake:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Snakemake not found. Please make sure your virtual environment (.venv) is activated first!")
        sys.exit(1)
        
    steps = parse_snakemake_output(result.stdout)
    
    if not steps:
        print("No steps needed. The target might already be fully built, or the configuration failed.")
        sys.exit(0)
    
    depths = compute_job_depths(steps)
    aggregated = aggregate_steps(steps, depths)

    for i, step in enumerate(aggregated, start=1):
        print("-" * 40)
        count = step.get('count', 1)
        min_d, max_d = step.get('min_depth', 0), step.get('max_depth', 0)
        stage = f"stage {min_d}" if min_d == max_d else f"stages {min_d}-{max_d}"
        print(f"Step {i} [{stage}]: rule {step.get('rule', 'unknown')} ({count} jobs)")
        
        # Print summarized Inputs
        inputs = summarize_items(step.get('input', []))
        print(f"Input: {inputs}")
        
        # Print summarized Outputs
        outputs = summarize_items(step.get('output', []))
        print(f"Output: {outputs}")
        
        # Print Script/Shell
        script_or_shell = step.get('script')
        print(f"Script/Shell: {script_or_shell if script_or_shell else 'None'}")

    print("-" * 40)
    print(f"\nTotal unique rules scheduled: {len(aggregated)}")
    print(f"Total jobs scheduled: {len(steps)}")

if __name__ == "__main__":
    main()