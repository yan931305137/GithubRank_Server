import re

import cohere
import langid
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import urllib3

from info_service.config.cohere_config import CohereConfig
from info_service.config.github_token_config import Config
from info_service.utils.logger_utils import logger
from info_service.services.info_service import get_rank_data, save_user_data, \
    save_user_reops_data, save_user_total_info_data, save_user_tech_info_data, save_user_guess_nation_info_data, \
    save_user_summary_info_data, get_github_id, save_evaluate_info

from info_service.utils.agent_utils import get_random_user_agent
from info_service.config.github_config import GITHUB_USER_URL, GITHUB_REPOS_URL, GITHUB_EVENTS_URL, \
    GITHUB_CONTRIBUTORS_URL, GITHUB_COMMITS_URL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_paginated_data(url, headers, session):
    """通过分页获取 GitHub API 数据。"""
    page = 1
    data = []
    while True:
        response = session.get(url, params={'per_page': 100, 'page': page}, headers=headers)
        if response.status_code != 200:
            logger.warning(f"获取分页数据失败, URL: {url}, 状态码: {response.status_code}")
            break
        page_data = response.json()
        if not page_data:
            break
        data.extend(page_data)
        page += 1
    return data


def get_github_rank():
    """
    获取GitHub排名信息。
    """
    try:
        logger.info("开始获取GitHub排名信息")
        rank_data = get_rank_data()
        logger.info(f"成功获取GitHub排名信息: {rank_data}")
        return rank_data, 200
    except Exception as e:
        logger.error(f"获取GitHub排名信息失败: {e}")
        return {'error': '获取GitHub排名信息失败'}, 500


def get_user_info(info_id):
    """
    根据用户ID获取用户信息。
    :param info_id: 用户ID
    """
    try:
        user_url = GITHUB_USER_URL.format(username=info_id)
        session = requests.Session()
        headers = {'User-Agent': get_random_user_agent(),
                   'Authorization': f'token {Config.token}'
                   } if Config.token else {}

        user_response = session.get(user_url, headers=headers, verify=False)
        if user_response.status_code == 200:
            user_data = user_response.json()
            logger.info(f"成功获取用户信息: {user_data}")
            save_response = save_user_data(info_id, user_data)
            if save_response:
                return user_data, 200
            else:
                return {'error': '保存用户信息失败'}, 500
        else:
            logger.error(f"获取用户信息失败: 用户信息状态码 {user_response.status_code}")
            return {'error': '获取用户信息失败'}, user_response.status_code
    except Exception as e:
        logger.error(f"获取用户信息失败，用户ID: {info_id}, 错误: {e}")
        return {'error': '获取用户信息失败'}, 500


def get_user_repos_info(info_id):
    """
    获取用户的仓库信息。
    :param info_id: 用户ID
    """
    try:
        user_url = GITHUB_REPOS_URL.format(username=info_id)
        session = requests.Session()
        headers = {'User-Agent': get_random_user_agent(),
                   'Authorization': f'token {Config.token}'
                   } if Config.token else {}
        user_response = session.get(user_url, headers=headers, verify=False)
        if user_response.status_code == 200:
            user_data = user_response.json()
            logger.info(f"成功获取用户项目信息")
            save_response = save_user_reops_data(info_id, user_data)
            if save_response:
                return user_data, 200
            else:
                return {'error': '保存用户项目信息失败'}, 500
        else:
            logger.error(f"获取用户项目信息失败: 用户项目信息状态码 {user_response.status_code}")
            return {'error': '获取用户项目信息失败'}, user_response.status_code
    except Exception as e:
        logger.error(f"获取用户项目信息失败，用户ID: {info_id}, 错误: {e}")
        return {'error': '获取用户项目信息失败'}, 500


