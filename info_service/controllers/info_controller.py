import concurrent
import re
from collections import Counter
from datetime import datetime

import langid
import requests
import json
import urllib3
from dateutil import parser

from info_service.config.cohere_config import CohereConfig
from info_service.config.github_token_config import Config
from info_service.config.nation_config import Nation
from info_service.utils.logger_utils import logger
from info_service.services.info_service import (
    save_user_data, save_user_reops_data,
    save_user_tech_info_data, save_user_guess_nation_info_data, save_user_summary_info_data,
    get_github_id, save_evaluate_info, save_user_issues_data
)
from info_service.utils.agent_utils import get_random_user_agent
from info_service.config.github_config import (
    GITHUB_USER_URL, GITHUB_REPOS_URL, GITHUB_EVENTS_URL, GITHUB_FOLLOWING_URL, GITHUB_FOLLOWERS_URL,
)
from info_service.utils.evaluate_utils import evaluate_github_user
from info_service.utils.tech_utils import get_tech_type, get_tech_language_details

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InfoController:
    """info 控制器类,处理所有 info 相关的请求"""

    @staticmethod
    def get_user_info(username):
        """获取用户基本信息"""
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get('user_info'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('user_info')), 200

            logger.info(f"开始获取用户{username}的基本信息")
            user_url = GITHUB_USER_URL.format(username=username)
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

            user_response = session.get(user_url, headers=headers, verify=False, timeout=30)
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"成功获取用户{username}的基本信息")
                logger.debug(f"用户{username}的详细信息: {user_data}")
                if save_user_data(username, user_data):
                    return user_data, 200
                logger.error(f"保存用户{username}的基本信息失败")
                return {'error': '保存用户信息失败'}, 500
            elif user_response.status_code == 404:
                logger.error(f"用户{username}不存在")
                return {'error': '用户不存在'}, 404
            else:
                logger.error(f"获取用户{username}信息失败: 状态码 {user_response.status_code}")
                return {'error': '获取用户信息失败'}, user_response.status_code
        except requests.exceptions.Timeout:
            logger.error(f"获取用户{username}信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户{username}信息网络请求失败: {e}", exc_info=True)
            return {'error': '网络请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{username}信息失败: {e}", exc_info=True)
            return {'error': '获取用户信息失败'}, 500

    @staticmethod
    def get_user_repos_info(username):
        """获取用户仓库信息"""
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get('repos_info'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('repos_info')), 200

            logger.info(f"开始获取用户{username}的仓库信息")
            user_url = GITHUB_REPOS_URL.format(username=username)
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

            user_response = session.get(user_url, headers=headers, verify=False, timeout=30)
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"成功获取用户{username}的仓库信息,共{len(user_data)}个仓库")
                if save_user_reops_data(username, user_data):
                    return user_data, 200
                logger.error(f"保存用户{username}的仓库信息失败")
                return {'error': '保存用户项目信息失败'}, 500
            elif user_response.status_code == 404:
                logger.error(f"用户{username}不存在")
                return {'error': '用户不存在'}, 404
            else:
                logger.error(f"获取用户{username}仓库信息失败: 状态码 {user_response.status_code}")
                return {'error': '获取用户项目信息失败'}, user_response.status_code
        except requests.exceptions.Timeout:
            logger.error(f"获取用户{username}仓库信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户{username}仓库信息网络请求失败: {e}", exc_info=True)
            return {'error': '网络请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{username}仓库信息失败: {e}", exc_info=True)
            return {'error': '获取用户项目信息失败'}, 500


    @staticmethod
    def get_user_issue_info(username):
        """
        获取用户的issue信息
        :param username: GitHub用户ID
        :return: issue信息列表和状态码
        """
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get('issues_info'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('issues_info')), 200

            # 设置请求头
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

            session = requests.Session()

            # 存储所有issue信息
            all_issues = []

            # 获取用户的issue信息，添加is:issue查询参数
            issues_url = f"https://api.github.com/search/issues?q=user:{username}+is:issue&sort=updated&order=desc"
            issues_response = session.get(issues_url, headers=headers, verify=False, timeout=30)
            issues_data = issues_response.json()

            # 处理返回的issue数据
            if 'items' in issues_data:
                for issue in issues_data['items']:
                    # 使用正则表达式从repository_url提取仓库名
                    repo_name = issue['repository_url']
                    repo_name_match = re.search(r'https://api\.github\.com/repos/[^/]+/([^/]+)', repo_name)
                    repo_name = repo_name_match.group(1) if repo_name_match else repo_name

                    issue_info = {
                        'created_at': issue['created_at'],
                        'update_at': issue['updated_at'],
                        'issue_url': issue['html_url'],
                        'issue_title': issue['title'],
                        'repo_name': repo_name,
                        'state': issue['state'],
                        'user': issue['user']
                    }
                    all_issues.append(issue_info)

            logger.info(f"成功获取用户{username}的issue信息")

            if save_user_issues_data(username, all_issues):
                return all_issues, 200

        except requests.exceptions.Timeout:
            logger.error(f"获取用户{username}的issue信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"请求用户{username}的issue信息失败: {str(e)}", exc_info=True)
            return {'error': '请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{username}的issue信息失败: {str(e)}", exc_info=True)
            return {'error': '获取issue信息失败'}, 500

    @staticmethod
    def get_user_tech_info(username):
        """获取用户技术栈信息"""
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get('tech_stack'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('tech_stack')), 200

            logger.info(f"开始获取用户{username}的技术栈信息")
            if not result:
                logger.error(f"获取用户{username}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 404

            repos = json.loads(result.get('repos_info', '[]'))
            language_details = get_tech_language_details(repos)
            # 判断技术型
            tech_type = get_tech_type(language_details)
            logger.info(f"用户{username}的技术栈类型为: {tech_type}")

            tech_info = {
                "languages": language_details,
                "techs": tech_type
            }

            if save_user_tech_info_data(username, tech_info):
                return tech_info, 200
            logger.error(f"保存用户{username}的技术栈信息失败")
            return {'error': '保存用户技术信息失败'}, 500

        except Exception as e:
            logger.error(f"获取用户{username}技术栈信息失败: {e}", exc_info=True)
            return {'error': '获取用户技术信息失败'}, 500

    @staticmethod
    def get_user_guess_nation_info(username):
        """猜测用户国家信息"""
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get('most_common_language'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('most_common_language')), 200

            logger.info(f"开始猜测用户{username}的国家信息")
            if not result:
                logger.error(f"获取用户{username}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 404

            user_data = json.loads(result.get('user_info', '{}'))
            repos_data = json.loads(result.get('repos_info', '[]'))

            # 1. 检查用户资料中的位置信息
            location = user_data.get("location")
            if location:
                logger.info(f"从用户资料中获取到位置信息: {location}")
                if save_user_guess_nation_info_data(username, {"guess_nation": location}):
                    return {"guess_nation": location}, 200

            # 2. 并行请求读取 README 文件并分析语言
            def fetch_readme_language(repo):
                for branch in ["main", "master"]:
                    readme_url = f"https://raw.githubusercontent.com/{username}/{repo['name']}/{branch}/README.md"
                    try:
                        readme_response = requests.get(readme_url, timeout=30)
                        readme_response.raise_for_status()
                        readme_content = readme_response.text

                        if not readme_content.strip():
                            continue

                        lang, confidence = langid.classify(readme_content)
                        if confidence < 0.5:
                            continue
                        nation_mapping = Nation.nation_mapping
                        if lang in nation_mapping:
                            guess_nation = nation_mapping[lang]
                            logger.info(f"用户{username}的README使用{lang}语言,推测来自{guess_nation}")
                            if save_user_guess_nation_info_data(username, {"guess_nation": guess_nation}):
                                return {"guess_nation": guess_nation}, 200
                    except (requests.exceptions.RequestException, UnicodeDecodeError) as e:
                        logger.debug(f"获取或解析README失败: {str(e)}")
                        continue
                return None

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(fetch_readme_language, repo) for repo in repos_data]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        return result

            # 3. 从活动记录中获取位置信息
            def fetch_event_location(event):
                if event["type"] == "PushEvent":
                    for commit in event["payload"].get("commits", []):
                        try:
                            commit_response = requests.get(
                                commit["url"],
                                headers={'User-Agent': get_random_user_agent()},
                                timeout=30
                            )
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
                        except (requests.exceptions.RequestException, ValueError) as e:
                            logger.debug(f"获取或解析提交信息失败: {str(e)}")
                            continue
                return None

            try:
                events_response = requests.get(
                    GITHUB_EVENTS_URL.format(username=username),
                    headers={'User-Agent': get_random_user_agent()},
                    timeout=30
                )
                events_response.raise_for_status()
                events_data = events_response.json()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(fetch_event_location, event) for event in events_data]
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result:
                            return result
            except (requests.exceptions.RequestException, ValueError) as e:
                logger.warning(f"获取用户活动记录失败: {str(e)}")

            # 4. 根据关系网络推测国家信息
            def analyze_network_locations():
                follower_locations = []
                following_locations = []

                try:
                    # 获取关注者
                    followers_response = requests.get(
                        GITHUB_FOLLOWERS_URL.format(username=username),
                        headers={'User-Agent': get_random_user_agent()},
                        timeout=30
                    )
                    followers_response.raise_for_status()
                    followers = followers_response.json()

                    for follower in followers:
                        follower_info = requests.get(
                            GITHUB_USER_URL.format(username=follower['login']),
                            headers={'User-Agent': get_random_user_agent()},
                            timeout=30
                        ).json()
                        location = follower_info.get("location")
                        if location:
                            follower_locations.append(location)

                    # 获取关注的用户
                    following_response = requests.get(
                        GITHUB_FOLLOWING_URL.format(username=username),
                        headers={'User-Agent': get_random_user_agent()},
                        timeout=30
                    )
                    following_response.raise_for_status()
                    following = following_response.json()

                    for follow in following:
                        following_info = requests.get(
                            GITHUB_USER_URL.format(follow['login']),
                            headers={'User-Agent': get_random_user_agent()},
                            timeout=30
                        ).json()
                        location = following_info.get("location")
                        if location:
                            following_locations.append(location)

                    # 统计位置频率
                    location_counts = Counter(follower_locations + following_locations)
                    if location_counts:
                        most_common_location, _ = location_counts.most_common(1)[0]
                        logger.info(f"通过关系网络推测用户{username}的国家: {most_common_location}")
                        if save_user_guess_nation_info_data(username, {"guess_nation": most_common_location}):
                            return {"guess_nation": most_common_location}, 200
                except (requests.exceptions.RequestException, ValueError) as e:
                    logger.warning(f"获取关系网络信息失败: {str(e)}")
                    return None

            network_result = analyze_network_locations()
            if network_result:
                return network_result

            logger.info(f"未能找到用户{username}的位置信息")
            if save_user_guess_nation_info_data(username, {"guess_nation": "Unknown"}):
                return {"guess_nation": "Unknown"}, 200
            return {'error': '保存猜测信息失败'}, 500

        except Exception as e:
            logger.error(f"猜测用户{username}国家信息失败: {e}", exc_info=True)
            return {'error': '猜测用户国家信息失败'}, 500

    @staticmethod
    def get_user_summary_info(username):
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get(
                        'summa'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return {"summary": json.loads(result.get('summa')), "updated_at": result.get('updated_at')}, 200

            logger.info(f"开始获取用户{username}的总结信息")

            if not result:
                logger.error(f"获取用户{username}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 404

            user_info = json.loads(result.get('user_info', '{}'))
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
                f"主要技术栈: {tech_stack}\n"
                "以上信息是有关GitHub用户的个人信息，请以此生成一段用户介绍信息，要求300字英文！"
            )

            # 调用Cohere API
            logger.info(f"开始调用Cohere API生成用户{username}的总结")
            if not CohereConfig.COHEREKEY:
                logger.error("Cohere API密钥未配置")
                return {'error': 'Cohere API密钥未配置'}, 500

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

            try:
                response = requests.post(
                    'https://api.cohere.ai/v1/generate',
                    headers=headers,
                    json=data,
                    verify=False,
                    timeout=30
                )
                response.raise_for_status()

                logger.info("成功从Cohere API获取响应")
                response_data = response.json()
                if not response_data.get('generations'):
                    logger.error("Cohere API返回的生成结果为空")
                    return {'error': 'AI生成失败'}, 500

                summary_text = response_data['generations'][0]['text'].strip()
                if not summary_text:
                    logger.error("生成的总结内容为空")
                    return {'error': '生成的总结内容为空'}, 500

                logger.info(f"成功生成用户{username}的总结信息")
                logger.debug(f"用户{username}的总结内容: {summary_text}")

                if save_user_summary_info_data(username, summary_text):
                    return {"summary": summary_text, "updated_at": result.get('updated_at')}, 200
                logger.error(f"保存用户{username}的总结信息失败")
                return {'error': '保存总结信息失败'}, 500

            except requests.exceptions.Timeout:
                logger.error("Cohere API请求超时")
                return {'error': 'AI生成超时'}, 504
            except requests.exceptions.RequestException as e:
                logger.error(f"Cohere API请求失败: {str(e)}")
                return {'error': 'AI服务请求失败'}, 503

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}", exc_info=True)
            return {'error': '数据解析错误'}, 500
        except Exception as e:
            logger.error(f"获取用户{username}总结信息失败: {e}", exc_info=True)
            return {'error': '获取用户总结信息失败'}, 500

    @staticmethod
    def get_evaluate_info(username):
        """获取用户GitHub统计评价信息"""
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get(
                        'evaluate'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('evaluate')), 200

            logger.info(f"开始获取用户{username}的GitHub统计评价信息")
            stats = evaluate_github_user(username)
            if not stats:
                logger.error(f"获取用户{username}的评价数据为空")
                return {'error': '评价数据为空'}, 404

            if save_evaluate_info(username, stats):
                return stats, 200
            logger.error(f"保存用户{username}的评价信息失败")
            return {'error': '保存用户评价信息失败'}, 500

        except requests.exceptions.Timeout:
            logger.error(f"获取用户{username}的GitHub统计数据超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"请求用户{username}的GitHub统计数据失败: {str(e)}", exc_info=True)
            return {'error': '请求GitHub统计数据失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{username}的评价信息失败: {str(e)}", exc_info=True)
            return {'error': '获取评价信息失败'}, 500

    @staticmethod
    def get_user_total_info(username):
        try:
            if not username:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            result = get_github_id(username)
            if result:
                result = json.loads(result)
                # 检查是否有最近的缓存数据
                updated_at = result.get('updated_at')
                if isinstance(updated_at, str):
                    updated_at = parser.isoparse(updated_at)

                if updated_at and (datetime.now().date() - updated_at.date()).days <= 7 and result.get(
                        'total'):
                    logger.info(f"返回用户{username}的缓存总结信息")
                    return json.loads(result.get('total')), 200

            logger.info(f"开始获取用户{username}的总信息")
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

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
                prs_url = f"https://api.github.com/repos/{username}/{repo['name']}/pulls"
                prs_response = session.get(prs_url, headers=headers, verify=False, timeout=30)
                prs_response.raise_for_status()
                total_prs += len(prs_response.json())

                # 获取每个仓库的问题数
                issues_url = f"https://api.github.com/repos/{username}/{repo['name']}/issues"
                issues_response = session.get(issues_url, headers=headers, verify=False, timeout=30)
                issues_response.raise_for_status()
                total_issues += len(issues_response.json())

            user_total_info = {
                "commits": total_commits,
                "forks": total_forks,
                "issues": total_issues,
                "prs": total_prs,
                "stars": total_stars,
                "username": username
            }

            logger.info(f"成功获取用户{username}的总信息: {user_total_info}")
            return user_total_info, 200

        except requests.exceptions.Timeout:
            logger.error(f"获取用户{username}的总信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"请求用户{username}的总信息失败: {str(e)}", exc_info=True)
            return {'error': '请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{username}的总信息失败: {str(e)}", exc_info=True)
            return {'error': '获取总信息失败'}, 500
