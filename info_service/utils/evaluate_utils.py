import requests
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from info_service.config.evaluate_config import (
    COMMITS_WEIGHT, PRS_WEIGHT, ISSUES_WEIGHT,
    STARS_WEIGHT, FOLLOWERS_WEIGHT, TOTAL_WEIGHT_BASE,
    COMMITS_MEDIAN, PRS_MEDIAN, ISSUES_MEDIAN,
    STARS_MEDIAN, FOLLOWERS_MEDIAN, PROJECT_IMPORTANCE_WEIGHT, TOTAL_PROJECT_IMPORTANCE_MEDIAN,
    TOTAL_CONTRIBUTION_MEDIAN, DEVELOPER_CONTRIBUTION_WEIGHT
)
from info_service.config.github_config import GITHUB_REPOS_URL, GITHUB_USER_URL
from info_service.config.github_token_config import Config
from info_service.utils.logger_utils import logger
from info_service.utils.agent_utils import get_random_user_agent


def fetch_data(session, url, headers):
    """发送 HTTP 请求并获取数据"""
    try:
        response = session.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return []  # 返回空列表，避免中断其他请求


def evaluate_github_user(username: str, previous_score: float = 5.0) -> Dict[str, Any]:
    try:
        session = requests.Session()
        headers = {
            'User-Agent': get_random_user_agent(),
            'Authorization': f'token {Config.token}'
        } if Config.token else {'User-Agent': get_random_user_agent()}

        # 获取用户的基本信息
        user_url = GITHUB_USER_URL.format(username=username)
        user_data = fetch_data(session, user_url, headers)

        # 获取用户的仓库信息
        repos_url = GITHUB_REPOS_URL.format(username=username)
        repos_data = fetch_data(session, repos_url, headers)

        total_commits = 0
        total_forks = 0
        total_issues = 0
        total_prs = 0
        total_stars = 0
        total_project_importance = 0  # 项目重要性
        total_contribution = 0  # 开发者贡献度

        # 使用 ThreadPoolExecutor 实现并行请求
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for repo in repos_data:
                repo_name = repo['name']
                repo_url = f"https://api.github.com/repos/{username}/{repo_name}"

                # 向每个仓库发起并行请求
                futures.append(executor.submit(fetch_data, session, f"{repo_url}/commits", headers))
                futures.append(executor.submit(fetch_data, session, f"{repo_url}/pulls?state=all", headers))
                futures.append(executor.submit(fetch_data, session, f"{repo_url}/issues?state=all", headers))

            # 获取请求结果
            for future in as_completed(futures):
                data = future.result()
                if 'commits' in str(future):
                    total_commits += len(data)
                elif 'pulls' in str(future):
                    total_prs += len(data)
                elif 'issues' in str(future):
                    total_issues += len(data)

            # 计算其他数据
            for repo in repos_data:
                total_forks += repo.get('forks_count', 0)
                total_stars += repo.get('stargazers_count', 0)

                # 计算项目重要性：可以使用星标数、提交数、活跃度等来计算项目的重要性
                project_importance = repo.get('stargazers_count', 0) + repo.get('open_issues_count', 0)
                total_project_importance += project_importance

                # 计算开发者在该项目中的贡献度（例如提交数、PR数等）
                developer_contribution = (total_commits + total_prs + total_issues)
                total_contribution += developer_contribution

        # 计算用户的活跃度排名，增加项目重要性和开发者贡献度的权重
        rank = (
                       COMMITS_WEIGHT * (total_commits / (COMMITS_MEDIAN if COMMITS_MEDIAN > 0 else 1)) +
                       PRS_WEIGHT * (total_prs / (PRS_MEDIAN if PRS_MEDIAN > 0 else 1)) +
                       ISSUES_WEIGHT * (total_issues / (ISSUES_MEDIAN if ISSUES_MEDIAN > 0 else 1)) +
                       STARS_WEIGHT * (total_stars / (STARS_MEDIAN if STARS_MEDIAN > 0 else 1)) +
                       FOLLOWERS_WEIGHT * (
                               user_data.get('followers', 0) / (FOLLOWERS_MEDIAN if FOLLOWERS_MEDIAN > 0 else 1)) +
                       PROJECT_IMPORTANCE_WEIGHT * (total_project_importance / (
                   TOTAL_PROJECT_IMPORTANCE_MEDIAN if TOTAL_PROJECT_IMPORTANCE_MEDIAN > 0 else 1)) +
                       DEVELOPER_CONTRIBUTION_WEIGHT * (total_contribution / (
                   TOTAL_CONTRIBUTION_MEDIAN if TOTAL_CONTRIBUTION_MEDIAN > 0 else 1))
               ) / TOTAL_WEIGHT_BASE

        # 平滑处理
        smooth_factor = 0.8  # 平滑因子
        percentile = (smooth_factor * (rank * 100) + (1 - smooth_factor) * previous_score) / 30

        # 确保分数在0到10之间并保留一位小数
        percentile = round(max(0, min(percentile, 10)), 1)

        # 组织输出结果
        result = {
            "score": percentile
        }

        return result

    except Exception as e:
        logger.error(e)
        raise
