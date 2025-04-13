import re

def get_next_run_id(base_dir):
    run_dirs = [d.name for d in base_dir.iterdir() if d.is_dir() and re.match(r"run_\d{3}", d.name)]
    if not run_dirs:
        return "run_001"
    run_nums = [int(re.search(r"\d{3}", d).group()) for d in run_dirs]
    next_run = max(run_nums) + 1
    return f"run_{next_run:03d}"