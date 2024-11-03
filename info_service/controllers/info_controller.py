import langid
import requests
import json
import urllib3

from info_service.config.cohere_config import CohereConfig
from info_service.config.github_token_config import Config
from info_service.utils.logger_utils import logger
from info_service.services.info_service import (
    get_rank_data, save_user_data, save_user_reops_data,
    save_user_tech_info_data, save_user_guess_nation_info_data, save_user_summary_info_data,
    get_github_id, save_evaluate_info
)
from info_service.utils.agent_utils import get_random_user_agent
from info_service.config.github_config import (
    GITHUB_USER_URL, GITHUB_REPOS_URL, GITHUB_EVENTS_URL,
)
from info_service.utils.evaluate_utils import evaluate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InfoController:
    """info 控制器类,处理所有 info 相关的请求"""

    @staticmethod
    def get_paginated_data(url, headers, session):
        """通过分页获取 GitHub API 数据"""
        page = 1
        data = []
        logger.info(f"开始获取分页数据,URL: {url}")
        while True:
            response = session.get(url, params={'per_page': 100, 'page': page}, headers=headers)
            if response.status_code != 200:
                logger.warning(f"获取分页数据失败, URL: {url}, 状态码: {response.status_code}, 页码: {page}")
                break
            page_data = response.json()
            if not page_data:
                logger.info(f"已获取所有分页数据,共{page - 1}页")
                break
            data.extend(page_data)
            logger.debug(f"成功获取第{page}页数据,数据条数:{len(page_data)}")
            page += 1
        return data

    @staticmethod
    def get_github_rank():
        """获取GitHub排名信息"""
        try:
            logger.info("开始获取GitHub排名信息")
            rank_data = get_rank_data()
            logger.info(f"成功获取GitHub排名信息,共{len(rank_data.get('top_users', []))}条记录")
            return rank_data, 200
        except Exception as e:
            logger.error(f"获取GitHub排名信息失败: {e}", exc_info=True)
            return {'error': '获取GitHub排名信息失败'}, 500

    @staticmethod
    def get_user_info(info_id):
        """获取用户基本信息"""
        try:
            logger.info(f"开始获取用户{info_id}的基本信息")
            user_url = GITHUB_USER_URL.format(username=info_id)
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {}

            user_response = session.get(user_url, headers=headers, verify=False)
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"成功获取用户{info_id}的基本信息")
                logger.debug(f"用户{info_id}的详细信息: {user_data}")
                if save_user_data(info_id, user_data):
                    return user_data, 200
                logger.error(f"保存用户{info_id}的基本信息失败")
                return {'error': '保存用户信息失败'}, 500
            logger.error(f"获取用户{info_id}信息失败: 状态码 {user_response.status_code}")
            return {'error': '获取用户信息失败'}, user_response.status_code
        except Exception as e:
            logger.error(f"获取用户{info_id}信息失败: {e}", exc_info=True)
            return {'error': '获取用户信息失败'}, 500

    @staticmethod
    def get_user_repos_info(info_id):
        """获取用户仓库信息"""
        try:
            logger.info(f"开始获取用户{info_id}的仓库信息")
            user_url = GITHUB_REPOS_URL.format(username=info_id)
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {}
            user_response = session.get(user_url, headers=headers, verify=False)
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"成功获取用户{info_id}的仓库信息,共{len(user_data)}个仓库")
                if save_user_reops_data(info_id, user_data):
                    return user_data, 200
                logger.error(f"保存用户{info_id}的仓库信息失败")
                return {'error': '保存用户项目信息失败'}, 500
            logger.error(f"获取用户{info_id}仓库信息失败: 状态码 {user_response.status_code}")
            return {'error': '获取用户项目信息失败'}, user_response.status_code
        except Exception as e:
            logger.error(f"获取用户{info_id}仓库信息失败: {e}", exc_info=True)
            return {'error': '获取用户项目信息失败'}, 500

    @staticmethod
    def get_user_tech_info(info_id):
        """获取用户技术栈信息"""
        try:
            logger.info(f"开始获取用户{info_id}的技术栈信息")
            result = get_github_id(info_id)
            repos = json.loads(result.get('repos_info', '[]'))
            language_stats = {}

            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {}

            for repo in repos:
                languages_url = repo.get("languages_url")
                logger.debug(f"正在获取仓库{repo.get('name')}的语言信息")
                response = requests.get(languages_url, headers=headers)

                if response.status_code == 200:
                    languages = response.json()
                    for lang, bytes_count in languages.items():
                        if lang not in language_stats:
                            language_stats[lang] = {"bytes": 0, "count": 0}
                        language_stats[lang]["bytes"] += bytes_count
                        language_stats[lang]["count"] += 1
                else:
                    logger.error(f"获取仓库{repo.get('name')}的语言信息失败: 状态码 {response.status_code}")

            total_bytes = sum(stats["bytes"] for stats in language_stats.values())
            language_details = []
            for lang, stats in language_stats.items():
                percentage = (stats["bytes"] / total_bytes) * 100 if total_bytes > 0 else 0
                language_details.append({
                    "language": lang,
                    "weight": percentage,
                    "language_percentages": f"{percentage:.2f}%",
                    "count": stats["count"]
                })

            language_details.sort(key=lambda x: x['weight'], reverse=True)
            logger.info(f"成功分析用户{info_id}的技术栈信息,共使用{len(language_details)}种编程语言")

            if save_user_tech_info_data(info_id, language_details):
                return language_details, 200
            logger.error(f"保存用户{info_id}的技术栈信息失败")
            return {'error': '保存用户技术信息失败'}, 500

        except Exception as e:
            logger.error(f"获取用户{info_id}技术栈信息失败: {e}", exc_info=True)
            return {'error': '获取用户技术信息失败'}, 500

    @staticmethod
    def get_user_guess_nation_info(username):
        """猜测用户国家信息"""
        try:
            logger.info(f"开始猜测用户{username}的国家信息")
            result = get_github_id(username)
            user_data = json.loads(result.get('user_info', '{}'))
            repos_data = json.loads(result.get('repos_info', '[]'))

            # 1. 首先检查用户资料中的位置信息
            location = user_data.get("location")
            if location:
                logger.info(f"从用户资料中获取到位置信息: {location}")
                if save_user_guess_nation_info_data(username, {"guess_nation": location}):
                    return {"guess_nation": location}, 200

            # 2. 检查README文件的语言
            for repo in repos_data:
                for branch in ["main", "master"]:
                    readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/{branch}/README.md"
                    try:
                        readme_response = requests.get(readme_url)
                        readme_response.raise_for_status()
                        readme_content = readme_response.text

                        lang, _ = langid.classify(readme_content)
                        if lang == "zh":
                            logger.info(f"用户{username}的README使用中文,推测来自中国")
                            if save_user_guess_nation_info_data(username, {"guess_nation": "China"}):
                                return {"guess_nation": "China"}, 200
                        elif lang == "en":
                            logger.info(f"用户{username}的README使用英文")
                            if save_user_guess_nation_info_data(username, {"guess_nation": "English-speaking country"}):
                                return {"guess_nation": "English-speaking country"}, 200
                    except requests.exceptions.RequestException:
                        continue

            # 3. 从活动记录中获取位置信息
            logger.info(f"开始从用户{username}的活动记录中获取位置信息")
            events_response = requests.get(GITHUB_EVENTS_URL.format(username=username))
            events_response.raise_for_status()
            events_data = events_response.json()

            for event in events_data:
                if event["type"] == "PushEvent":
                    for commit in event["payload"]["commits"]:
                        commit_url = commit["url"]
                        commit_response = requests.get(commit_url)
                        commit_response.raise_for_status()
                        commit_data = commit_response.json()

                        location_keywords = ["country", "city", "location"]
                        commit_message = commit_data.get("commit", {}).get("message", "").lower()
                        author_name = commit_data.get("commit", {}).get("author", {}).get("name", "").lower()
                        author_email = commit_data.get("commit", {}).get("author", {}).get("email", "").lower()

                        for text in [commit_message, author_name, author_email]:
                            if any(keyword in text for keyword in location_keywords):
                                logger.info(f"在用户{username}的提交信息中找到位置信息: {text}")
                                if save_user_guess_nation_info_data(username, {"guess_nation": text}):
                                    return {"guess_nation": text}, 200

            logger.info(f"未能找到用户{username}的位置信息")
            return {"guess_nation": "None"}, 200

        except requests.exceptions.RequestException as e:
            logger.error(f"获取GitHub用户{username}信息失败: {e}", exc_info=True)
            return {'error': '获取GitHub用户信息失败'}, 500
        except Exception as e:
            logger.error(f"猜测用户{username}国家信息失败: {e}", exc_info=True)
            return {'error': '猜测用户国家信息失败'}, 500

    @staticmethod
    def get_user_summary_info(username):
        """获取用户总结信息"""
        try:
            logger.info(f"开始获取用户{username}的总结信息")
            result = get_github_id(username)
            if not result:
                logger.error(f"获取用户{username}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 500

            # 准备用户数据
            user_info = json.loads(result.get('user_info', '{}') or '{}')
            most_common_language = result.get('most_common_language', '未知语言')
            tech_stack = json.loads(result.get('tech_stack', '[]') or '[]')

            # 生成提示信息
            logger.info(f"正在为用户{username}生成总结提示信息")
            prompt_data = (
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
                f"主要技术栈: {', '.join([tech['language'] for tech in tech_stack[:3]])}\n"
                "以上信息是有关GitHub用户的个人信息，请以此生成一段用户介绍信息，要求300字英文！"
            )

            # 调用Cohere API
            logger.info(f"开始调用Cohere API生成用户{username}的总结")
            headers = {
                'Authorization': f'BEARER {CohereConfig.COHEREKEY}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'command',
                'prompt': prompt_data,
                'max_tokens': 300,
                'temperature': 0.7,
                'k': 0,
                'stop_sequences': [],
                'return_likelihoods': 'NONE'
            }

            logger.info("开始调用Cohere API生成总结")
            response = requests.post(
                'https://api.cohere.ai/v1/generate',
                headers=headers,
                json=data,
                verify=False
            )

            if response.status_code != 200:
                logger.error(f"Cohere API请求失败: {response.text}")
                return {'error': 'Cohere API请求失败'}, 500

            logger.info("成功从Cohere API获取响应")
            summary_text = response.json()['generations'][0]['text'].strip()

            logger.info(f"成功生成用户{username}的总结信息")
            logger.debug(f"用户{username}的总结内容: {summary_text}")
            save_user_summary_info_data(username, summary_text)
            return {"summary": summary_text}, 200

        except Exception as e:
            logger.error(f"获取用户{username}总结信息失败: {e}", exc_info=True)
            return {'error': '获取用户总结信息失败'}, 500

    @staticmethod
    def get_evaluate_info(username):
        """获取用户GitHub统计评价信息"""
        try:
            logger.info(f"开始获取用户{username}的GitHub统计评价信息")
            stats = evaluate(username, Config.token)
            if save_evaluate_info(username, stats):
                return stats, 200
            logger.error(f"保存用户{username}的评价信息失败")
            return {'error': '保存用户评价信息失败'}, 500

        except requests.RequestException as e:
            logger.error(f"请求用户{username}的GitHub统计数据失败: {str(e)}", exc_info=True)
            return {'error': '请求GitHub统计数据失败'}, 500
