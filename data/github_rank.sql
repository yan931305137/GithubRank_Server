-- 创建数据库
CREATE DATABASE IF NOT EXISTS github_rank;

-- 使用数据库
USE github_rank;

-- 创建 users 表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户 ID',
    username VARCHAR(255) NOT NULL UNIQUE COMMENT '用户名，用户的唯一标识',
    password VARCHAR(255) NOT NULL COMMENT '密码，用户登录所需',
    email VARCHAR(255) DEFAULT NULL UNIQUE COMMENT '邮箱，用户的联系邮箱',
    github_id VARCHAR(255) UNIQUE COMMENT 'GitHub 用户 ID，用户在 GitHub 的唯一标识',
    status TINYINT DEFAULT 1 COMMENT '用户状态：1-正常，0-禁用，表示用户的当前状态',
    last_login_at DATETIME COMMENT '最后登录时间，记录用户上次登录的时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，记录用户创建的时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，记录用户信息最后一次更新的时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表，存储用户的基本信息';

-- 创建 Github 表
CREATE TABLE IF NOT EXISTS Github (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID，作为主键',
    github_id VARCHAR(255) NOT NULL UNIQUE COMMENT 'GitHub用户的唯一标识符，不能为空',
    user_info JSON COMMENT '用户详细信息，存储为JSON格式，包含用户的个人资料',
    repos_info JSON COMMENT '用户仓库信息，存储为JSON格式，包含用户的所有仓库信息',
    issues_info JSON COMMENT '信息，存储为JSON格式，包含用户的所有问题信息',
    tech_stack JSON COMMENT '用户技术栈信息，存储为JSON格式，记录用户使用的技术栈',
    most_common_language VARCHAR(255) COMMENT '用户最常用的编程语言，最大长度255字符',
    total JSON COMMENT '用户的总计信息，存储为JSON格式，包含用户的统计数据',
    evaluate JSON COMMENT '用户的评价信息，存储为JSON格式，记录用户的评价',
    summa TEXT COMMENT '用户的总结信息，存储为文本，包含用户的总结',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认为当前时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，默认为当前时间，并在更新时自动更新'
) COMMENT='存储GitHub用户信息的表，包含用户的GitHub相关数据';

-- 创建 appraisal 表，并添加级联删除
CREATE TABLE IF NOT EXISTS appraisal (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID，唯一标识每条评价',
    user_id INT NOT NULL COMMENT '用户ID，关联到用户表',
    github_id VARCHAR(255) NOT NULL COMMENT 'GitHub ID，关联到GitHub表',
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 10) COMMENT '评分（1-10），用户对评价的评分',
    message TEXT COMMENT '评价内容，用户对GitHub用户的评价文本',
    avatar_url VARCHAR(255) COMMENT '用户头像URL，用户的头像链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，记录评价创建的时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，记录评价最后一次更新的时间',
    UNIQUE KEY unique_github_user (user_id, github_id) USING BTREE, -- 添加 USING BTREE 以优化索引
    INDEX idx_github_id (github_id) USING BTREE, -- 添加 github_id 的索引，优化查询性能
    INDEX idx_user_id (user_id) USING BTREE,     -- 添加 user_id 的索引，优化查询性能
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- 级联删除，删除用户时删除相关评价
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='用户评价表，存储用户对GitHub用户的评价信息';

-- 创建 weekly_recommend 表
CREATE TABLE IF NOT EXISTS weekly_recommend (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID，作为主键',
    weekly VARCHAR(20) NOT NULL UNIQUE COMMENT '周标识，唯一且不能为空，标识每周的推荐',
    recommendations JSON NOT NULL COMMENT '推荐数据，存储为JSON格式，包含每周的推荐信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认为当前时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，默认为当前时间，并在更新时自动更新'
) COMMENT='存储每周推荐数据的表，包含每周的推荐信息';

-- 创建 daily_recommend 表
CREATE TABLE IF NOT EXISTS daily_recommend (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID，作为主键',
    daily VARCHAR(20) NOT NULL UNIQUE COMMENT '日标识，唯一且不能为空，标识每日的推荐',
    recommendations JSON NOT NULL COMMENT '推荐数据，存储为JSON格式，包含每日的推荐信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认为当前时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，默认为当前时间，并在更新时自动更新'
) COMMENT='存储每日推荐数据的表，包含每日的推荐信息';

-- 创建 monthly_recommend 表
CREATE TABLE IF NOT EXISTS monthly_recommend (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID，作为主键',
    monthly VARCHAR(20) NOT NULL UNIQUE COMMENT '月标识，唯一且不能为空，标识每月的推荐',
    recommendations JSON NOT NULL COMMENT '推荐数据，存储为JSON格式，包含每月的推荐信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认为当前时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，默认为当前时间，并在更新时自动更新'
) COMMENT='存储每月推荐数据的表，包含每月的推荐信息';
