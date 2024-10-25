import requests
import json
from collections import defaultdict
from tqdm import tqdm
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import langid
import cohere


def fetch_user_info(session, user_url, headers):
    user_response = session.get(user_url, headers=headers, verify=False)
    if user_response.status_code == 200:
        user_data = user_response.json()
        location = user_data.get('location', 'None')
        print(f"用户位置信息: {location}")
        return user_data
    else:
        print(f"获取用户信息失败: 用户信息状态码 {user_response.status_code}")
        return None


def fetch_repos_info(session, repos_url):
    repos_info = []
    page = 1
    while True:
        headers = {'User-Agent': get_random_user_agent()}  # 每请求更新User-Agent
        response = session.get(repos_url, params={'per_page': 100, 'page': page}, headers=headers)
        if response.status_code != 200:
            break
        repos_page = response.json()
        if not repos_page:
            break
        repos_info.extend(repos_page)
        page += 1
    return repos_info


def fetch_repo_details(repo, session):
    repo_url = repo.get('url', '')
    try:
        repo_response = session.get(repo_url, headers={'User-Agent': get_random_user_agent()})
        repo_response.raise_for_status()  # 检查请求是否成功
        repo_data = repo_response.json()
        star_count = repo_data.get('stargazers_count', 0)
        commit_count = repo_data.get('commits_count', 0)  # 假设API返回提交次数

        # 获取PR数和Issue数
        pulls_url = repo_data.get('pulls_url', '').replace('{/number}', '')
        issues_url = repo_data.get('issues_url', '').replace('{/number}', '')

        pr_count = session.get(pulls_url, headers={'User-Agent': get_random_user_agent()}).json()
        issue_count = session.get(issues_url, headers={'User-Agent': get_random_user_agent()}).json()

        # 使用langid检测项目描述语言
        description = repo_data.get('description', '')
        if description:
            try:
                language = detect_language(description)
            except Exception as e:
                print(f"语言检测失败: {e}")

        return repo['id'], star_count, commit_count, len(pr_count), len(issue_count)
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return repo['id'], 0, 0, 0, 0


def calculate_language_weight(star_count, commit_count):
    # 权重计算：基础权重 + 星标权重 + 提交权重
    return 1 + star_count * 0.1 + commit_count * 0.05


def calculate_totals(commit_counts):
    total_commits = sum(commit_count for _, commit_count, _, _ in commit_counts.values())
    total_prs = sum(pr_count for _, _, pr_count, _ in commit_counts.values())
    total_issues = sum(issue_count for _, _, _, issue_count in commit_counts.values())
    total_stars = sum(star_count for star_count, _, _, _ in commit_counts.values())

    return {
        'total_commits': total_commits,
        'total_prs': total_prs,
        'total_issues': total_issues,
        'total_stars': total_stars
    }


def get_github_user_info(username):
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"
    session = requests.Session()
    headers = {'User-Agent': get_random_user_agent()}
    user_info = fetch_user_info(session, user_url, headers)

    if user_info:
        repos_info = fetch_repos_info(session, repos_url)
        print(f"用户 {username} 有 {len(repos_info)} 个项目")

        language_weights = defaultdict(float)
        commit_counts = {}
        language_counts = defaultdict(int)  # 用于统计每种语言出现的次数
        country_language_counts = defaultdict(int)  # 用于统计每种国家语言出现的次数

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_repo_details, repo, session): repo for repo in repos_info}
            for future in tqdm(as_completed(futures), total=len(repos_info), desc="预先获取star数和提交次数"):
                repo_id, star_count, commit_count, pr_count, issue_count = future.result()
                commit_counts[repo_id] = (star_count, commit_count, pr_count, issue_count)

        for repo in tqdm(repos_info, desc="计算语言权重进度"):
            language = repo.get('language')
            if not language:
                continue

            star_count, commit_count, pr_count, issue_count = commit_counts.get(repo['id'], (0, 0, 0, 0))
            language_weights[language] += calculate_language_weight(star_count, commit_count)
            language_counts[language] += 1  # 统计各个计算机语言使用次数

            # 统计国家语言出现次数
            description = repo.get('description', '')
            if description:
                try:
                    detected_language = detect_language(description)
                    country_language_counts[detected_language] += 1
                except Exception as e:
                    print(f"语言检测失败: {e}")

        # 预测用户国家
        most_common_country_language = max(country_language_counts, key=country_language_counts.get)
        print(f"预测用户国家基于项目描述语言: {most_common_country_language}")

        totals = calculate_totals(commit_counts)
        print(f"总提交数: {totals['total_commits']}, 总PR数: {totals['total_prs']}, 总Issue数: {totals['total_issues']}, 总星标数: {totals['total_stars']}")

        # 生成用户介绍词
        user_summary = generate_ai_summary(
            user_info,
            most_common_country_language,
            totals,
            sorted_tech_stack,
            language_counts
        )
        print("用户介绍词:\n", user_summary)

        result = {
            'user_info': user_info,
            'repos_info': repos_info,
            'tech_stack': sorted_tech_stack,
            'most_common_language': most_common_country_language,
            'total': totals,
            'summary': user_summary
        }

        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("用户信息、项目和技术栈已保存到result.json文件")


def detect_language(text):
    language_code, _ = langid.classify(text)  # 预测语言
    return language_code


def generate_ai_summary(user_info, most_common_language, total, tech_stack, language_counts):
    # 构建提示信息
    prompt = (
        f"用户名:{user_info.get('login', '用户名')}\n"
        f"姓名: {user_info.get('name', '未知')}\n"
        f"公司: {user_info.get('company', '未知')}\n"
        f"博客: {user_info.get('blog', '无')}\n"
        f"位置: {user_info.get('location', '未知位置')}\n"
        f"邮箱: {user_info.get('email', '无')}\n"
        f"是否可雇佣: {user_info.get('hireable', '未知')}\n"
        f"简介: {user_info.get('bio', '无个人简介')}\n"
        f"Twitter用户名: {user_info.get('twitter_username', '无')}\n"
        f"公开仓库数: {user_info.get('public_repos', 0)}\n"
        f"公开Gists数: {user_info.get('public_gists', 0)}\n"
        f"粉丝数: {user_info.get('followers', 0)}\n"
        f"关注数: {user_info.get('following', 0)}\n"
        f"最常用的项目语言: {most_common_language}\n"
        f"总提交数: {total['total_commits']}, 总PR数: {total['total_prs']}, "
        f"总Issue数: {total['total_issues']}, 总星标数: {total['total_stars']}\n"
        f"主要技术栈: {', '.join([tech['language'] for tech in tech_stack[:3]])}\n"
        f"每种计算机语言的使用个数: {', '.join([f'{tech['language']}({language_counts[tech['language']]})' for tech in tech_stack])}\n"
        "以上信息是有关github用户的个人信息请以此生成一段用户介绍信息,要求300字英文!"
    )
    print(prompt)

    # 初始化Cohere客户端
    co = cohere.Client('syHymLe0hF7HqhhCJPSkVg6NdLb5Co3nKcYNOvz6')  # 替换为你的Cohere API密钥

    # 调用Cohere API生成摘要
    response = co.generate(
        model='command',  # 使用适当的模型
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )

    # 返回生成的摘要
    return response.generations[0].text.strip()


if __name__ == "__main__":
    get_github_user_info('abc')
    # get_github_user_info('yyx990803')