def get_user_total_info(info_id):
    """
    获取用户的总信息。
    :param info_id: 用户ID
    """
    try:
        logger.info(f"开始获取用户总信息，用户ID: {info_id}")
        session = requests.Session()
        headers = {'User-Agent': get_random_user_agent(),
                   'Authorization': f'token {Config.token}'
                   } if Config.token else {}

        total_commits, total_prs, total_issues, total_stars = 0, 0, 0, 0

        # 将 JSON 字符串解析为字典
        result = get_github_id(info_id)
        repos_data = json.loads(result['repos_info'])

        with ThreadPoolExecutor() as executor:
            futures = []
            for repo in repos_data:
                repo_name = repo['name']
                total_stars += repo.get('stargazers_count', 0)

                # 提交任务时指定类型，减少 future.result() 时的判断
                futures.append((executor.submit(get_paginated_data,
                                                f"https://api.github.com/repos/{info_id}/{repo_name}/commits",
                                                headers, session), 'commits'))
                futures.append((executor.submit(get_paginated_data,
                                                f"https://api.github.com/repos/{info_id}/{repo_name}/pulls",
                                                headers, session), 'pulls'))
                futures.append((executor.submit(get_paginated_data,
                                                f"https://api.github.com/repos/{info_id}/{repo_name}/issues",
                                                headers, session), 'issues'))

            # 统计请求结果
            for future, request_type in futures:
                result = future.result()
                if request_type == 'commits':
                    total_commits += len(result)
                elif request_type == 'pulls':
                    total_prs += len(result)
                elif request_type == 'issues':
                    total_issues += len(result)

        total_info = {
            'total_commits': total_commits,
            'total_prs': total_prs,
            'total_issues': total_issues,
            'total_stars': total_stars
        }
        logger.info(f"成功获取用户总信息: {total_info}")

        save_response = save_user_total_info_data(info_id, total_info)
        if save_response:
            return total_info, 200
        else:
            return {'error': '保存用户项目信息失败'}, 500
    except Exception as e:
        logger.error(f"获取用户总信息失败，用户ID: {info_id}, 错误: {e}")
        return {'error': '获取用户总信息失败'}, 500


def get_user_tech_info(info_id):
    """
    获取用户的技术信息。
    :param info_id: 用户ID
    :return: 用户的语言使用详情和HTTP状态码
    """
    try:
        # 获取 GitHub 用户的仓库信息
        result = get_github_id(info_id)
        repos = json.loads(result.get('repos_info', '[]'))

        # 初始化 language_stats，用于存储每种语言的字节数和项目计数
        language_stats = {}

        # 遍历用户所有仓库，获取每个仓库的语言统计信息
        for repo in repos:
            languages_url = repo.get("languages_url")
            headers = {'User-Agent': get_random_user_agent(),
                       'Authorization': f'token {Config.token}'
                       } if Config.token else {}

            response = requests.get(languages_url, headers=headers)

            if response.status_code == 200:
                languages = response.json()
                for lang, bytes_count in languages.items():
                    # 累加每种语言的字节数和项目个数
                    if lang not in language_stats:
                        language_stats[lang] = {"bytes": 0, "count": 0}
                    language_stats[lang]["bytes"] += bytes_count
                    language_stats[lang]["count"] += 1
            else:
                logger.error(f"获取仓库 {repo.get('name')} 的语言信息失败: {response.status_code}")

        # 计算各语言的使用比例
        total_bytes = sum(stats["bytes"] for stats in language_stats.values())
        language_details = []
        for lang, stats in language_stats.items():
            percentage = (stats["bytes"] / total_bytes) * 100 if total_bytes > 0 else 0
            language_details.append({
                "language": lang,
                "weight": percentage,
                "language_percentages": f"{percentage:.2f}%",
                "count": stats["count"]  # 项目个数
            })

        # 按照权重对 language_details 进行排序
        language_details.sort(key=lambda x: x['weight'], reverse=True)

        # 保存用户的技术信息数据
        save_response = save_user_tech_info_data(info_id, language_details)
        if save_response:
            return language_details, 200
        else:
            return {'error': '保存用户技术信息失败'}, 500

    except Exception as e:
        logger.error(f"获取用户技术信息失败，用户ID: {info_id}, 错误: {e}")
        return {'error': '获取用户技术信息失败'}, 500


