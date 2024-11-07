from apify_client import ApifyClient
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

    try:
        logger.info("初始化 Apify 客户端...")
        apify_client = ApifyClient(ApifyConfig.APIFY_API_TOKEN)

        logger.info("开始运行 Actor...")

        run = apify_client.actor(ApifyConfig.ACTOR_ID).call(run_input=run_input)
        print(run)
        logger.info("获取数据集内容...")
        dataset_items = apify_client.dataset(run['defaultDatasetId']).list_items().items

        if dataset_items:
            logger.info(f"找到 {len(dataset_items)} 条数据:")
            return dataset_items
        else:
            logger.warning("数据集中没有找到任何条目。")

    except TimeoutError as te:
        logger.error(f"超时错误: {te}")
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        logger.info("Actor 运行结束")
