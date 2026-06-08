# 雅思单词记忆故事

配套书目：《雅思核心词汇精讲精练》（宋鹏昊）  
词源笔记：`D:\E-book\英语学习\宋鹏浩单词课\宋鹏浩1600-Total.docx`

## 目录结构

```
ielts-vocab/
├── notes/        # 从 docx 提取的章节词表
├── stories/      # 每章一个记忆故事
├── docs/         # GitHub Pages 静态网站
├── data/         # 章节词汇 JSON
└── scripts/      # 提取与构建脚本
```

## 使用流程

1. 从 docx 提取某章词汇：
   ```bash
   python3 scripts/extract_from_docx.py          # 默认第 01 章
   python3 scripts/extract_from_docx.py "" 02  # 第 02 章
   ```
2. 在 Cursor 中说：**「用 notes/ch02.md 写第 2 章记忆故事」**
3. 生成网页：
   ```bash
   python3 scripts/build_pages.py 01
   ```
4. 复习：打开 `docs/ch01.html` 或在线 Pages 链接

## 进度

| 章 | 词表 | 故事 | 网页 |
|----|:----:|:----:|:----:|
| 01 | ✅ | ✅ | ✅ |
| 02 | ☐ | ☐ | ☐ |
| … | | | |
| 32 | ☐ | ☐ | ☐ |

## 部署到外网（GitHub Pages）

```bash
# 1. 在 GitHub 新建仓库，例如 ielts-vocab
git init
git add .
git commit -m "第01章记忆故事与 GitHub Pages"
git branch -M main
git remote add origin https://github.com/你的用户名/ielts-vocab.git
git push -u origin main

# 2. GitHub 仓库 → Settings → Pages
#    Source: Deploy from a branch
#    Branch: main / folder: /docs

# 3. 访问 https://你的用户名.github.io/ielts-vocab/
```

## 在 Cursor 中打开

```bash
cursor ~/ielts-vocab
```
