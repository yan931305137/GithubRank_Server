import requests
from typing import Dict, Any

from info_service.config.evaluate_config import (
    COMMITS_WEIGHT, PRS_WEIGHT, ISSUES_WEIGHT,
    STARS_WEIGHT, FOLLOWERS_WEIGHT, TOTAL_WEIGHT_BASE,
    COMMITS_MEDIAN, PRS_MEDIAN, ISSUES_MEDIAN,
    STARS_MEDIAN, FOLLOWERS_MEDIAN
)
from info_service.config.github_config import GITHUB_REPOS_URL, GITHUB_USER_URL
from info_service.config.github_token_config import Config
from info_service.utils.logger_utils import logger
from info_service.utils.agent_utils import get_random_user_agent


def evaluate_github_user(username: str, previous_score: float = 5.0) -> Dict[str, Any]:
    """
    评估GitHub用户的活跃度并返回相关数据

    Args:
        username: GitHub用户名
        previous_score: 上一次的评分，用于平滑处理

    Returns:
        包含用户活跃度得分和用户名的字典

    Raises:
        Exception: 当API请求失败时抛出异常
    """
    try:
        session = requests.Session()
        headers = {
            'User-Agent': get_random_user_agent(),
            'Authorization': f'token {Config.token}'
        } if Config.token else {'User-Agent': get_random_user_agent()}

        # 获取用户的基本信息
        user_url = GITHUB_USER_URL.format(username=username)
        user_response = session.get(user_url, headers=headers, verify=False, timeout=30)
        user_response.raise_for_status()
        user_data = user_response.json()

        # 获取用户的仓库信息
        repos_url = GITHUB_REPOS_URL.format(username=username)
        repos_response = session.get(repos_url, headers=headers, verify=False, timeout=30)
        repos_response.raise_for_status()
        repos_data = repos_response.json()

        total_commits = 0
        total_forks = 0
        total_issues = 0
        total_prs = 0
        total_stars = 0

        for repo in repos_data:
            total_forks += repo.get('forks_count', 0)
            total_stars += repo.get('stargazers_count', 0)

            # 获取每个仓库的提交数
            commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits"
            commits_response = session.get(commits_url, headers=headers, verify=False, timeout=30)
            commits_response.raise_for_status()
            total_commits += len(commits_response.json())

            # 获取每个仓库的拉取请求数
            prs_url = f"https://api.github.com/repos/{username}/{repo['name']}/pulls?state=all"
            prs_response = session.get(prs_url, headers=headers, verify=False, timeout=30)
            prs_response.raise_for_status()
            total_prs += len(prs_response.json())

            # 获取每个仓库的问题数
            issues_url = f"https://api.github.com/repos/{username}/{repo['name']}/issues?state=all"
            issues_response = session.get(issues_url, headers=headers, verify=False, timeout=30)
            issues_response.raise_for_status()
            total_issues += len(issues_response.json())

        # 计算用户的活跃度排名
        rank = (
                       COMMITS_WEIGHT * (total_commits / (COMMITS_MEDIAN if COMMITS_MEDIAN > 0 else 1)) +
                       PRS_WEIGHT * (total_prs / (PRS_MEDIAN if PRS_MEDIAN > 0 else 1)) +
                       ISSUES_WEIGHT * (total_issues / (ISSUES_MEDIAN if ISSUES_MEDIAN > 0 else 1)) +
                       STARS_WEIGHT * (total_stars / (STARS_MEDIAN if STARS_MEDIAN > 0 else 1)) +
                       FOLLOWERS_WEIGHT * (
                                   user_data.get('followers', 0) / (FOLLOWERS_MEDIAN if FOLLOWERS_MEDIAN > 0 else 1))
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
        raise  # 重新抛出异常以便外部捕获
