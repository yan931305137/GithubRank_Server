import requests

from info_service.config.github_token_config import Config
from info_service.utils.agent_utils import get_random_user_agent
from info_service.utils.logger_utils import logger


def get_tech_language_details(repos):
    language_stats = {}

    headers = {
        'User-Agent': get_random_user_agent(),
        'Authorization': f'token {Config.token}'
    } if Config.token else {'User-Agent': get_random_user_agent()}

    for repo in repos:
        languages_url = repo.get("languages_url")
        if not languages_url:
            continue

        logger.debug(f"正在获取仓库{repo.get('name')}的语言信息")
        try:
            response = requests.get(languages_url, headers=headers, timeout=30)
            response.raise_for_status()
            languages = response.json()

            for lang, bytes_count in languages.items():
                if lang not in language_stats:
                    language_stats[lang] = {"bytes": 0, "count": 0}
                language_stats[lang]["bytes"] += bytes_count
                language_stats[lang]["count"] += 1
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"获取仓库{repo.get('name')}的语言信息失败: {str(e)}")
            continue

    if not language_stats:
        logger.warning(f"未找到用户的任何语言信息")
        return {'error': '未找到语言信息'}, 404

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
    logger.info(f"成功分析用户的技术栈信息, 共使用{len(language_details)}种编程语言")
    return language_details


def get_tech_type(language_details):
    """
    根据语言详情判断技术栈类型
    :param language_details: 语言使用详情列表, 每个元素包含language和weight字段
    :return: 技术栈列表
    """
    if not language_details:
        return [{"tech": "未知技术栈"}]

    # 定义各技术领域的主要语言及其权重
    tech_stacks = {
        "前端开发": {
            'JavaScript': 1.0, 'TypeScript': 0.95, 'HTML': 0.85, 'CSS': 0.85,
            'React': 0.75, 'Vue': 0.75, 'Angular': 0.75, 'Svelte': 0.65,
            'Next.js': 0.65, 'Webpack': 0.55, 'Sass': 0.45, 'Less': 0.45,
            'jQuery': 0.35, 'Bootstrap': 0.35, 'Tailwind CSS': 0.55
        },

        "后端开发": {
            'Java': 0.95, 'Python': 0.95, 'Go': 0.85, 'Node.js': 0.85,
            'Spring': 0.75, 'Django': 0.75, 'Flask': 0.65, 'Express': 0.65,
            'MySQL': 0.55, 'PostgreSQL': 0.55, 'MongoDB': 0.55,
            'Redis': 0.45, 'Docker': 0.45, 'Kubernetes': 0.45
        },

        "移动开发": {
            'Swift': 0.95, 'Kotlin': 0.95, 'Java': 0.65,
            'Flutter': 0.85, 'React Native': 0.75, 'Android SDK': 0.75,
            'iOS': 0.65, 'Android': 0.65, 'SwiftUI': 0.55,
            'Jetpack Compose': 0.55
        },

        "数据科学": {
            'Python': 0.85, 'R': 0.85, 'Julia': 0.75,
            'TensorFlow': 0.95, 'PyTorch': 0.95, 'Pandas': 0.75,
            'NumPy': 0.75, 'Scikit-learn': 0.75, 'Jupyter': 0.65,
            'CUDA': 0.55, 'Spark': 0.65, 'Matplotlib': 0.55,
            'SciPy': 0.65, 'Keras': 0.75
        },

        "人工智能": {
            'Python': 0.95, 'C++': 0.75, 'CUDA': 0.85,
            'TensorFlow': 0.95, 'PyTorch': 0.95, 'Keras': 0.85,
            'Scikit-learn': 0.85, 'OpenCV': 0.75, 'Caffe': 0.65,
            'MXNet': 0.65, 'ONNX': 0.55, 'JAX': 0.75
        },

        "系统开发": {
            'C': 0.95, 'C++': 0.95, 'Rust': 0.85,
            'Assembly': 0.75, 'Linux': 0.65, 'LLVM': 0.65,
            'CMake': 0.55, 'Make': 0.45
        },

        "区块链开发": {
            'Solidity': 0.95, 'Rust': 0.85, 'Go': 0.75,
            'JavaScript': 0.65, 'Python': 0.65, 'C++': 0.65,
            'Web3.js': 0.75, 'Truffle': 0.65, 'Hardhat': 0.65
        },

        "嵌入式系统": {
            'C': 0.95, 'C++': 0.85, 'Rust': 0.75,
            'Assembly': 0.85, 'Python': 0.55, 'Arduino': 0.75,
            'VHDL': 0.65, 'Verilog': 0.65, 'FreeRTOS': 0.75
        }
    }

    # 计算各领域的加权得分
    scores = {}
    for tech, lang_weights in tech_stacks.items():
        score = 0
        for lang in language_details:
            if lang['language'] in lang_weights:
                score += lang['weight'] * lang_weights[lang['language']]
        scores[tech] = score

    # 过滤掉得分为0的领域
    valid_scores = {k: v for k, v in scores.items() if v > 0}

    if not valid_scores:
        return [{"tech": "未知技术栈"}]

    # 按得分排序
    sorted_techs = sorted(valid_scores.items(), key=lambda x: x[1], reverse=True)

    max_score = sorted_techs[0][1]
    threshold = max_score * 0.25

    if len(sorted_techs) == 1:
        threshold = max_score * 0.45

    result = []
    has_frontend = scores.get("前端开发", 0) > 0
    has_backend = scores.get("后端开发", 0) > 0

    # 如果同时具有前端和后端开发,则只返回全栈开发
    if has_frontend and has_backend:
        fullstack_score = (scores["前端开发"] + scores["后端开发"]) / 2
        confidence = min(fullstack_score / max_score, 1.0)
        confidence_percent = round(confidence * 100)
        if confidence_percent >= 50:
            return [{"tech": "全栈开发", "confidence": confidence_percent}]

    # 否则返回原有的技术栈
    for tech, score in sorted_techs:
        if score >= threshold:
            confidence = min(score / max_score, 1.0)
            confidence_percent = round(confidence * 100)
            if confidence_percent >= 50:
                result.append({
                    "tech": tech,
                    "confidence": confidence_percent
                })

    return result if result else [{"tech": "未知技术栈"}]
