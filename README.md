# 雅思单词记忆故事

配套书目：《雅思核心词汇精讲精练》（宋鹏昊）  
**权威来源**：`D:\E-book\英语学习\宋鹏浩单词课\分章节整理\` 下的 `ch* story.docx`

> 词数、覆盖率、目录标题均以 **story Word 文件** 为准，不对照 `data/chXX.json` 原书词表。

## 在线阅读

**https://dreamsilcon.github.io/ielts-vocab/**

## 目录结构

```
ielts-vocab/
├── reader/       # 交互阅读器（JS/CSS + HTML 构建逻辑，所有章节共用）
├── baseline/     # 写作基线（v3.0 精修版）
├── stories/      # 每章故事（由 story docx 转换）
├── docs/         # GitHub Pages 静态网站
├── notes/        # 原书词表（参考，非权威）
├── data/         # 原书词汇 JSON（参考，非权威）
└── scripts/      # 转换与构建脚本
```

## 阅读器（reader/）

所有章节页面统一使用 `reader/` 模块生成的交互阅读效果：

- **显示中文** — 开关，逐句同步显示译文
- **只高亮生词** — 弱化正文、突出关键词
- **显示全部** — 一次展开本章全文
- **下一句** — 逐句阅读，Part 折叠与进度保存在浏览器

源码在 `reader/assets/`（`reader.js`、`reader.css`），构建时自动同步到 `docs/`。改阅读功能只动 `reader/`，再跑 `build_pages.py` 或 `build_all.py`。

## 使用流程

```bash
# 1. 从 story docx 转换（Windows 路径需在 WSL 可访问）
python3 scripts/convert_story_docx.py 2

# 2. 生成单章网页（含阅读器）
python3 scripts/build_pages.py 02

# 3. 批量重建全部章节 + 同步阅读器资源
python3 scripts/build_all.py

# 4. 刷新首页（标题 + 词数从 stories/ 读取）
python3 scripts/build_index.py

# 统计本章 story 词数
python3 scripts/audit_coverage.py 02
```

## 进度

| 章 | 词表 | 故事 | 网页 | 章 | 词表 | 故事 | 网页 |
|----|:----:|:----:|:----:|----|:----:|:----:|:----:|
| 01 | ✅ | ✅ | ✅ | 17 | ✅ | ✅ | ✅ |
| 02 | ✅ | ✅ | ✅ | 18 | ✅ | ✅ | ✅ |
| 03 | ✅ | ✅ | ✅ | 19 | ✅ | ✅ | ✅ |
| 04 | ✅ | ✅ | ✅ | 20 | ✅ | ✅ | ✅ |
| 05 | ✅ | ✅ | ✅ | 21 | ✅ | ✅ | ✅ |
| 06 | ✅ | ✅ | ✅ | 22 | ✅ | ✅ | ✅ |
| 07 | ✅ | ✅ | ✅ | 23 | ✅ | ✅ | ✅ |
| 08 | ✅ | ✅ | ✅ | 24 | ✅ | ✅ | ✅ |
| 09 | ✅ | ✅ | ✅ | 25 | ✅ | ✅ | ✅ |
| 10 | ✅ | ✅ | ✅ | 26 | ✅ | ✅ | ✅ |
| 11 | ✅ | ✅ | ✅ | 27 | ✅ | ✅ | ✅ |
| 12 | ✅ | ✅ | ✅ | 28 | ✅ | ✅ | ✅ |
| 13 | ✅ | ✅ | ✅ | 29 | — | — | — |
| 14 | ✅ | ✅ | ✅ | 30 | ✅ | ✅ | ✅ |
| 15 | ✅ | ✅ | ✅ | 31 | ✅ | ✅ | ✅ |
| 16 | ✅ | ✅ | ✅ | 32 | — | — | — |

> 第 29、32 章笔记缺失，暂未生成。

## 故事格式

- 全英文故事，关键词 `<b>word</b> /音标/`
- 每段下方中文对照，关键词 **黑体**(english)

## 部署

GitHub → Settings → Pages → Branch: `main` → Folder: `/docs`
