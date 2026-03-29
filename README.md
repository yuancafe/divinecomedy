# Dante《神曲》数字阅读（ReadClub）

这是一个基于 [Knowledge2skills](https://github.com/yuancafe/knowledge2skills) 技术栈搭建的示例项目，也可以被看作一本“数字手抄本”。

This repository demonstrates a Knowledge2skills-powered digital reading experience for Dante's *Divine Comedy*. It stitches together multilingual text, guided maps, and knowledge graph data, all served as a static frontend plus a small SQLite data store.

## 项目功能 / Features

- **整歌对读**：展示意大利原文、英文译本和多个中文译文（含译注），允许在 1-4 栏之间切换阅读，并支持列宽拖拽与同步滚动开关。
- **三界地图**：地狱、炼狱与天堂各自的中世纪插画背景上叠加热点，点击能调出对应章节和人物卡片。
- **知识图谱**：区分人物/地点/事件/概念/文本/组织等类别的核心与全图视图，并附带实体词典与注释索引。
- **静态站 + SQLite 双源**：读取预构建的 JSON 文件即可部署，构建脚本同时输出 `divine_comedy.db`，方便后续接入本地 API 或扩展服务。
- **品牌式画廊**：包含精选插图、Dante 肖像、三界总图与史诗谱系视觉页，参考 Digital Dante 与传统羊皮纸视觉。

- **Full bilingual documentation**: README, UI copy and credits show both Chinese and English to mirror the polyglot nature of the source texts.

## 快速上手 / Quick Start

```bash
npm install
npm run build
npm run preview
```

本项目适合部署到 Vercel、Netlify 或任何静态托管平台，同时在本地运行构建脚本会生成所需的 SQLite 数据库 `data/divine_comedy.db`，便于浏览器端或 API Server 查询。

## 致谢 / Credits

感谢 Dante、各位中文译者（王维克、田德望、黄国彬等）、以及知识图谱中使用的数据源。这份数字作品也以 Knowledge2skills 为基础，体现人机共创的力量。
