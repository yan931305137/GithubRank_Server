# 导入所需的库
import requests
from typing import Dict, Any, Tuple

from info_service.config.evaluate_config import COMMITS_WEIGHT, PRS_WEIGHT, ISSUES_WEIGHT, REVIEWS_WEIGHT, STARS_WEIGHT, \
    FOLLOWERS_WEIGHT, TOTAL_WEIGHT_BASE, COMMITS_MEDIAN, PRS_MEDIAN, ISSUES_MEDIAN, REVIEWS_MEDIAN, STARS_MEDIAN, \
    FOLLOWERS_MEDIAN, THRESHOLDS, LEVELS
from info_service.config.github_config import GITHUB_COMMITS_URL, GITHUB_USER_URL, GITHUB_REPOS_URL


def fetch_data(url: str, token: str) -> Dict[str, Any]:
    """
    从GitHub API获取数据
    
    Args:
        url: API请求地址
        token: GitHub访问令牌
    
    Returns:
        返回API响应的JSON数据
        
    Raises:
        Exception: 当API请求失败时抛出异常
    """
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"请求数据时出错: {response.status_code} - {response.text}")
    return response.json()


def get_user_commits(username: str, repo_name: str, token: str) -> int:
    """
    获取用户在指定仓库的提交数
    
    Args:
        username: GitHub用户名
        repo_name: 仓库名
        token: GitHub访问令牌
    
    Returns:
        返回提交总数
    """
    commits_url = GITHUB_COMMITS_URL.format(username=username, repo=repo_name)
    commits_response = fetch_data(commits_url, token)
    return len(commits_response)


def get_github_user_data(username: str, token: str) -> Dict[str, Any]:
    """
    获取GitHub用户的基本数据
    
    Args:
        username: GitHub用户名
        token: GitHub访问令牌
    
    Returns:
        返回包含用户数据的字典,包括:
        - stars: 获得的star数
        - followers: 关注者数量
        - user_commits: 用户提交数
        - total_commits: 总提交数
        - contribution_degree: 贡献度
    """
    user_url = GITHUB_USER_URL.format(username=username)
    repos_url = GITHUB_REPOS_URL.format(username=username)
    
    user_data = fetch_data(user_url, token)
    repos_data = fetch_data(repos_url, token)

    stars = sum(repo.get('stargazers_count', 0) for repo in repos_data)
    total_commits = sum(repo.get('size', 0) for repo in repos_data)

    user_commits = sum(get_user_commits(username, repo['name'], token) for repo in repos_data)
    contribution_degree = (user_commits / total_commits * 10) if total_commits > 0 else 0

    return {
        'stars': stars,
        'followers': user_data.get('followers', 0),
        'user_commits': user_commits,
        'total_commits': total_commits,
        'contribution_degree': contribution_degree
    }


def get_user_activity(username: str, token: str) -> Tuple[int, int, int]:
    """
    获取用户的活动数据
    
    Args:
        username: GitHub用户名
        token: GitHub访问令牌
    
    Returns:
        返回包含(PR数, Issue数, Review数)的元组
    """
    repos_url = GITHUB_REPOS_URL.format(username=username)
    repos_data = fetch_data(repos_url, token)
    prs_count, issues_count, reviews_count = 0, 0, 0

    for repo in repos_data:
        repo_name = repo['name']
        # 使用完整的 API URL
        prs_url = f'https://api.github.com/repos/{username}/{repo_name}/pulls?state=all'
        issues_url = f'https://api.github.com/repos/{username}/{repo_name}/issues?state=all'
        
        prs_response = fetch_data(prs_url, token)
        issues_response = fetch_data(issues_url, token)
        
        prs_count += len(prs_response)
        issues_count += len([issue for issue in issues_response if 'pull_request' not in issue])

        # 获取每个PR的评审数据
        for pr in prs_response:
            reviews_url = f'https://api.github.com/repos/{username}/{repo_name}/pulls/{pr["number"]}/reviews'
            reviews_response = fetch_data(reviews_url, token)
            reviews_count += len(reviews_response)

    return prs_count, issues_count, reviews_count


def calculate_rank(params: Dict[str, Any]) -> Dict[str, float]:
    """
    计算用户的GitHub活跃度排名
    
    Args:
        params: 包含用户各项指标的字典
    
    Returns:
        返回包含等级和百分位的字典
    """
    commits = params['user_commits']
    total_commits = params['total_commits']
    stars = params['stars']
    followers = params['followers']

    # 计算综合得分
    rank = 1 - (
            COMMITS_WEIGHT * (commits / (COMMITS_MEDIAN if total_commits > 0 else 1)) +
            PRS_WEIGHT * (params['prs'] / PRS_MEDIAN) +
            ISSUES_WEIGHT * (params['issues'] / ISSUES_MEDIAN) +
            REVIEWS_WEIGHT * (params['reviews'] / REVIEWS_MEDIAN) +
            STARS_WEIGHT * (stars / STARS_MEDIAN) +
            FOLLOWERS_WEIGHT * (followers / FOLLOWERS_MEDIAN)
    ) / TOTAL_WEIGHT_BASE

    # 计算百分位和等级
    percentile = rank * 100
    level = LEVELS[next(i for i, t in enumerate(THRESHOLDS) if percentile <= t)]

    return {'level': level, 'percentile': percentile}


# 主程序入口
def evaluate(username, token):
    try:
        # 获取用户数据
        user_data = get_github_user_data(username, token)
        prs_count, issues_count, reviews_count = get_user_activity(username, token)

        # 整理评分参数
        params = {
            'user_commits': user_data['user_commits'],
            'total_commits': user_data['total_commits'],
            'prs': prs_count,
            'issues': issues_count,
            'reviews': reviews_count,
            'stars': user_data['stars'],
            'followers': user_data['followers'],
            'contribution_degree': user_data['contribution_degree']
        }

        # 计算排名
        rank_info = calculate_rank(params)

        # 组织输出结果
        result = {
            "commits": str(user_data['user_commits']),
            "contributions": str(user_data['contribution_degree']),
            "issues": str(issues_count),
            "prs": str(prs_count),
            "rank": rank_info['level'],
            "stars": str(user_data['stars']),
            "username": username
        }

        return result  # 输出结果

    except Exception as e:
        logger.info(e)  # 输出错误信息
