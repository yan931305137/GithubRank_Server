import requests
from info_service.utils.logger_utils import logger
from info_service.config.github_token_config import Config
from info_service.config.apify_config import ApifyConfig


def run_actor(search_query, nation, target_language, techs, confidence_threshold, page, per_page):
    run_input = {
        "confidence_threshold": confidence_threshold,
        "github_token": Config.token,
        "page": page,
        "per_page": per_page,
        "proxyConfiguration": {
            "useApifyProxy": True
        },
        "search_query": search_query,
        "nation": nation,
        "startUrls": [
            {
                "url": "https://apify.com",
                "method": "GET"
            }
        ],
        "target_language": target_language,
        "techs": techs
    }

    print(run_input)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ApifyConfig.APIFY_API_TOKEN}"
    }

    try:
        # 使用 ~ 符号连接 username 和 actor_name
        url = f"https://api.apify.com/v2/acts/{ApifyConfig.ACTOR_ID}/runs"
        logger.info("发送 HTTP 请求以启动 Actor...")
        response = requests.post(url, json=run_input, headers=headers)
        response.raise_for_status()
        run_data = response.json()

        # 等待 Actor 运行完成
        run_id = run_data['data']['id']
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?waitForFinish=999999"
        status_response = requests.get(status_url, headers=headers)
        status_response.raise_for_status()
        status_data = status_response.json()

        # 获取数据集内容
        dataset_id = status_data['data']['defaultDatasetId']
        logger.info("获取数据集内容...")
        dataset_response = requests.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
            headers=headers
        )
        dataset_response.raise_for_status()
        dataset_items = dataset_response.json()

        if dataset_items:
            logger.info(f"找到 {len(dataset_items)} 条数据:")
            return dataset_items
        else:
            logger.warning("数据集中没有找到任何条目。")

    except requests.exceptions.Timeout as te:
        logger.error(f"超时错误: {te}")
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP 请求错误: {e}")
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        logger.info("Actor 运行结束")
