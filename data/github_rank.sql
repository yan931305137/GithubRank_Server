-- 创建数据库
CREATE DATABASE IF NOT EXISTS github_rank;

-- 使用数据库
USE github_rank;

-- 创建 user 表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户 ID',
    username VARCHAR(255) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    email VARCHAR(255) DEFAULT NULL COMMENT '邮箱',
    github_id VARCHAR(255) COMMENT 'GitHub 用户 ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建 Github 表
CREATE TABLE IF NOT EXISTS Github (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID，作为主键',
    github_id VARCHAR(255) NOT NULL UNIQUE COMMENT 'GitHub用户的唯一标识符，不能为空',
    user_info JSON COMMENT '用户详细信息，存储为JSON格式',
    repos_info JSON COMMENT '用户仓库信息，存储为JSON格式',
    tech_stack JSON COMMENT '用户技术栈信息，存储为JSON格式',
    most_common_language VARCHAR(255) COMMENT '用户最常用的编程语言，最大长度255字符',
    total JSON COMMENT '用户的总计信息，存储为JSON格式',
    evaluate JSON COMMENT '用户的评价信息，存储为JSON格式',
    summa TEXT COMMENT '用户的总结信息，存储为文本',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，默认为当前时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，默认为当前时间，并在更新时自动更新'
) COMMENT='存储GitHub用户信息的表';

-- 创建 appraisal 表，并添加级联删除
CREATE TABLE IF NOT EXISTS appraisal (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    user_id INT NOT NULL COMMENT '用户ID',
    github_id VARCHAR(255) NOT NULL COMMENT 'GitHub ID',
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 10) COMMENT '评分（1-10）',
    message TEXT COMMENT '评价内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY unique_github_user (user_id, github_id), -- 防止相同 user_id 和 github_id 的重复记录
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE -- 外键约束，引用 user 表的 id 列，且启用级联删除
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户评价表';