def get_user_guess_nation_info(username):
    """
    猜测用户的国家信息。
    :param username: 用户名
    """
    try:

        logger.info(f"开始猜测用户国家信息，用户名: {username}")

        result = get_github_id(username)
        user_data = json.loads(result.get('user_info', '{}'))

        # 获取位置信息
        location = user_data.get("location")
        if location:
            logger.info(f"GitHub 用户 {username} 的位置信息为: {location}")
            save = save_user_guess_nation_info_data(username, {"guess_nation": location})
            if save:
                return {"guess_nation": location}, 200

        logger.info(f"GitHub 用户 {username} 未公开位置信息，尝试从活动记录或 README 中获取...")

        # 获取用户的最近活动记录
        events_response = requests.get(GITHUB_EVENTS_URL.format(username=username))
        events_response.raise_for_status()
        events_data = events_response.json()

        # 分析活动记录
        possible_location = None
        for event in events_data:
            if event["type"] == "PushEvent":
                for commit in event["payload"]["commits"]:
                    commit_url = commit["url"]
                    commit_response = requests.get(commit_url)
                    commit_response.raise_for_status()
                    commit_data = commit_response.json()

                    commit_message = commit_data.get("commit", {}).get("message", "").lower()
                    author_name = commit_data.get("commit", {}).get("author", {}).get("name", "").lower()
                    author_email = commit_data.get("commit", {}).get("author", {}).get("email", "").lower()

                    if any(keyword in commit_message for keyword in ["country", "city", "location"]):
                        possible_location = commit_message
                        break
                    elif any(keyword in author_name for keyword in ["country", "city", "location"]):
                        possible_location = author_name
                        break
                    elif any(keyword in author_email for keyword in ["country", "city", "location"]):
                        possible_location = author_email
                        break

            if possible_location:
                logger.info(f"通过提交记录推测 GitHub 用户 {username} 的位置信息为: {possible_location}")
                save = save_user_guess_nation_info_data(username, {"guess_nation": possible_location})
                if save:
                    return {"guess_nation": possible_location}, 200

        # 如果活动记录没有找到，尝试从 README 中获取语言信息
        repos_data = json.loads(result.get('repos_info', '[]'))
        branches = ["main", "master"]  # 支持的分支列表
        for repo in repos_data:
            for branch in branches:
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/{branch}/README.md"
                try:
                    readme_response = requests.get(readme_url)
                    readme_response.raise_for_status()
                    readme_content = readme_response.text

                    # 使用 langid 进行语言检测
                    lang, _ = langid.classify(readme_content)
                    if lang == "zh":
                        logger.info(f"通过 README 文件推测 GitHub 用户 {username} 可能来自中国")
                        save = save_user_guess_nation_info_data(username, {"guess_nation": "China"})
                        if save:
                            return {"guess_nation": "China"}, 200
                    elif lang == "en":
                        logger.info(f"通过 README 文件推测 GitHub 用户 {username} 可能来自英语国家")
                        save = save_user_guess_nation_info_data(username, {"guess_nation": "China"})
                        if save:
                            return {"guess_nation": "English-speaking country"}, 200
                except requests.exceptions.RequestException:
                    continue

        # 无法通过其他途径找到用户位置信息的默认提示
        logger.info(f"未能通过活动记录或 README 文件找到 GitHub 用户 {username} 的位置信息")
        return {"guess_nation": "None"}, 200

    except requests.exceptions.RequestException as e:
        logger.error(f"获取 GitHub 用户信息失败: {e}")
        return {'error': '获取 GitHub 用户信息失败'}, 500
    except Exception as e:
        logger.error(f"猜测用户国家信息失败，用户名: {username}, 错误: {e}")
        return {'error': '猜测用户国家信息失败'}, 500


