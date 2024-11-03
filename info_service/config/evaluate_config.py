
# 定义评分相关的常量
# 提交数的中位数和权重
COMMITS_MEDIAN = 1000  # 提交数中位数
COMMITS_WEIGHT = 2     # 提交数权重

# PR数的中位数和权重
PRS_MEDIAN = 50       # PR数中位数
PRS_WEIGHT = 3        # PR数权重

# Issue数的中位数和权重
ISSUES_MEDIAN = 25    # Issue数中位数
ISSUES_WEIGHT = 1     # Issue数权重

# Review数的中位数和权重
REVIEWS_MEDIAN = 2    # Review数中位数
REVIEWS_WEIGHT = 1    # Review数权重

# Star数的中位数和权重
STARS_MEDIAN = 50     # Star数中位数
STARS_WEIGHT = 4      # Star数权重

# Follower数的中位数和权重
FOLLOWERS_MEDIAN = 10 # Follower数中位数
FOLLOWERS_WEIGHT = 1  # Follower数权重

# 计算总权重基数
TOTAL_WEIGHT_BASE = (
    COMMITS_WEIGHT +   # 提交权重
    PRS_WEIGHT +      # PR权重
    ISSUES_WEIGHT +   # Issue权重
    REVIEWS_WEIGHT +  # Review权重
    STARS_WEIGHT +    # Star权重
    FOLLOWERS_WEIGHT  # Follower权重
)

# 定义排名阈值和对应等级
THRESHOLDS = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]  # 百分位阈值
LEVELS = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"] # 对应等级
