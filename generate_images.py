#!/usr/bin/python3

import asyncio
import os
import re
import json
from datetime import datetime, timedelta

import aiohttp

from github_stats import Stats

REPO_STATS_PATH = "generated/repo_stats.json"

################################################################################
# Helper Functions
################################################################################


def generate_output_folder() -> None:
    """
    Create the output folder if it does not already exist
    """
    if not os.path.isdir("generated"):
        os.mkdir("generated")


def load_repo_stats():
    if os.path.exists(REPO_STATS_PATH):
        with open(REPO_STATS_PATH, "r") as f:
            return json.load(f)
    return {}


def save_repo_stats(data):
    generate_output_folder()
    with open(REPO_STATS_PATH, "w") as f:
        json.dump(data, f, indent=2)


################################################################################
# Individual Image Generation Functions
################################################################################


async def generate_overview(s: Stats) -> None:
    """
    Generate an SVG badge with summary statistics
    :param s: Represents user's GitHub statistics
    """
    with open("templates/overview.svg", "r") as f:
        output = f.read()

    output = re.sub("{{ name }}", await s.name, output)
    output = re.sub("{{ stars }}", f"{await s.stargazers:,}", output)
    output = re.sub("{{ forks }}", f"{await s.forks:,}", output)
    output = re.sub("{{ contributions }}", f"{await s.total_contributions:,}", output)
    changed = (await s.lines_changed)[0] + (await s.lines_changed)[1]
    output = re.sub("{{ lines_changed }}", f"{changed:,}", output)
    output = re.sub("{{ views }}", f"{await s.views:,}", output)
    output = re.sub("{{ repos }}", f"{len(await s.repos):,}", output)

    generate_output_folder()
    with open("generated/overview.svg", "w") as f:
        f.write(output)


async def generate_languages(s: Stats) -> None:
    """
    Generate an SVG badge with summary languages used
    :param s: Represents user's GitHub statistics
    """
    with open("templates/languages.svg", "r") as f:
        output = f.read()

    progress = ""
    lang_list = ""
    sorted_languages = sorted(
        (await s.languages).items(), reverse=True, key=lambda t: t[1].get("size")
    )
    delay_between = 150
    for i, (lang, data) in enumerate(sorted_languages):
        color = data.get("color")
        color = color if color is not None else "#000000"
        progress += (
            f'<span style="background-color: {color};'
            f'width: {data.get("prop", 0):0.3f}%;" '
            f'class="progress-item"></span>'
        )
        lang_list += f"""
<li style="animation-delay: {i * delay_between}ms;">
<svg xmlns="http://www.w3.org/2000/svg" class="octicon" style="fill:{color};"
viewBox="0 0 16 16" version="1.1" width="16" height="16"><path
fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path></svg>
<span class="lang">{lang}</span>
<span class="percent">{data.get("prop", 0):0.2f}%</span>
</li>

"""

    output = re.sub(r"{{ progress }}", progress, output)
    output = re.sub(r"{{ lang_list }}", lang_list, output)

    generate_output_folder()
    with open("generated/languages.svg", "w") as f:
        f.write(output)


async def fetch_repo_traffic(s: Stats, repo: str):
    clones = await s.queries.query_rest(f"/repos/{repo}/traffic/clones")
    views = await s.queries.query_rest(f"/repos/{repo}/traffic/views")
    clone_count = sum([c.get("count", 0) for c in clones.get("clones", [])])
    view_count = sum([v.get("count", 0) for v in views.get("views", [])])
    return clone_count, view_count


async def fetch_repo_stars(s: Stats, repo: str):
    repo_info = await s.queries.query_rest(f"/repos/{repo}")
    return repo_info.get("stargazers_count", 0)


def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")


async def generate_repo_image(repo: str, stats: dict):
    template_path = "templates/repo_status.svg"
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"SVG template not found: {template_path}")
    with open(template_path, "r") as f:
        output = f.read()
    output = output.replace("{{ repo }}", repo)
    output = output.replace("{{ stars }}", str(stats.get("stars", 0)))
    output = output.replace("{{ clones }}", str(stats.get("clones", 0)))
    output = output.replace("{{ views }}", str(stats.get("views", 0)))
    generate_output_folder()
    safe_repo = repo.replace("/", "__")
    with open(f"generated/{safe_repo}_status.svg", "w") as f:
        f.write(output)


async def update_and_generate_repo_stats(s: Stats):
    repo_stats = load_repo_stats()
    today = today_str()
    # 调试输出
    all_repos = await s.repos
    print("All repos to be processed:", all_repos)
    if not all_repos:
        print("No repositories found for the user. Please check ACCESS_TOKEN permissions and EXCLUDED settings.")
    for repo in all_repos:
        repo = str(repo)
        if repo not in repo_stats:
            repo_stats[repo] = {"stars": 0, "clones": 0, "views": 0, "history": {}}
            is_first = True
        else:
            is_first = False
        stats = repo_stats[repo]
        stars = await fetch_repo_stars(s, repo)
        clones, views = await fetch_repo_traffic(s, repo)
        if is_first:
            stats["stars"] = stars
            stats["clones"] = clones
            stats["views"] = views
            stats["history"][today] = {"stars": stars, "clones": clones, "views": views}
        else:
            delta_stars = max(0, stars - stats.get("last_stars", stats["stars"]))
            delta_clones = max(0, clones - stats.get("last_clones", stats["clones"]))
            delta_views = max(0, views - stats.get("last_views", stats["views"]))
            stats["stars"] += delta_stars
            stats["clones"] += delta_clones
            stats["views"] += delta_views
            stats["history"][today] = {
                "stars": delta_stars,
                "clones": delta_clones,
                "views": delta_views,
            }
        stats["last_stars"] = stars
        stats["last_clones"] = clones
        stats["last_views"] = views
        await generate_repo_image(repo, stats)
    save_repo_stats(repo_stats)


################################################################################
# Main Function
################################################################################


async def main() -> None:
    """
    Generate all badges
    """
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        # access_token = os.getenv("GITHUB_TOKEN")
        raise Exception("A personal access token is required to proceed!")
    user = os.getenv("GITHUB_ACTOR")
    if user is None:
        raise RuntimeError("Environment variable GITHUB_ACTOR must be set.")
    exclude_repos = os.getenv("EXCLUDED")
    excluded_repos = (
        {x.strip() for x in exclude_repos.split(",")} if exclude_repos else None
    )
    exclude_langs = os.getenv("EXCLUDED_LANGS")
    excluded_langs = (
        {x.strip() for x in exclude_langs.split(",")} if exclude_langs else None
    )
    # Convert a truthy value to a Boolean
    raw_ignore_forked_repos = os.getenv("EXCLUDE_FORKED_REPOS")
    ignore_forked_repos = (
        not not raw_ignore_forked_repos
        and raw_ignore_forked_repos.strip().lower() != "false"
    )
    async with aiohttp.ClientSession() as session:
        s = Stats(
            user,
            access_token,
            session,
            exclude_repos=excluded_repos,
            exclude_langs=excluded_langs,
            ignore_forked_repos=ignore_forked_repos,
        )
        repos = await s.repos
        print("实际统计的仓库数量:", len(repos))
        print("实际统计的仓库:", repos)
        await asyncio.gather(
            generate_languages(s),
            generate_overview(s),
            update_and_generate_repo_stats(s)
        )


if __name__ == "__main__":
    asyncio.run(main())
