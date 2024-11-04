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
from info_service.utils.evaluate_utils import evaluate_github_user
from info_service.utils.tech_utils import get_tech_type, get_tech_language_details

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
            try:
                response = session.get(url, params={'per_page': 100, 'page': page}, headers=headers, timeout=30)
                response.raise_for_status()
                page_data = response.json()
                if not page_data:
                    logger.info(f"已获取所有分页数据,共{page - 1}页")
                    break
                data.extend(page_data)
                logger.debug(f"成功获取第{page}页数据,数据条数:{len(page_data)}")
                page += 1
            except requests.exceptions.RequestException as e:
                logger.warning(f"获取分页数据失败, URL: {url}, 错误: {str(e)}, 页码: {page}")
                break
            except ValueError as e:
                logger.warning(f"解析JSON数据失败, URL: {url}, 错误: {str(e)}, 页码: {page}")
                break
        return data

    @staticmethod
    def get_github_rank():
        """获取GitHub排名信息"""
        try:
            logger.info("开始获取GitHub排名信息")
            rank_data = get_rank_data()
            if not rank_data:
                logger.warning("获取到的排名数据为空")
                return {'error': '排名数据为空'}, 404
            logger.info(f"成功获取GitHub排名信息,共{len(rank_data.get('top_users', []))}条记录")
            return rank_data, 200
        except Exception as e:
            logger.error(f"获取GitHub排名信息失败: {e}", exc_info=True)
            return {'error': '获取GitHub排名信息失败'}, 500

    @staticmethod
    def get_user_info(info_id):
        """获取用户基本信息"""
        try:
            if not info_id:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            logger.info(f"开始获取用户{info_id}的基本信息")
            user_url = GITHUB_USER_URL.format(username=info_id)
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

            user_response = session.get(user_url, headers=headers, verify=False, timeout=30)
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"成功获取用户{info_id}的基本信息")
                logger.debug(f"用户{info_id}的详细信息: {user_data}")
                if save_user_data(info_id, user_data):
                    return user_data, 200
                logger.error(f"保存用户{info_id}的基本信息失败")
                return {'error': '保存用户信息失败'}, 500
            elif user_response.status_code == 404:
                logger.error(f"用户{info_id}不存在")
                return {'error': '用户不存在'}, 404
            else:
                logger.error(f"获取用户{info_id}信息失败: 状态码 {user_response.status_code}")
                return {'error': '获取用户信息失败'}, user_response.status_code
        except requests.exceptions.Timeout:
            logger.error(f"获取用户{info_id}信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户{info_id}信息网络请求失败: {e}", exc_info=True)
            return {'error': '网络请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{info_id}信息失败: {e}", exc_info=True)
            return {'error': '获取用户信息失败'}, 500

    @staticmethod
    def get_user_repos_info(info_id):
        """获取用户仓库信息"""
        try:
            if not info_id:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            logger.info(f"开始获取用户{info_id}的仓库信息")
            user_url = GITHUB_REPOS_URL.format(username=info_id)
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

            user_response = session.get(user_url, headers=headers, verify=False, timeout=30)
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"成功获取用户{info_id}的仓库信息,共{len(user_data)}个仓库")
                if save_user_reops_data(info_id, user_data):
                    return user_data, 200
                logger.error(f"保存用户{info_id}的仓库信息失败")
                return {'error': '保存用户项目信息失败'}, 500
            elif user_response.status_code == 404:
                logger.error(f"用户{info_id}不存在")
                return {'error': '用户不存在'}, 404
            else:
                logger.error(f"获取用户{info_id}仓库信息失败: 状态码 {user_response.status_code}")
                return {'error': '获取用户项目信息失败'}, user_response.status_code
        except requests.exceptions.Timeout:
            logger.error(f"获取用户{info_id}仓库信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户{info_id}仓库信息网络请求失败: {e}", exc_info=True)
            return {'error': '网络请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{info_id}仓库信息失败: {e}", exc_info=True)
            return {'error': '获取用户项目信息失败'}, 500

    @staticmethod
    def get_user_tech_info(info_id):
        """获取用户技术栈信息"""
        try:
            if not info_id:
                logger.error("用户ID不能为空")
                return {'error': '用户ID不能为空'}, 400

            logger.info(f"开始获取用户{info_id}的技术栈信息")
            result = get_github_id(info_id)
            if not result:
                logger.error(f"获取用户{info_id}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 404

            repos = json.loads(result.get('repos_info', '[]'))
            language_details = get_tech_language_details(repos)
            # 判断技术栈类型
            tech_type = get_tech_type(language_details)
            logger.info(f"用户{info_id}的技术栈类型为: {tech_type}")

            tech_info = {
                "languages": language_details,
                "techs": tech_type
            }

            if save_user_tech_info_data(info_id, tech_info):
                return tech_info, 200
            logger.error(f"保存用户{info_id}的技术栈信息失败")
            return {'error': '保存用户技术信息失败'}, 500

        except Exception as e:
            logger.error(f"获取用户{info_id}技术栈信息失败: {e}", exc_info=True)
            return {'error': '获取用户技术信息失败'}, 500

    @staticmethod
    def get_user_guess_nation_info(username):
        """猜测用户国家信息"""
        try:
            if not username:
                logger.error("用户名不能为空")
                return {'error': '用户名不能为空'}, 400

            logger.info(f"开始猜测用户{username}的国家信息")
            result = get_github_id(username)
            if not result:
                logger.error(f"获取用户{username}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 404

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
                        readme_response = requests.get(readme_url, timeout=30)
                        readme_response.raise_for_status()
                        readme_content = readme_response.text

                        if not readme_content.strip():
                            continue

                        lang, confidence = langid.classify(readme_content)
                        if confidence < 0.5:
                            continue

                        nation_mapping = {
                            "zh": "China",
                            "en": "English-speaking country",
                            "ja": "Japan",
                            "ko": "Korea",
                            "ru": "Russia",
                            "de": "Germany",
                            "fr": "France",
                            "es": "Spanish-speaking country"
                        }

                        if lang in nation_mapping:
                            guess_nation = nation_mapping[lang]
                            logger.info(f"用户{username}的README使用{lang}语言,推测来自{guess_nation}")
                            if save_user_guess_nation_info_data(username, {"guess_nation": guess_nation}):
                                return {"guess_nation": guess_nation}, 200
                    except (requests.exceptions.RequestException, UnicodeDecodeError) as e:
                        logger.debug(f"获取或解析README失败: {str(e)}")
                        continue

            # 3. 从活动记录中获取位置信息
            try:
                logger.info(f"开始从用户{username}的活动记录中获取位置信息")
                events_response = requests.get(
                    GITHUB_EVENTS_URL.format(username=username),
                    headers={'User-Agent': get_random_user_agent()},
                    timeout=30
                )
                events_response.raise_for_status()
                events_data = events_response.json()

                for event in events_data:
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
            except (requests.exceptions.RequestException, ValueError) as e:
                logger.warning(f"获取用户活动记录失败: {str(e)}")

            logger.info(f"未能找到用户{username}的位置信息")
            if save_user_guess_nation_info_data(username, {"guess_nation": "Unknown"}):
                return {"guess_nation": "Unknown"}, 200
            return {'error': '保存猜测信息失败'}, 500

        except Exception as e:
            logger.error(f"猜测用户{username}国家信息失败: {e}", exc_info=True)
            return {'error': '猜测用户国家信息失败'}, 500

    @staticmethod
    def get_user_summary_info(username):
        """获取用户总结信息"""
        try:
            if not username:
                logger.error("用户名不能为空")
                return {'error': '用户名不能为空'}, 400

            logger.info(f"开始获取用户{username}的总结信息")
            result = get_github_id(username)
            if not result:
                logger.error(f"获取用户{username}的GitHub ID失败")
                return {'error': '获取GitHub ID失败'}, 404

            # 准备用户数据
            user_info = json.loads(result.get('user_info', '{}') or '{}')
            most_common_language = result.get('most_common_language', '未知语言')
            tech_stack = json.loads(result.get('tech_stack', '[]') or '[]')

            if not user_info:
                logger.error(f"未找到用户{username}的基本信息")
                return {'error': '未找到用户基本信息'}, 404

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
                f"主要技术栈: {', '.join([tech.get('language', '未知') for tech in tech_stack.get('languages')[:3]])}\n"
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
                    return {"summary": summary_text}, 200
                logger.error(f"保存用户{username}的总结信息失败")
                return {'error': '保存总结信息失败'}, 500

            except requests.exceptions.Timeout:
                logger.error("Cohere API请求超时")
                return {'error': 'AI生成超时'}, 504
            except requests.exceptions.RequestException as e:
                logger.error(f"Cohere API请求失败: {str(e)}")
                return {'error': 'AI服务请求失败'}, 503

        except Exception as e:
            logger.error(f"获取用户{username}总结信息失败: {e}", exc_info=True)
            return {'error': '获取用户总结信息失败'}, 500

    @staticmethod
    def get_evaluate_info(username):
        """获取用户GitHub统计评价信息"""
        try:
            if not username:
                logger.error("用户名不能为空")
                return {'error': '用户名不能为空'}, 400

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
    def get_user_total_info(github_id):
        try:
            if not github_id:
                logger.error("GitHub ID不能为空")
                return {'error': 'GitHub ID不能为空'}, 400

            logger.info(f"开始获取用户{github_id}的总信息")
            session = requests.Session()
            headers = {
                'User-Agent': get_random_user_agent(),
                'Authorization': f'token {Config.token}'
            } if Config.token else {'User-Agent': get_random_user_agent()}

            # 获取用户的仓库信息
            repos_url = GITHUB_REPOS_URL.format(username=github_id)
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
                commits_url = f"https://api.github.com/repos/{github_id}/{repo['name']}/commits"
                commits_response = session.get(commits_url, headers=headers, verify=False, timeout=30)
                commits_response.raise_for_status()
                total_commits += len(commits_response.json())

                # 获取每个仓库的拉取请求数
                prs_url = f"https://api.github.com/repos/{github_id}/{repo['name']}/pulls"
                prs_response = session.get(prs_url, headers=headers, verify=False, timeout=30)
                prs_response.raise_for_status()
                total_prs += len(prs_response.json())

                # 获取每个仓库的问题数
                issues_url = f"https://api.github.com/repos/{github_id}/{repo['name']}/issues"
                issues_response = session.get(issues_url, headers=headers, verify=False, timeout=30)
                issues_response.raise_for_status()
                total_issues += len(issues_response.json())

            user_total_info = {
                "commits": total_commits,
                "forks": total_forks,
                "issues": total_issues,
                "prs": total_prs,
                "stars": total_stars,
                "username": github_id
            }

            logger.info(f"成功获取用户{github_id}的总信息: {user_total_info}")
            return user_total_info, 200

        except requests.exceptions.Timeout:
            logger.error(f"获取用户{github_id}的总信息超时")
            return {'error': '请求超时'}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"请求用户{github_id}的总信息失败: {str(e)}", exc_info=True)
            return {'error': '请求失败'}, 503
        except Exception as e:
            logger.error(f"获取用户{github_id}的总信息失败: {str(e)}", exc_info=True)
            return {'error': '获取总信息失败'}, 500

    ...
