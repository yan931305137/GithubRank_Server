# 定义评分相关的常量
# 提交数的中位数和权重
COMMITS_MEDIAN = 10  # 提交数中位数
COMMITS_WEIGHT = 1.5  # 提交数权重，降低高位

# PR数的中位数和权重
PRS_MEDIAN = 10  # PR数中位数
PRS_WEIGHT = 2.5  # PR数权重，降低高位

# Issue数的中位数和权重
ISSUES_MEDIAN = 25  # Issue数中位数
ISSUES_WEIGHT = 1.5  # Issue数权重，平衡中位

# Review数的中位数和权重
REVIEWS_MEDIAN = 2  # Review数中位数
REVIEWS_WEIGHT = 1.5  # Review数权重，提过低位

# Star数的中位数和权重
STARS_MEDIAN = 50  # Star数中位数
STARS_WEIGHT = 3.5  # Star数权重，降低高位

# Follower数的中位数和权重
FOLLOWERS_MEDIAN = 10  # Follower数中位数
FOLLOWERS_WEIGHT = 1.5  # Follower数权重，提过低位

# 计算总权重基数
TOTAL_WEIGHT_BASE = (
        COMMITS_WEIGHT +  # 提交权重
        PRS_WEIGHT +  # PR权重
        ISSUES_WEIGHT +  # Issue权重
        REVIEWS_WEIGHT +  # Review权重
        STARS_WEIGHT +  # Star权重
        FOLLOWERS_WEIGHT  # Follower权重
)

# 项目重要性和贡献度的权重
PROJECT_IMPORTANCE_WEIGHT = 2.0  # 项目重要性权重
DEVELOPER_CONTRIBUTION_WEIGHT = 2.0  # 开发者贡献度权重

# 项目重要性中位数 (根据实际情况设定)
TOTAL_PROJECT_IMPORTANCE_MEDIAN = 80  # 假设项目的总重要性中位数

# 开发者贡献度中位数 (根据实际情况设定)
TOTAL_CONTRIBUTION_MEDIAN = 80  # 假设贡献度的中位数
