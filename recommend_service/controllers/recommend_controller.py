import datetime

import requests
import urllib3
from bs4 import BeautifulSoup

from recommend_service.config.github_token_config import Config
from recommend_service.utils.logger_utils import logger
from recommend_service.services.recommend_service import save_weekly_recommendations, get_weekly_recommendations

from recommend_service.utils.agent_utils import get_random_user_agent
from recommend_service.config.github_config import GITHUB_USER_URL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_weekly_recommend():
    today = datetime.date.today()
    year, week_num, _ = today.isocalendar()
    weekly = f"{year}-W{week_num}"

    existing_recommendations = get_weekly_recommendations(weekly)
    if existing_recommendations:
        return existing_recommendations,200

    url = "https://github.com/trending/developers?since=weekly"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"获取热门开发者时出错: {e}")
        return [],500

    soup = BeautifulSoup(response.text, 'html.parser')
    developers = soup.find_all('article', class_='Box-row d-flex')

    recommendations = []
    for developer in developers:
        github_id = developer.get('id', '').replace("pa-", "")
        if github_id:
            user_url = GITHUB_USER_URL.format(username=github_id)
            session = requests.Session()
            headers = {'User-Agent': get_random_user_agent(),
                       'Authorization': f'token {Config.token}'
                       } if Config.token else {}

            try:
                user_response = session.get(user_url, headers=headers, verify=False)
                user_response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"获取用户 {github_id} 详情时出错: {e}")
                continue

            user_details = user_response.json()

            developer_info = {
                "id": user_details.get("id", ""),
                "name": user_details.get("name", ""),
                "username": user_details.get("login", ""),
                "avatar": user_details.get("avatar_url", ""),
                "country": user_details.get("location", ""),
                "bio": user_details.get("bio", ""),
                "followers": str(user_details.get("followers", ""))
            }
            recommendations.append(developer_info)
    
    save_weekly_recommendations(weekly,recommendations)
    return recommendations,200