def get_user_summary_info(username):
    """
    获取用户的总结信息。
    :param username: 用户名
    """
    try:
        logger.info(f"开始获取用户总结信息，用户ID: {username}")

        # 获取用户的 GitHub 数据
        result = get_github_id(username)
        user_info = json.loads(result.get('user_info', '{}'))
        most_common_language = result.get('most_common_language', '未知语言')
        total = json.loads(result.get('total', '{}'))
        tech_stack = json.loads(result.get('tech_stack', '[]'))

        # 构建 Cohere API 提示内容
        prompt = (
            f"用户名: {user_info.get('login', '未知')}\n"
            f"姓名: {user_info.get('name', '未知')}\n"
            f"公司: {user_info.get('company', '未知')}\n"
            f"博客: {user_info.get('blog', '无')}\n"
            f"位置: {user_info.get('location', '未知')}\n"
            f"邮箱: {user_info.get('email', '无')}\n"
            f"是否可雇佣: {user_info.get('hireable', '未知')}\n"
            f"简介: {user_info.get('bio', '无简介')}\n"
            f"Twitter用户名: {user_info.get('twitter_username', '无')}\n"
            f"公开仓库数: {user_info.get('public_repos', 0)}\n"
            f"公开Gists数: {user_info.get('public_gists', 0)}\n"
            f"粉丝数: {user_info.get('followers', 0)}\n"
            f"关注数: {user_info.get('following', 0)}\n"
            f"最常用的项目语言: {most_common_language}\n"
            f"总提交数: {total.get('total_commits', 0)}, 总PR数: {total.get('total_prs', 0)}, "
            f"总Issue数: {total.get('total_issues', 0)}, 总星标数: {total.get('total_stars', 0)}\n"
            f"主要技术栈: {', '.join([tech['language'] for tech in tech_stack[:3]])}\n"
            "以上信息是有关GitHub用户的个人信息，请以此生成一段用户介绍信息，要求300字英文！"
        )

        # 初始化 Cohere 客户端并生成摘要
        co = cohere.Client(CohereConfig.COHEREKEY)
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )

        summary_text = response.generations[0].text.strip() if response.generations else "生成用户简介失败。"
        save_user_summary_info_data(username, {"summary": summary_text})

        logger.info(f"成功获取用户总结信息: {summary_text}")
        return {"summary": summary_text}, 200

    except Exception as e:
        logger.error(f"获取用户总结信息失败，用户ID: {username}, 错误: {e}")
        return {'error': '获取用户总结信息失败'}, 500


def get_evaluate_info(username):
    try:
        headers = {'User-Agent': get_random_user_agent(),
                   'Authorization': f'token {Config.token}'
                   } if Config.token else {}
        result = get_github_id(username)  # 需要确保此函数已定义
        repos = json.loads(result.get('repos_info', '[]'))
        total_score = 0

        for repo in repos:
            contributors_url = GITHUB_CONTRIBUTORS_URL.format(username=username, repo=repo['name'])
            contributors_response = requests.get(contributors_url, headers=headers)
            contributors = contributors_response.json() if contributors_response.status_code == 200 else []
            if len(contributors) > 1:  # 协作加分
                total_score += 2

            readme_url = repo['contents_url'].replace('{+path}', 'README.md')
            readme_response = requests.get(readme_url, headers=headers)
            has_readme = readme_response.status_code == 200
            naming_convention_score = 1 if re.search(r"[A-Z][a-z]*", repo['name']) else 0
            total_score += 1 + has_readme + naming_convention_score

            commits_url = GITHUB_COMMITS_URL.format(username=username, repo=repo['name'])
            commits_response = requests.get(commits_url, headers=headers)
            if commits_response.status_code == 200:
                commits = commits_response.json()
                total_score += len(commits)

        if total_score >= 90:
            rating = "SSS"
        elif total_score >= 80:
            rating = "SS"
        elif total_score >= 70:
            rating = "S"
        elif total_score >= 60:
            rating = "A"
        elif total_score >= 40:
            rating = "B"
        elif total_score >= 15:
            rating = "C"
        elif total_score >= 5:
            rating = "D"
        else:
            rating = "F"
        logger.info(f"用户: {username} 评价: {rating} 评分: {total_score}")

        # 如果 save_evaluate_info 在项目中定义，可使用；否则用 json.dumps 代替 jsonify
        save_evaluate_info(username, json.dumps({"evaluate": rating, "score": total_score}))

        return {"evaluate": rating, "score": total_score}, 200

    except requests.RequestException as e:
        logger.error(f"请求 GitHub API 失败: {e}")
        return {'error': '请求 GitHub API 失败'}, 500
    except Exception as e:
        logger.error(f"获取用户评价信息失败，用户ID: {username}, 错误: {e}")
        return {'error': '获取用户评价信息失败'}, 500
