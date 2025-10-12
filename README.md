# GitHub Repo Activity Recorder

![Animation](generated/overview.svg)

![Animation](generated/3089464667__default-app_status.svg)

![Animation](generated/languages.svg)

## 项目简介
 
**GitHub Repo Activity Recorder** 能够自动统计和可视化你的 GitHub 仓库活跃度和贡献数据，并以 SVG 动态图片的形式展示。

---

## 功能说明

1. **总览统计动图**
   - 自动生成 `generated/overview.svg`，展示你的 GitHub 账号整体统计信息，包括：
     - 用户名
     - 总 star 数
     - 总 fork 数
     - 总贡献次数
     - 总代码变更行数
     - 总仓库数
     - 总页面访问量（views）

2. **语言统计动图**
   - 自动生成 `generated/languages.svg`，展示你所有仓库的主要编程语言占比和颜色分布。

3. **每个仓库的详细活跃度统计**
   - 首次运行时，自动统计每个仓库过去 14 天的总 clone 数和 view 数，并记录初始 star 数。
   - 之后每天自动累加当天的 star 增量、clone 增量和 view 增量。
   - 为每个仓库生成独立的 SVG 状态图片（如 `generated/username__repo_status.svg`），内容包括：
     - 仓库名
     - 累计 star 数
     - 累计 clone 数
     - 累计 view 数

4. **数据持久化**
   - 所有统计数据每日自动累加并保存在 `generated/repo_stats.json`，保证数据不会丢失。

5. **自动化与定时更新**
   - 支持 GitHub Actions 自动化，每天定时（UTC 00:05）北京时间08:05自动统计并更新所有图片和数据。
   - 支持手动触发 workflow，首次运行时自动初始化所有仓库的统计数据。

6. **自定义统计范围**
   - 支持通过环境变量/Secrets 排除指定仓库或指定语言。
   - 支持排除 fork 仓库，仅统计你拥有的仓库。

7. **一键集成到你的 README**
   - 你可以直接在你的个人主页或项目 README 中引用 `generated/overview.svg`、`generated/languages.svg` 以及每个仓库的状态图片，实时展示你的 GitHub 活跃度。

---

## 使用方法

1. **点击use this template按钮创建新仓库，并配置 GitHub Actions Secrets：**
   - （必选）`ACCESS_TOKEN`：你的 GitHub Personal Access Token（需 `repo` 权限）
   - （可选）`EXCLUDED`：排除的仓库名，逗号分隔
   - （可选）`EXCLUDED_LANGS`：排除的语言，逗号分隔
   - （可选）`EXCLUDE_FORKED_REPOS`：如需排除 fork 仓库，设置为 `true`

2. **首次手动运行 `Generate Stats Images` workflow，初始化所有统计数据和图片。**

3. **每天自动定时统计并更新所有图片和数据，无需人工干预。**

4. **在你的模板仓库README 中插入如下内容展示统计动图：**
   ```markdown
   ![](generated/overview.svg)
   ![](generated/languages.svg)
   ![](generated/your_repo_name_status.svg)
   ```
5. **在你的其他仓库（或者主页仓库）的README 中插入如下内容展示统计动图：**
   ```markdown
   ![](https://raw.githubusercontent.com/<你的用户名>/<你的统计仓库名>/main/generated/overview.svg)
![](https://raw.githubusercontent.com/<你的用户名>/<你的统计仓库名>/main/generated/languages.svg)
![](https://raw.githubusercontent.com/<你的用户名>/<你的统计仓库名>/main/generated/<repo>_status.svg)
   ```
6. 如果你喜欢，请给仓库一个star以支持仓库

---

## 功能

- 个人主页展示 GitHub 活跃度和每个仓库的总star数、clone数和view 数（不只是14天，是从第一次在 Actions 页面，手动运行 “Generate Stats Images” workflow 开始，记录的每个仓库的总star数、clone数和view 数）
- 项目 README 展示仓库热度
- 自动化数据归档与可视化

---

# 声明和许可证
本项目基于
[jstrieb/github-stats](https://github.com/jstrieb/github-stats)二次开发，新增功能：展示每个仓库的总star数、clone数和view 数（从第一次在 Actions 页面，手动运行 “Generate Stats Images” workflow 开始，记录的每个仓库的总star数、clone数和view 数），遵循 GNU GPL v3 协议。
