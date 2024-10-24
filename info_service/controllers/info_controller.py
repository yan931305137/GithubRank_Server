from flask import request, jsonify

from info_service.utils.logger_utils import logger
from info_service.services.info_service import get_rank_data, get_user_data, save_user_appraisal, get_user_appraisals


def get_github_rank():
    """
    获取GitHub排名信息。
    """
    try:
        logger.info("开始获取GitHub排名信息")
        rank_data = get_rank_data()  # 假设从服务中获取数据
        logger.info(f"成功获取GitHub排名信息: {rank_data}")
        return rank_data, 200
    except Exception as e:
        logger.error(f"获取GitHub排名信息失败: {e}")
        return jsonify({'error': '获取GitHub排名信息失败'}), 500


def get_user_info(info_id):
    """
    根据用户ID获取用户信息。
    :param info_id: 用户ID
    """
    try:
        logger.info(f"开始获取用户信息，用户ID: {info_id}")
        info_info = get_user_data(info_id)  # 假设从服务中获取数据
        logger.info(f"成功获取用户信息: {info_info}")
        return info_info, 200
    except Exception as e:
        logger.error(f"获取用户信息失败，用户ID: {info_id}, 错误: {e}")
        return jsonify({'error': '获取用户信息失败'}), 500


def save_appraisal(data):
    """
    保存评估数据。
    :param data: 评估数据
    """
    try:
        logger.info(f"开始保存评估数据: {data}")
        save_user_appraisal(data)  # 假设保存数据到服务
        logger.info("评估数据保存成功")
        return jsonify({'message': '评估数据保存成功'}), 201
    except Exception as e:
        logger.error(f"保存评估数据失败: {e}")
        return jsonify({'error': '保存评估数据失败'}), 500


def get_appraisals(info_id):
    """
    获取用户的所有评估。
    :param info_id: 用户ID
    """
    try:
        logger.info(f"开始获取用户评估，用户ID: {info_id}")
        appraisals = get_user_appraisals(info_id)  # 假设从服务中获取数据
        logger.info(f"成功获取用户评估: {appraisals}")
        return appraisals, 200
    except Exception as e:
        logger.error(f"获取用户评估失败，用户ID: {info_id}, 错误: {e}")
        return jsonify({'error': '获取用户评估失败'}), 500
