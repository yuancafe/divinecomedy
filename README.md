# Dante《神曲》数字阅读 / Divine Comedy Digital Reading

这是一个基于 [Knowledge2skills](https://github.com/yuancafe/knowledge2skills) 开发的示例项目，用一套静态站点加轻量数据底座的方式，重做但丁《神曲》的数字阅读体验。

This is a sample project built with [Knowledge2skills](https://github.com/yuancafe/knowledge2skills). It reimagines Dante's *Divine Comedy* as a digital reading experience powered by a static site plus a lightweight data layer.

## 项目简介 / Overview

本项目把《神曲》整理成一个兼具阅读、导览与研究价值的网站，重点展示三界地图、多译本对读、知识图谱和实体词典。

This project turns *The Divine Comedy* into a site that supports reading, navigation, and research. Its core experiences include tripartite world maps, multilingual parallel reading, a knowledge graph, and an entity dictionary.

## 核心功能 / Key Features

- **整歌对读 / Full-canto reading**  
  支持意大利原文、英文译本和多个中文译本的整歌对读，并提供 1-4 栏切换、列宽拖拽和同步滚动开关。  
  Supports canto-level comparison across the Italian original, English translation, and multiple Chinese translations, with 1-4 column switching, resizable columns, and synchronized scrolling.

- **三界地图 / Three-world maps**  
  以地狱、炼狱、天堂三界插图为基础叠加热点，点击即可进入对应章节、人物或事件。  
  Uses infernal, purgatorial, and paradisiacal illustrated maps with hotspots that link directly to relevant cantos, people, and events.

- **知识图谱 / Knowledge graph**  
  按人物、地点、事件、概念、文本等类别组织实体，提供核心图谱、完整图谱和实体卡片。  
  Organizes entities by people, places, events, concepts, texts, and more, with core graph views, full graph views, and entity cards.

- **实体词典 / Entity dictionary**  
  汇总所有重要实体的中文名、意大利文、英文名、类型与出现场次，方便快速检索。  
  Collects major entities with Chinese, Italian, and English names, types, and occurrence references for fast lookup.

- **静态站 + SQLite 双交付 / Static site + SQLite delivery**  
  前端可直接作为静态站部署，构建脚本同时生成 `data/divine_comedy.db`，便于后续扩展本地 API 或检索服务。  
  The frontend can be deployed as a static site, while the build process also produces `data/divine_comedy.db` for future local APIs or search services.

- **中世纪视觉风格 / Medieval visual style**  
  页面采用黑金页眉、羊皮纸质感、雕版插图和中世纪标题字，整体参考 Digital Dante 的数字人文气质。  
  The UI uses a black-and-gold header, parchment textures, woodcut-style illustrations, and medieval display type, inspired by the Digital Dante digital-humanities aesthetic.

## 适合谁使用 / Who It's For

适合想把经典文本做成数字人文网站、想研究《神曲》结构与注释体系，或者想参考 Knowledge2skills 做项目的人。

It is meant for anyone building a digital-humanities site around a classic text, studying the structure and annotations of *The Divine Comedy*, or learning from a Knowledge2skills-based project.

## 快速开始 / Quick Start

```bash
npm install
npm run build
npm run preview
```

## 说明 / Notes

网站可部署到 Vercel、Netlify 或任意静态托管平台。构建时会生成所需的数据文件和 SQLite 数据库，便于后续扩展开发。

The site can be deployed to Vercel, Netlify, or any static hosting platform. The build generates the required data files and SQLite database for future development.

## 致谢 / Credits

感谢 Dante、中文译者与所有相关资料来源，也感谢 [Knowledge2skills](https://github.com/yuancafe/knowledge2skills) 提供的方法论与工作流支持。

Thanks to Dante, the Chinese translators, the source materials used in this project, and [Knowledge2skills](https://github.com/yuancafe/knowledge2skills) for the methodology and workflow behind this work.
