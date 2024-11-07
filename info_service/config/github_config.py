# GitHub API 用户信息 URL
GITHUB_USER_URL = "https://api.github.com/users/{username}"
# GitHub API 用户仓库 URL，按最近推送时间排序
GITHUB_REPOS_URL = "https://api.github.com/users/{username}/repos?sort=pushed"
# GitHub API 用户公开事件 URL
GITHUB_EVENTS_URL = "https://api.github.com/users/{username}/events/public"
# GitHub API 仓库贡献者 URL
GITHUB_CONTRIBUTORS_URL = "https://api.github.com/repos/{username}/{repo}/contributors"
# GitHub API 仓库提交记录 URL
GITHUB_COMMITS_URL = "https://api.github.com/repos/{username}/{repo}/commits"
# GitHub API 用户粉丝 URL
GITHUB_FOLLOWERS_URL = "https://api.github.com/users/{username}/followers"
# GitHub API 用户关注 URL
GITHUB_FOLLOWING_URL = "https://api.github.com/users/{username}/following"
