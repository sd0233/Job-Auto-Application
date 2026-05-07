import yaml

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def filter_jobs(jobs: list, existing_keys: set) -> list:
    config = load_config()
    exclude = [kw.lower() for kw in config["filters"]["exclude_keywords"]]
    filtered = []

    for job in jobs:
        # Skip already applied
        if job.get("job_key") in existing_keys:
            continue

        # Skip excluded keywords
        title_lower = job.get("title", "").lower()
        desc_lower  = job.get("description", "").lower()
        combined    = title_lower + " " + desc_lower

        if any(kw in combined for kw in exclude):
            continue

        filtered.append(job)

    return filtered