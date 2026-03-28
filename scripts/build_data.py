#!/usr/bin/env python3

from __future__ import annotations

import json
import html
import hashlib
from io import BytesIO
import re
import ssl
import shutil
import sqlite3
import textwrap
import time
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
PUBLIC_DATA_DIR = PUBLIC_DIR / "data"
PUBLIC_MEDIA_DIR = PUBLIC_DIR / "media"
CORE_GRAPH_MEDIA_DIR = PUBLIC_MEDIA_DIR / "graph-core"
DB_DIR = ROOT / "data"
DB_PATH = DB_DIR / "divine_comedy.db"
REMOTE_JSON_CACHE: dict[str, dict[str, Any]] = {}
REMOTE_BYTES_CACHE: dict[str, bytes] = {}

COMEDY_ROOT = Path("/Users/yuan/Downloads/Comedy")
SKILL_ROOT = Path("/Users/yuan/.agents/skills/divine-comedy-expert/references")
GRAPH_DATA_PATH = SKILL_ROOT / "visualization" / "graph_data.json"
ENTITY_DETAILS_PATH = SKILL_ROOT / "visualization" / "entity_details.json"
COMPARISON_MD_PATH = COMEDY_ROOT / "对比.md"

WORKS: list[dict[str, Any]] = [
    {
        "id": "it_pg1012",
        "kind": "italian",
        "title": "La Divina Commedia",
        "displayTitle": "意大利文原文",
        "translator": "但丁",
        "language": "it",
        "source": str(COMEDY_ROOT / "pg1012-images-3.epub"),
        "format": "epub",
    },
    {
        "id": "en_pg8800",
        "kind": "english",
        "title": "The Divine Comedy",
        "displayTitle": "英文",
        "translator": "Henry Francis Cary / Project Gutenberg",
        "language": "en",
        "source": str(COMEDY_ROOT / "pg8800-images-3.epub"),
        "format": "epub",
    },
    {
        "id": "zh_zhu",
        "kind": "chinese",
        "title": "神曲",
        "displayTitle": "朱维基译本",
        "translator": "朱维基",
        "language": "zh",
        "source": str(
            COMEDY_ROOT
            / "神曲 (译文名著精选) -- 但丁·阿利吉耶里 (Dante Alighieri) -- 2011 -- 上海译文出版社 -- bf364812178f9dd2b875dcc7501384e8 -- Anna’s Archive.epub"
        ),
        "format": "epub",
    },
    {
        "id": "zh_wang",
        "kind": "chinese",
        "title": "神曲：全3册",
        "displayTitle": "王维克译本",
        "translator": "王维克",
        "language": "zh",
        "source": str(
            COMEDY_ROOT
            / "神曲_全3册(133幅插图全新重制,翻译家王维克经典译本,地狱、净界、天堂套装全收录)(果麦经典) -- 但丁 -- 2019 -- cj5_1561 -- aa2b979b12470e8846b5c0f432eb0bc6 -- Anna’s Archive.epub"
        ),
        "format": "epub",
    },
    {
        "id": "zh_tian",
        "kind": "chinese",
        "title": "神曲：地狱篇、炼狱篇、天国篇",
        "displayTitle": "田德望译本",
        "translator": "田德望",
        "language": "zh",
        "source": str(
            COMEDY_ROOT
            / "神曲_地狱篇、炼狱篇、天国篇 (田德望译文集) -- (意)但丁(Dante Alighieri)著; 但丁; 田德望 -- 2015 -- 北京：人民文学出版社 -- 9787020100309 -- 2606e85e7e18412d9bcdfbef7ce2b85b -- Anna’s Archive.epub"
        ),
        "format": "epub",
    },
    {
        "id": "zh_huang",
        "kind": "chinese",
        "title": "神曲（全三册）",
        "displayTitle": "黄国彬译本",
        "translator": "黄国彬",
        "language": "zh",
        "source": str(
            COMEDY_ROOT
            / "神曲(全三册)(知名翻译家黄国彬意大利语原文直译,华语世界首部三韵体《神曲》全译本 理想国出品) -- 但丁·阿利格耶里 黄国彬译 -- Di 1 ban, Haikou, 2021 -- 理想国丨海南出版社 -- 978757.epub"
        ),
        "format": "epub",
    },
]

REALMS = ("inferno", "purgatorio", "paradiso")
REALM_LABELS = {
    "inferno": "地狱篇",
    "purgatorio": "炼狱篇",
    "paradiso": "天堂篇",
}
REALM_ENGLISH = {
    "inferno": "Inferno",
    "purgatorio": "Purgatorio",
    "paradiso": "Paradiso",
}
REALM_SHORT = {
    "inferno": "地狱",
    "purgatorio": "炼狱",
    "paradiso": "天堂",
}
ROMANS = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
    "XXI",
    "XXII",
    "XXIII",
    "XXIV",
    "XXV",
    "XXVI",
    "XXVII",
    "XXVIII",
    "XXIX",
    "XXX",
    "XXXI",
    "XXXII",
    "XXXIII",
    "XXXIV",
]
CN_NUMBERS = {
    1: "第一",
    2: "第二",
    3: "第三",
    4: "第四",
    5: "第五",
    6: "第六",
    7: "第七",
    8: "第八",
    9: "第九",
    10: "第十",
    11: "第十一",
    12: "第十二",
    13: "第十三",
    14: "第十四",
    15: "第十五",
    16: "第十六",
    17: "第十七",
    18: "第十八",
    19: "第十九",
    20: "第二十",
    21: "第二十一",
    22: "第二十二",
    23: "第二十三",
    24: "第二十四",
    25: "第二十五",
    26: "第二十六",
    27: "第二十七",
    28: "第二十八",
    29: "第二十九",
    30: "第三十",
    31: "第三十一",
    32: "第三十二",
    33: "第三十三",
    34: "第三十四",
}

ABOUT_SECTIONS = [
    {
        "title": "百歌结构与三界布局",
        "body": "《神曲》由一百歌组成。第一歌既是引言，也是整部旅程的暗夜起点；其后地狱篇、炼狱篇、天堂篇各三十三歌，分别对应罪、净化与救赎。这样的布局让整部作品既像一部宇宙史诗，也像一部被严格编排的灵魂地理学：读者不是在抽象概念里游走，而是在一层层可进入、可辨识、可比较的空间之中向前推进。",
    },
    {
        "title": "数字秩序与三位一体",
        "body": "三部、各三十三歌、整书一百歌，这些数字并不是装饰，而是《神曲》结构感的来源。三这个数字不断回返，对应基督教的三位一体；九圈地狱、七层炼狱、九重天则把宗教宇宙秩序转化为读者可感的节奏。数字在这里既是神学象征，也是文学组织原则，让诗歌的推进具有近乎建筑般的稳定感。",
    },
    {
        "title": "三行连锁韵",
        "body": "《神曲》最著名的形式特征是 Terza Rima，也就是三行连锁韵：ABA、BCB、CDC、DED。每个三行节的中间韵脚都会带入下一节，使整首诗形成链式向前的韵律。它的效果不是单纯好听，而是制造出持续前行的阅读动势，像旅程本身一样，一步步把读者牵进更深的空间与思想之中。",
    },
    {
        "title": "十一音节诗行",
        "body": "但丁使用的是意大利诗歌传统中的 Endecasillabo，即十一音节诗行。十一音节给予诗行足够的呼吸长度，既能承载叙事，也能容纳思辨与祈祷式抒情。和三行连锁韵结合之后，《神曲》形成了一种兼具建筑感与流动感的节奏：每一行都稳，每一节又都在推动下一节继续向前。",
    },
    {
        "title": "俗语写作与语言革命",
        "body": "在那个时代，神学与严肃学术多用拉丁文书写，但丁却选择托斯卡纳俗语来写《神曲》。这个决定使作品不再只是学者内部传阅的拉丁文本，而成为能够直接触及普通读者与市民世界的诗歌。正因为如此，《神曲》不只是伟大的文学作品，也被视为现代意大利语的奠基性文本，类似莎士比亚之于英语文学史的意义。",
    },
    {
        "title": "为什么叫“喜剧”",
        "body": "但丁最初给这部作品起名为 Comedìa。按古典传统，喜剧并不等于幽默搞笑，而是指从黑暗、迷失或卑下状态出发，最终抵达光明、秩序与圆满的作品；悲剧则相反，是从高处坠落到破败与毁灭。后来薄伽丘在其前加上 Divina，才逐渐形成今天熟悉的《神曲》之名。这个标题本身已经提示了全书的运动方向：从迷失到得救。",
    },
    {
        "title": "宗教宇宙与道德地图",
        "body": "《神曲》当然是一部宗教作品，但它的力量并不止于教义说明。地狱、炼狱与天堂并不是抽象背景，而是一张完整的道德地图：罪如何使灵魂下沉，悔罪如何让灵魂攀升，福乐如何接近神圣光明，全部都被空间化、层级化了。这种写法让抽象的神学判断转化为可见、可行走、可记忆的图像系统，也让作品带有近乎“心理测试”般的自我审视强度。",
    },
    {
        "title": "时代背景与流放经验",
        "body": "《神曲》诞生于中世纪晚期的意大利城邦世界：佛罗伦萨商业繁荣、党争激烈，教皇与帝国的权力冲突不断加剧。但丁既是诗人，也是深度卷入公共生活的政治人物。1302 年被判终身流放后，他再也无法回到故乡。正是流放的痛苦、不公和失乡感，让《神曲》从一部宗教旅程诗变成了带有自我辩护、政治记忆与文明诊断意味的伟大作品；它因此被视为中世纪的总结，也是通向文艺复兴与现代主体意识的桥梁。",
    },
]

DANTE_TIMELINE = [
    {"year": "1265", "title": "生于佛罗伦萨", "body": "但丁出生在佛罗伦萨，成长于商业繁荣、政治撕裂与宗教权威并存的意大利城邦世界。"},
    {"year": "1274", "title": "初见贝雅特丽齐", "body": "贝雅特丽齐成为但丁诗学、伦理和救赎想象的中心人物。"},
    {"year": "1289", "title": "参战与进入公共生活", "body": "但丁在战场和城邦政治中接受现实教育，开始理解暴力、秩序与权力。"},
    {"year": "1302", "title": "流放", "body": "黑白党争和教皇政治使但丁被判永久流放，失乡经验成为《神曲》的深层情感引擎。"},
    {"year": "1308-1321", "title": "写作《神曲》", "body": "在长期流徙中，但丁把私人遭遇、神学宇宙和意大利政治熔铸成百歌旅程。"},
    {"year": "1321", "title": "卒于拉文纳", "body": "但丁未能回到佛罗伦萨，却以《神曲》重塑了意大利文学和西方史诗传统。"},
]

HERO = {
    "title": "但丁《神曲》数字阅读",
    "subtitle": "《神曲》地图、整歌对读与知识图谱 | Digital Dante Museum",
    "quote": "Nel mezzo del cammin di nostra vita",
}

ILLUSTRATION_SPECS = [
    {
        "id": "home-hero-domenico",
        "source": PUBLIC_MEDIA_DIR / "Dante_Domenico_di_Michelino.jpg",
        "title": "多梅尼科·迪·米凯利诺《但丁与三界》",
        "credit": "public media / 主页主图",
        "usage": ["home"],
    },
    {
        "id": "overview-medieval",
        "source": COMEDY_ROOT / "the-universe-according-to-dante-999x1444-v0-izFW3D8TfQajMGBUqiJIAf3n2CAAHXI0vlIB_r9OcAg.webp",
        "title": "三界宇宙结构图",
        "credit": "素材文件夹 / 宇宙结构图",
        "usage": ["home", "overview"],
    },
    {
        "id": "overview-structure",
        "source": COMEDY_ROOT / "map-of-purgatory-from-dante-alighieris-commedia-circa-1290-v0-xkegj0r7wsc51.webp",
        "title": "三界古地图总览",
        "credit": "素材文件夹 / 古地图扫描",
        "usage": ["home", "overview"],
    },
    {
        "id": "inferno-medieval",
        "source": PUBLIC_MEDIA_DIR / "inferno-medieval.jpg",
        "title": "地狱篇中世纪插图",
        "credit": "public media / 地狱篇插图",
        "usage": ["inferno", "graph"],
    },
    {
        "id": "overview-inferno-menu",
        "source": PUBLIC_MEDIA_DIR / "commento-menu-inferno.jpg",
        "title": "地狱篇总图",
        "credit": "Commento 古图 / public media",
        "usage": ["home", "overview"],
    },
    {
        "id": "inferno-structure",
        "source": COMEDY_ROOT / "5fdf8db1cb13495409235789ab068558d109b2dedc8f.jpeg",
        "title": "地狱结构示意",
        "credit": "素材文件夹 / 地狱结构图",
        "usage": ["home", "inferno"],
    },
    {
        "id": "purgatorio-medieval",
        "source": PUBLIC_MEDIA_DIR / "purgatorio-medieval.jpg",
        "title": "炼狱篇中世纪插图",
        "credit": "public media / 炼狱篇插图",
        "usage": ["purgatorio", "graph"],
    },
    {
        "id": "overview-purgatorio-menu",
        "source": PUBLIC_MEDIA_DIR / "commento-menu-purgatorio.jpg",
        "title": "炼狱篇总图",
        "credit": "Commento 古图 / public media",
        "usage": ["home", "overview"],
    },
    {
        "id": "purgatorio-structure",
        "source": COMEDY_ROOT / "35a85edf8db1cb13495480fe201c414e9258d009dd8f.jpeg",
        "title": "炼狱结构示意",
        "credit": "素材文件夹 / 炼狱结构图",
        "usage": ["home", "purgatorio"],
    },
    {
        "id": "paradiso-medieval",
        "source": PUBLIC_MEDIA_DIR / "paradiso-medieval.jpg",
        "title": "天堂篇中世纪插图",
        "credit": "public media / 天堂篇插图",
        "usage": ["paradiso", "graph"],
    },
    {
        "id": "overview-paradiso-menu",
        "source": PUBLIC_MEDIA_DIR / "commento-menu-paradiso.jpg",
        "title": "天堂篇总图",
        "credit": "Commento 古图 / public media",
        "usage": ["home", "overview"],
    },
    {
        "id": "paradiso-structure",
        "source": COMEDY_ROOT / "6a00d83542d51e69e2014e61068874970c.jpg",
        "title": "天堂结构示意",
        "credit": "素材文件夹 / 天堂结构图",
        "usage": ["home", "paradiso"],
    },
    {
        "id": "dante-portrait",
        "source": PUBLIC_MEDIA_DIR / "dante-portrait.jpeg",
        "title": "但丁肖像",
        "credit": "田德望译本插图 / public media",
        "usage": ["dante", "about"],
    },
    {
        "id": "dante-diagram",
        "source": PUBLIC_MEDIA_DIR / "dante-diagram.webp",
        "title": "但丁宇宙结构图",
        "credit": "public media / 结构配图",
        "usage": ["dante", "about", "graph"],
    },
    {
        "id": "purgatory-plan",
        "source": COMEDY_ROOT / "Purgatory_Plan.png",
        "title": "炼狱层级示意",
        "credit": "素材文件夹 / 炼狱层级图",
        "usage": ["about", "purgatorio"],
    },
]

CORE_GRAPH_IMAGE_SPECS: dict[str, dict[str, str]] = {
    "但丁": {"page": "Dante_Alighieri", "title": "但丁肖像", "credit": "Wikimedia Commons / Wikipedia"},
    "维吉尔": {"page": "Virgil", "title": "维吉尔肖像", "credit": "Wikimedia Commons / Wikipedia"},
    "Ugolino": {"page": "Ugolino_della_Gherardesca", "title": "乌戈利诺配图", "credit": "Wikimedia Commons / Wikipedia"},
    "featured:paolo": {"page": "Paolo_Malatesta", "title": "保罗配图", "credit": "Wikimedia Commons / Wikipedia"},
    "featured:cacciaguida": {"page": "Cacciaguida", "title": "卡恰圭达配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Bernardin": {"page": "Bernard_of_Clairvaux", "title": "圣伯尔纳配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Cato": {"page": "Cato_the_Younger", "title": "小加图配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Ulysses": {"page": "Odysseus", "title": "尤利西斯配图", "credit": "Wikimedia Commons / Wikipedia"},
    "featured:francesca": {"page": "Francesca_da_Rimini", "title": "弗兰切斯卡配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Statius": {
        "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Publio%20Papinio%20Stazio%20(cropped).png",
        "title": "斯塔提乌斯配图",
        "credit": "Wikimedia Commons / Wikipedia",
        "source": "Publio Papinio Stazio (cropped).png",
    },
    "featured:justinian": {"page": "Justinian_I", "title": "查士丁尼配图", "credit": "Wikimedia Commons / Wikipedia"},
    "featured:farinata": {"page": "Farinata_degli_Uberti", "title": "法里纳塔配图", "credit": "Wikimedia Commons / Wikipedia"},
    "featured:matelda": {"page": "Matilda_of_Tuscany", "title": "玛泰尔妲配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Piccarda": {
        "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Par%2003,%20Gustave%20Dor%C3%A9,%20piccarda.jpg",
        "title": "皮卡尔达配图",
        "credit": "Wikimedia Commons / Gustave Dore",
        "source": "Par 03, Gustave Doré, piccarda.jpg",
    },
    "person-beatrice": {"page": "Beatrice_Portinari", "title": "贝雅特丽齐配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Lucifer": {"page": "Lucifer", "title": "路西法配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Minos": {"page": "Minos", "title": "弥诺斯配图", "credit": "Wikimedia Commons / Wikipedia"},
    "realm-inferno": {"page": "Inferno_(Dante)", "title": "地狱篇配图", "credit": "Wikimedia Commons / Wikipedia"},
    "realm-paradiso": {"page": "Paradiso_(Dante)", "title": "天堂篇配图", "credit": "Wikimedia Commons / Wikipedia"},
    "place-florence": {"page": "Florence", "title": "佛罗伦萨配图", "credit": "Wikimedia Commons / Wikipedia"},
    "realm-purgatorio": {"page": "Purgatorio", "title": "炼狱篇配图", "credit": "Wikimedia Commons / Wikipedia"},
    "意大利": {"page": "Italy", "title": "意大利配图", "credit": "Wikimedia Commons / Wikipedia"},
    "罗马涅": {"page": "Romagna", "title": "罗马涅配图", "credit": "Wikimedia Commons / Wikipedia"},
    "天体": {"page": "Celestial_spheres", "title": "天体配图", "credit": "Wikimedia Commons / Wikipedia"},
    "托斯卡纳": {"page": "Tuscany", "title": "托斯卡纳配图", "credit": "Wikimedia Commons / Wikipedia"},
    "罗马": {"page": "Rome", "title": "罗马配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Adamo": {"page": "Counterfeit_coin", "title": "阿达莫配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Arno": {"page": "Arno", "title": "阿诺河流域配图", "credit": "Wikimedia Commons / Wikipedia"},
    "阿诺河": {"page": "Arno", "title": "阿诺河配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Acheron": {"page": "Acheron", "title": "阿刻戎河配图", "credit": "Wikimedia Commons / Wikipedia"},
    "Cocytus": {"page": "Cocytus", "title": "科库托斯配图", "credit": "Wikimedia Commons / Wikipedia"},
    "底比斯": {"page": "Thebes,_Greece", "title": "底比斯配图", "credit": "Wikimedia Commons / Wikipedia"},
    "裂缝": {"page": "Chasm", "title": "裂缝配图", "credit": "Wikimedia Commons / Wikipedia"},
    "锡耶纳": {"page": "Siena", "title": "锡耶纳配图", "credit": "Wikimedia Commons / Wikipedia"},
    "忘川": {"page": "Lethe", "title": "忘川配图", "credit": "Wikimedia Commons / Wikipedia"},
    "炼狱山": {"page": "Purgatory", "title": "炼狱山配图", "credit": "Wikimedia Commons / Wikipedia"},
    "战车": {"page": "Chariot", "title": "战车配图", "credit": "Wikimedia Commons / Wikipedia"},
    "追逐": {"page": "Wild_Hunt", "title": "追逐配图", "credit": "Wikimedia Commons / Wikipedia"},
    "concept-soul": {"page": "Soul", "title": "灵魂配图", "credit": "Wikimedia Commons / Wikipedia"},
    "concept-god": {"page": "God_the_Father", "title": "上帝配图", "credit": "Wikimedia Commons / Wikipedia"},
    "concept-truth": {"page": "Truth_Coming_Out_of_Her_Well", "title": "真理配图", "credit": "Wikimedia Commons / Wikipedia"},
    "圣灵": {"page": "Holy_Spirit_in_Christianity", "title": "圣灵配图", "credit": "Wikimedia Commons / Wikipedia"},
    "concept-love": {"page": "Cupid_and_Psyche", "title": "爱配图", "credit": "Wikimedia Commons / Wikipedia"},
    "誓言": {"page": "Oath_of_the_Horatii", "title": "誓言配图", "credit": "Wikimedia Commons / Wikipedia"},
    "恶魔": {"page": "Devil", "title": "恶魔配图", "credit": "Wikimedia Commons / Wikipedia"},
    "罪犯": {"page": "The_Prisoners_(Goya)", "title": "罪犯配图", "credit": "Wikimedia Commons / Wikipedia"},
    "自由意志": {"page": "The_Choice_of_Hercules_(Carracci)", "title": "自由意志配图", "credit": "Wikimedia Commons / Wikipedia"},
    "work-divine-comedy": {"page": "Divine_Comedy", "title": "神曲配图", "credit": "Wikimedia Commons / Wikipedia"},
    "圣灵": {"page": "Holy_Spirit_in_Christianity", "title": "圣灵配图", "credit": "Wikimedia Commons / Wikipedia"},
    "大理石": {"page": "Marble", "title": "大理石配图", "credit": "Wikimedia Commons / Wikipedia"},
}

REGION_DEFS = {
    "inferno": [
        ("dark-forest", "黑暗森林与入口", (1, 1), {"x": 10, "y": 6, "w": 80, "h": 9}),
        ("gate", "前庭、阿刻戎河与地狱之门", (2, 3), {"x": 11, "y": 15, "w": 78, "h": 10}),
        ("limbo", "第一圈 灵薄狱", (4, 4), {"x": 14, "y": 24, "w": 72, "h": 8}),
        ("lust", "第二圈 色欲", (5, 5), {"x": 16, "y": 32, "w": 68, "h": 7}),
        ("gluttony", "第三圈 暴食", (6, 6), {"x": 18, "y": 39, "w": 64, "h": 7}),
        ("greed-anger", "第四至五圈 贪婪与愤怒", (7, 8), {"x": 20, "y": 46, "w": 60, "h": 9}),
        ("heresy", "第六圈 异端", (9, 11), {"x": 22, "y": 55, "w": 56, "h": 9}),
        ("violence", "第七圈 暴力", (12, 17), {"x": 25, "y": 64, "w": 50, "h": 11}),
        ("fraud", "第八圈 欺诈", (18, 30), {"x": 29, "y": 75, "w": 42, "h": 13}),
        ("treachery", "第九圈 背叛与冰湖", (31, 34), {"x": 36, "y": 88, "w": 28, "h": 10}),
    ],
    "purgatorio": [
        ("shore", "海岸与前炼狱", (1, 9), {"x": 34, "y": 84, "w": 46, "h": 11}),
        ("gate", "炼狱之门", (9, 10), {"x": 42, "y": 68, "w": 10, "h": 8}),
        ("terrace-1", "第一层 傲慢", (10, 12), {"x": 44, "y": 61, "w": 15, "h": 6}),
        ("terrace-2", "第二层 嫉妒", (13, 15), {"x": 47, "y": 54, "w": 16, "h": 6}),
        ("terrace-3", "第三层 愤怒", (15, 17), {"x": 49, "y": 48, "w": 17, "h": 6}),
        ("terrace-4", "第四层 懒惰", (18, 19), {"x": 51, "y": 41, "w": 16, "h": 6}),
        ("terrace-5", "第五层 贪婪", (19, 22), {"x": 52, "y": 35, "w": 16, "h": 6}),
        ("terrace-6", "第六层 暴食", (22, 24), {"x": 54, "y": 29, "w": 15, "h": 6}),
        ("terrace-7", "第七层 色欲", (25, 27), {"x": 56, "y": 23, "w": 14, "h": 6}),
        ("earthly-paradise", "地上乐园", (28, 33), {"x": 57, "y": 10, "w": 18, "h": 10}),
    ],
    "paradiso": [
        ("moon", "月球天", (1, 5), {"x": 53, "y": 84, "w": 10, "h": 6}),
        ("mercury", "水星天", (5, 7), {"x": 50, "y": 77, "w": 16, "h": 6}),
        ("venus", "金星天", (8, 9), {"x": 47, "y": 69, "w": 20, "h": 6}),
        ("sun", "太阳天", (10, 14), {"x": 42, "y": 60, "w": 28, "h": 6}),
        ("mars", "火星天", (14, 18), {"x": 38, "y": 51, "w": 34, "h": 6}),
        ("jupiter", "木星天", (18, 20), {"x": 35, "y": 43, "w": 40, "h": 6}),
        ("saturn", "土星天", (21, 22), {"x": 32, "y": 35, "w": 45, "h": 6}),
        ("fixed-stars", "恒星天", (23, 27), {"x": 26, "y": 24, "w": 56, "h": 8}),
        ("primum-mobile", "原动天", (28, 29), {"x": 22, "y": 14, "w": 63, "h": 6}),
        ("empyrean", "至高天与白色玫瑰", (30, 33), {"x": 31, "y": 4, "w": 46, "h": 7}),
    ],
}

FEATURED_ENTITY_SPECS = [
    {
        "canonical": "virgil",
        "match": ["Virgil", "维吉尔"],
        "fallback": {
            "nameZh": "维吉尔",
            "nameEn": "Virgil",
            "nameIt": "Virgilio",
            "description": "罗马诗人，但丁在地狱与炼狱中的向导。",
            "category": "Person",
            "aliases": ["Virgil", "Virgilio", "Vergil", "维吉尔"],
            "occurrences": [1, 2, 3, 4, 5, 34, 35, 36, 37, 38, 63],
        },
    },
    {
        "canonical": "beatrice",
        "match": ["Beatrice", "贝雅特丽"],
        "fallback": {
            "nameZh": "贝雅特丽齐",
            "nameEn": "Beatrice",
            "nameIt": "Beatrice",
            "description": "但丁的精神恋人，也是他在天堂中的引导者。",
            "category": "Person",
            "aliases": ["Beatrice", "Beatrix", "贝雅特丽齐", "贝缇丽彩"],
            "occurrences": [2, 30, 31, 32, 63, 64, 68, 69, 70, 71],
        },
    },
    {
        "canonical": "dante",
        "match": ["Dante", "但丁"],
        "fallback": {
            "nameZh": "但丁",
            "nameEn": "Dante",
            "nameIt": "Dante",
            "description": "《神曲》的作者与叙述主体，三界旅程的见证者。",
            "category": "Person",
            "aliases": ["Dante", "但丁"],
            "occurrences": [1, 2, 35, 68],
        },
    },
    {
        "canonical": "francesca",
        "match": ["Francesca"],
        "fallback": {
            "nameZh": "弗兰切斯卡",
            "nameEn": "Francesca da Rimini",
            "nameIt": "Francesca",
            "description": "第二圈色欲者中最著名的女性亡魂，与保罗同受风暴卷挟。",
            "category": "Person",
            "aliases": ["Francesca", "Francesca da Rimini", "弗兰切斯卡"],
            "occurrences": [5],
        },
    },
    {
        "canonical": "paolo",
        "match": ["Paolo"],
        "fallback": {
            "nameZh": "保罗",
            "nameEn": "Paolo",
            "nameIt": "Paolo",
            "description": "与弗兰切斯卡相恋的灵魂，一同在第二圈受罚。",
            "category": "Person",
            "aliases": ["Paolo", "保罗"],
            "occurrences": [5],
        },
    },
    {
        "canonical": "farinata",
        "match": ["Farinata"],
        "fallback": {
            "nameZh": "法里纳塔",
            "nameEn": "Farinata",
            "nameIt": "Farinata",
            "description": "第六圈异端者中高大的佛罗伦萨贵族。",
            "category": "Person",
            "aliases": ["Farinata", "法里纳塔"],
            "occurrences": [10],
        },
    },
    {
        "canonical": "ulysses",
        "match": ["Ulysses"],
        "fallback": {
            "nameZh": "尤利西斯",
            "nameEn": "Ulysses",
            "nameIt": "Ulisse",
            "description": "第八圈中最著名的谋略者之一，以越界的求知欲著称。",
            "category": "Person",
            "aliases": ["Ulysses", "Ulisse", "尤利西斯"],
            "occurrences": [26],
        },
    },
    {
        "canonical": "lucifer",
        "match": ["Lucifer"],
        "fallback": {
            "nameZh": "路西法",
            "nameEn": "Lucifer",
            "nameIt": "Lucifero",
            "description": "地狱最深处的堕天使，被冻在科库托斯中心。",
            "category": "Person",
            "aliases": ["Lucifer", "Lucifero", "路西法"],
            "occurrences": [34],
        },
    },
    {
        "canonical": "cato",
        "match": ["Cato"],
        "fallback": {
            "nameZh": "小加图",
            "nameEn": "Cato",
            "nameIt": "Catone",
            "description": "炼狱山脚的守卫者，象征自由与道德坚贞。",
            "category": "Person",
            "aliases": ["Cato", "Catone", "小加图"],
            "occurrences": [35],
        },
    },
    {
        "canonical": "statius",
        "match": ["Statius"],
        "fallback": {
            "nameZh": "斯塔提乌斯",
            "nameEn": "Statius",
            "nameIt": "Stazio",
            "description": "在炼狱后段加入旅程的诗人。",
            "category": "Person",
            "aliases": ["Statius", "Stazio", "斯塔提乌斯"],
            "occurrences": [51, 52, 53, 54],
        },
    },
    {
        "canonical": "matelda",
        "match": ["Matelda", "Matelda"],
        "fallback": {
            "nameZh": "玛泰尔妲",
            "nameEn": "Matelda",
            "nameIt": "Matelda",
            "description": "地上乐园中的女性形象，引导但丁理解忘川与忆涧。",
            "category": "Person",
            "aliases": ["Matelda", "玛泰尔妲"],
            "occurrences": [62, 63, 64],
        },
    },
    {
        "canonical": "piccarda",
        "match": ["Piccarda"],
        "fallback": {
            "nameZh": "皮卡尔达",
            "nameEn": "Piccarda",
            "nameIt": "Piccarda",
            "description": "天堂月球天中的首位福灵，讲述誓愿与自由意志。",
            "category": "Person",
            "aliases": ["Piccarda", "皮卡尔达"],
            "occurrences": [70, 71],
        },
    },
    {
        "canonical": "justinian",
        "match": ["Justinian"],
        "fallback": {
            "nameZh": "查士丁尼",
            "nameEn": "Justinian",
            "nameIt": "Giustiniano",
            "description": "天堂水星天中的皇帝灵魂，讲述罗马历史与帝国使命。",
            "category": "Person",
            "aliases": ["Justinian", "Giustiniano", "查士丁尼"],
            "occurrences": [73],
        },
    },
    {
        "canonical": "cacciaguida",
        "match": ["Cacciaguida"],
        "fallback": {
            "nameZh": "卡恰圭达",
            "nameEn": "Cacciaguida",
            "nameIt": "Cacciaguida",
            "description": "但丁的祖先，在火星天中预言诗人的流放与使命。",
            "category": "Person",
            "aliases": ["Cacciaguida", "卡恰圭达"],
            "occurrences": [81, 82, 83, 84, 85],
        },
    },
    {
        "canonical": "bernard",
        "match": ["Bernard"],
        "fallback": {
            "nameZh": "圣伯尔纳",
            "nameEn": "Saint Bernard",
            "nameIt": "Bernardo",
            "description": "天堂终章中的最后引导者，引领但丁观看白色玫瑰与神视。",
            "category": "Person",
            "aliases": ["Bernard", "Bernardo", "伯尔纳", "圣伯尔纳"],
            "occurrences": [99, 100],
        },
    },
    {
        "canonical": "minos",
        "match": ["Minos"],
        "fallback": {
            "nameZh": "弥诺斯",
            "nameEn": "Minos",
            "nameIt": "Minosse",
            "description": "在第二圈前审判灵魂的古代法官，以尾巴缠绕次数判定圈层。",
            "category": "Person",
            "aliases": ["Minos", "Minosse", "弥诺斯"],
            "occurrences": [5],
        },
    },
    {
        "canonical": "ugolino",
        "match": ["Ugolino"],
        "fallback": {
            "nameZh": "乌戈利诺",
            "nameEn": "Ugolino",
            "nameIt": "Ugolino",
            "description": "第九圈中最著名的背叛者与受害者形象之一。",
            "category": "Person",
            "aliases": ["Ugolino", "乌戈利诺"],
            "occurrences": [33],
        },
    },
    {
        "canonical": "dark-forest-event",
        "match": [],
        "fallback": {
            "nameZh": "黑暗森林的迷失",
            "nameEn": "The Dark Wood",
            "nameIt": "Selva Oscura",
            "description": "全诗开篇的迷途事件，标志着灵魂与道路的危机。",
            "category": "Event",
            "aliases": ["dark wood", "selva oscura", "黑暗森林"],
            "occurrences": [1],
        },
    },
    {
        "canonical": "purgatory-gate-event",
        "match": [],
        "fallback": {
            "nameZh": "进入炼狱之门",
            "nameEn": "The Gate of Purgatory",
            "nameIt": "Porta del Purgatorio",
            "description": "但丁正式进入炼狱的门槛时刻。",
            "category": "Event",
            "aliases": ["gate of purgatory", "炼狱之门"],
            "occurrences": [45],
        },
    },
]

SCENE_HOTSPOTS = {
    "inferno": [
        {"id": "inferno-virgil", "label": "维吉尔", "entity": "virgil", "x": 18, "y": 18, "kind": "entity"},
        {"id": "inferno-dark-wood", "label": "迷失", "entity": "dark-forest-event", "x": 80, "y": 10, "kind": "event"},
        {"id": "inferno-minos", "label": "弥诺斯", "entity": "minos", "x": 29, "y": 31, "kind": "entity"},
        {"id": "inferno-francesca", "label": "弗兰切斯卡", "entity": "francesca", "x": 72, "y": 26, "kind": "entity"},
        {"id": "inferno-farinata", "label": "法里纳塔", "entity": "farinata", "x": 71, "y": 58, "kind": "entity"},
        {"id": "inferno-ulysses", "label": "尤利西斯", "entity": "ulysses", "x": 56, "y": 79, "kind": "entity"},
        {"id": "inferno-ugolino", "label": "乌戈利诺", "entity": "ugolino", "x": 42, "y": 92, "kind": "entity"},
        {"id": "inferno-lucifer", "label": "路西法", "entity": "lucifer", "x": 56, "y": 97, "kind": "entity"},
    ],
    "purgatorio": [
        {"id": "purgatorio-cato", "label": "小加图", "entity": "cato", "x": 27, "y": 84, "kind": "entity"},
        {"id": "purgatorio-gate-event", "label": "炼狱之门", "entity": "purgatory-gate-event", "x": 49, "y": 72, "kind": "event"},
        {"id": "purgatorio-virgil", "label": "维吉尔", "entity": "virgil", "x": 40, "y": 82, "kind": "entity"},
        {"id": "purgatorio-statius", "label": "斯塔提乌斯", "entity": "statius", "x": 61, "y": 36, "kind": "entity"},
        {"id": "purgatorio-matelda", "label": "玛泰尔妲", "entity": "matelda", "x": 74, "y": 13, "kind": "entity"},
        {"id": "purgatorio-beatrice", "label": "贝雅特丽齐", "entity": "beatrice", "x": 67, "y": 7, "kind": "entity"},
    ],
    "paradiso": [
        {"id": "paradiso-beatrice", "label": "贝雅特丽齐", "entity": "beatrice", "x": 60, "y": 83, "kind": "entity"},
        {"id": "paradiso-piccarda", "label": "皮卡尔达", "entity": "piccarda", "x": 51, "y": 80, "kind": "entity"},
        {"id": "paradiso-justinian", "label": "查士丁尼", "entity": "justinian", "x": 56, "y": 74, "kind": "entity"},
        {"id": "paradiso-cacciaguida", "label": "卡恰圭达", "entity": "cacciaguida", "x": 52, "y": 52, "kind": "entity"},
        {"id": "paradiso-bernard", "label": "圣伯尔纳", "entity": "bernard", "x": 64, "y": 10, "kind": "entity"},
    ],
}

NOTELESS_WORK_IDS = {"zh_huang"}
NUMBERED_NOTES_WORK_IDS = {"zh_wang", "zh_tian"}

ENTITY_MERGE_GROUPS = [
    {
        "id": "realm-inferno",
        "aliases": ["地狱", "Inferno", "Hell"],
        "nameZh": "地狱",
        "nameIt": "Inferno",
        "nameEn": "Inferno",
        "category": "Place",
        "description": "《神曲》三界中的第一界，自黑暗森林与地狱之门一路下降到科库托斯与路西法。",
    },
    {
        "id": "realm-purgatorio",
        "aliases": ["炼狱", "净界", "Purgatorio", "Purgatory"],
        "nameZh": "炼狱",
        "nameIt": "Purgatorio",
        "nameEn": "Purgatory",
        "category": "Place",
        "description": "《神曲》三界中的第二界，自海岸与前炼狱一路上升到地上乐园。",
    },
    {
        "id": "realm-paradiso",
        "aliases": ["天堂", "天国", "Paradiso", "Paradise", "Heaven"],
        "nameZh": "天堂",
        "nameIt": "Paradiso",
        "nameEn": "Paradise",
        "category": "Place",
        "description": "《神曲》三界中的第三界，穿越九重天球并抵达白色玫瑰与至高天。",
    },
    {
        "id": "work-divine-comedy",
        "aliases": ["神曲", "Divine Comedy", "Divina Commedia", "The_Divine_Comedy", "The Divine Comedy"],
        "nameZh": "神曲",
        "nameIt": "Divina Commedia",
        "nameEn": "Divine Comedy",
        "category": "Document",
        "description": "但丁的百歌史诗，由《地狱篇》《炼狱篇》《天堂篇》三部分构成。",
    },
    {
        "id": "being-angel",
        "aliases": ["天使", "Angel", "Angels"],
        "nameZh": "天使",
        "nameIt": "Angelo",
        "nameEn": "Angel",
        "category": "Person",
        "description": "《神曲》中承担引导、看守与显现职责的天界灵体。",
    },
    {
        "id": "person-dionysius",
        "aliases": ["Dionysius", "狄奥尼修斯"],
        "nameZh": "狄奥尼修斯",
        "nameIt": "Dionisio",
        "nameEn": "Dionysius",
        "category": "Person",
        "description": "《神曲》语境中的历史人物与典故人物之一，需与其他同名概念分开处理。",
    },
    {
        "id": "concept-god",
        "aliases": ["上帝", "God", "Deus"],
        "nameZh": "上帝",
        "nameIt": "Dio",
        "nameEn": "God",
        "category": "Concept",
        "description": "《神曲》中作为终极秩序与神圣光源的上帝形象，是但丁宇宙结构的中心。",
    },
    {
        "id": "concept-soul",
        "aliases": ["灵魂", "Soul", "Spirit", "Spirits"],
        "nameZh": "灵魂",
        "nameIt": "Anima",
        "nameEn": "Soul",
        "category": "Concept",
        "description": "《神曲》中一切亡灵与精神存在的共同概念，也是惩罚、净化与升天的主体。",
    },
    {
        "id": "place-florence",
        "aliases": ["佛罗伦萨", "Florence", "Firenze"],
        "nameZh": "佛罗伦萨",
        "nameIt": "Firenze",
        "nameEn": "Florence",
        "category": "Place",
        "description": "但丁的故乡与政治放逐的原点，也是《神曲》不断回望的历史城市。",
    },
    {
        "id": "person-beatrice",
        "aliases": ["贝雅特丽齐", "贝阿特丽切", "Beatrice"],
        "nameZh": "贝雅特丽齐",
        "nameIt": "Beatrice",
        "nameEn": "Beatrice",
        "category": "Person",
        "description": "但丁的精神引导者与恩典象征，在《天堂篇》中接替维吉尔继续引领诗人上升。",
    },
    {
        "id": "person-christ",
        "aliases": ["基督", "耶稣", "Jesus", "Christ"],
        "nameZh": "基督",
        "nameIt": "Cristo",
        "nameEn": "Christ",
        "category": "Person",
        "description": "《神曲》中神学秩序的核心人物，其救赎意义贯穿三界旅程。",
    },
    {
        "id": "concept-love",
        "aliases": ["爱", "Love", "Amore"],
        "nameZh": "爱",
        "nameIt": "Amore",
        "nameEn": "Love",
        "category": "Concept",
        "description": "《神曲》里推动宇宙、伦理与灵魂上升的核心力量，最终指向神圣之爱。",
    },
    {
        "id": "concept-truth",
        "aliases": ["真理", "Truth"],
        "nameZh": "真理",
        "nameIt": "Verità",
        "nameEn": "Truth",
        "category": "Concept",
        "description": "《神曲》中由理性、启示与神恩共同照亮的终极真理。",
    },
    {
        "id": "concept-virtue",
        "aliases": ["美德", "Virtue"],
        "nameZh": "美德",
        "nameIt": "Virtù",
        "nameEn": "Virtue",
        "category": "Concept",
        "description": "《神曲》中与罪恶相对、与净化和升天密切关联的德性概念。",
    },
]

STOP_ALIASES = {
    "rome",
    "city",
    "lake",
    "river",
    "gate",
    "forest",
    "angel",
    "saint",
    "man",
    "woman",
}

EXCLUDED_ENTITY_IDS = {
    "Project_Gutenberg",
    "Project_Gutenberg_Literary_Archive_Foundation",
    "Project Gutenberg",
    "Montclair_NJ_07042",
    "美国国税局",
    "密西西比州",
}

EXCLUDED_ENTITY_NAMES = {
    "Project_Gutenberg",
    "Project Gutenberg",
    "Project_Gutenberg_Literary_Archive_Foundation",
    "Montclair_NJ_07042",
    "美国国税局",
    "密西西比州",
    "Well",
    "Mark",
    "Guide",
    "Circle",
    "Shadow",
    "Shore",
    "Shade",
    "Song",
    "Works",
    "Man",
}

EXCLUDED_ENTITY_PATTERNS = [
    r"^Project[_ ]Gutenberg",
    r"^Canto [IVXLCDM]+$",
    r"^[A-Za-z]+_[A-Z]{2}_\d+$",
]


def ensure_dirs() -> None:
    PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    CORE_GRAPH_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)


def clear_generated_json() -> None:
    for json_file in PUBLIC_DATA_DIR.glob("*.json"):
        json_file.unlink()


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip("[]")


def slugify(text: str) -> str:
    lowered = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text.strip().lower())
    lowered = lowered.strip("-")
    return lowered or "item"


def chinese_to_int(text: str) -> int:
    mapping = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if text == "十":
        return 10
    if "十" not in text:
        return mapping[text]
    head, _, tail = text.partition("十")
    tens = mapping.get(head, 1) if head else 1
    ones = mapping.get(tail, 0) if tail else 0
    return tens * 10 + ones


def realm_from_global_index(index: int) -> tuple[str, int]:
    if index <= 34:
        return "inferno", index
    if index <= 67:
        return "purgatorio", index - 34
    return "paradiso", index - 67


def build_default_reader_columns() -> list[str]:
    return [
        f"{next(work['id'] for work in WORKS if work['language'] == 'it')}:text",
        f"{next(work['id'] for work in WORKS if work['language'] == 'en')}:text",
        "zh_wang:text",
        "zh_wang:notes",
    ]


def parse_ncx_toc(epub_path: Path) -> list[tuple[str, str]]:
    with zipfile.ZipFile(epub_path) as zf:
        toc_name = next((name for name in zf.namelist() if name.lower().endswith(".ncx")), None)
        if not toc_name:
            return []
        root = ET.fromstring(zf.read(toc_name))
        entries: list[tuple[str, str]] = []
        for nav_point in root.iter():
            if strip_tag(nav_point.tag) != "navPoint":
                continue
            text_node = next((child for child in nav_point.iter() if strip_tag(child.tag) == "text"), None)
            content_node = next((child for child in nav_point.iter() if strip_tag(child.tag) == "content"), None)
            if text_node is None or content_node is None:
                continue
            entries.append((normalize_text("".join(text_node.itertext())), content_node.attrib.get("src", "")))
        return entries


def resolve_zip_path(zf: zipfile.ZipFile, path: str) -> str:
    if path in zf.namelist():
        return path
    for candidate in zf.namelist():
        if candidate.endswith(path):
            return candidate
    raise KeyError(f"No archive member matches {path!r}")


def strip_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def element_text(element: ET.Element) -> str:
    return normalize_text(" ".join(part for part in element.itertext()))


def parse_xml_fragment(data: bytes | str) -> ET.Element:
    if isinstance(data, bytes):
        data = data.decode("utf-8", errors="ignore")
    return ET.fromstring(data)


def iter_doc_order(root: ET.Element) -> list[ET.Element]:
    return list(root.iter())


def find_element_by_id(root: ET.Element, target_id: str) -> ET.Element | None:
    for element in root.iter():
        if element.attrib.get("id") == target_id:
            return element
    return None


def extract_lines_from_xml(root: ET.Element) -> list[str]:
    lines: list[str] = []
    for block in root.iter():
        if strip_tag(block.tag) not in {"p", "div"}:
            continue
        text = element_text(block)
        if not text:
            continue
        if len(text) > 360 and "\n" not in text:
            continue
        for raw_line in text.splitlines():
            line = normalize_text(raw_line)
            if not line:
                continue
            if re.search(
                r"^(第[一二三四五六七八九十百零〇两0-9 ]+[歌章节篇]|Inferno • Canto|Purgatorio • Canto|Paradiso • Canto|Hell • Canto|CANTO [IVXLCDM]+|HELL|PURGATORY|PARADISE|OR THE INFERNO)$",
                line,
            ):
                continue
            if any(
                line.startswith(prefix)
                for prefix in [
                    "图书在版",
                    "ISBN",
                    "目录",
                    "导读",
                    "译者序",
                    "译本序",
                    "译本前言",
                    "译本说明",
                    "但丁简介",
                    "版权页",
                    "扉页",
                    "书名页",
                    "The Project Gutenberg eBook",
                ]
            ):
                continue
            if line in {"未知"}:
                continue
            if re.fullmatch(r"[\[(]?\d+[\])]?", line):
                continue
            if re.fullmatch(r"[，。、“”‘’：；？！,.!?:;…—-]+", line):
                continue
            lines.append(line)
    return lines


def load_italian_cantos(epub_path: Path) -> dict[int, list[str]]:
    with zipfile.ZipFile(epub_path) as zf:
        toc = parse_xml_fragment(zf.read("OEBPS/toc.xhtml"))
        entries = []
        for a in toc.iter():
            if strip_tag(a.tag) != "a":
                continue
            label = normalize_text(" ".join(a.itertext()))
            if "Canto" in label:
                entries.append((label, a.attrib.get("href", "")))
        cantos: dict[int, list[str]] = {}
        for label, href in entries:
            file_name, _, anchor = href.partition("#")
            match = re.search(r"(Inferno|Purgatorio|Paradiso) • Canto ([IVXLCDM]+)", label)
            if not match:
                continue
            realm_word, roman = match.groups()
            realm = {"Inferno": "inferno", "Purgatorio": "purgatorio", "Paradiso": "paradiso"}[realm_word]
            offset = {"inferno": 0, "purgatorio": 34, "paradiso": 67}[realm]
            global_idx = offset + ROMANS.index(roman) + 1
            html = parse_xml_fragment(zf.read(resolve_zip_path(zf, f"OEBPS/{file_name}")))
            target = find_element_by_id(html, anchor)
            fragments = []
            if target:
                seen = False
                for elem in html.iter():
                    if elem is target:
                        seen = True
                        continue
                    if not seen:
                        continue
                    if strip_tag(elem.tag) == "h3" and fragments:
                        break
                    if strip_tag(elem.tag) == "p":
                        fragments.append(ET.tostring(elem, encoding="unicode"))
            cantos[global_idx] = extract_lines_from_xml(parse_xml_fragment("<root>" + "".join(fragments) + "</root>"))
        return cantos


def load_english_cantos(epub_path: Path) -> dict[int, list[str]]:
    with zipfile.ZipFile(epub_path) as zf:
        toc = parse_xml_fragment(zf.read("OEBPS/toc.xhtml"))
        entries = [(normalize_text(" ".join(a.itertext())), a.attrib.get("href", "")) for a in toc.iter() if strip_tag(a.tag) == "a"]
        cantos: dict[int, list[str]] = {}
        current_realm = "inferno"
        for label, href in entries:
            dense = re.sub(r"\s+", " ", label).upper()
            if dense == "HELL OR THE INFERNO":
                current_realm = "inferno"
                continue
            if dense == "PURGATORY":
                current_realm = "purgatorio"
                continue
            if dense == "PARADISE":
                current_realm = "paradiso"
                continue
            file_name, _, anchor = href.partition("#")
            match = re.fullmatch(r"CANTO ([IVXLCDM]+)", dense)
            if not match:
                continue
            roman = match.group(1)
            offset = {"inferno": 0, "purgatorio": 34, "paradiso": 67}[current_realm]
            global_idx = offset + ROMANS.index(roman) + 1
            html = parse_xml_fragment(zf.read(resolve_zip_path(zf, f"OEBPS/{file_name}")))
            target = find_element_by_id(html, anchor) if anchor else None
            if target:
                fragments = []
                seen = False
                for elem in html.iter():
                    if elem is target:
                        seen = True
                        continue
                    if not seen:
                        continue
                    if strip_tag(elem.tag) in {"h1", "h2", "h3"} and fragments:
                        break
                    if strip_tag(elem.tag) == "p":
                        fragments.append(ET.tostring(elem, encoding="unicode"))
                cantos[global_idx] = extract_lines_from_xml(parse_xml_fragment("<root>" + "".join(fragments) + "</root>"))
            else:
                cantos[global_idx] = extract_lines_from_xml(html)
        return cantos


def load_chinese_cantos(epub_path: Path, work_id: str) -> dict[int, list[str]]:
    toc_items = parse_ncx_toc(epub_path)
    entries: list[tuple[int, str, str | None]] = []
    current_realm = "inferno"
    for label, src in toc_items:
        normalized = normalize_text(label)
        dense = re.sub(r"\s+", "", normalized)
        if dense in {"地狱", "地狱篇", "神曲·地狱篇"}:
            current_realm = "inferno"
            continue
        if dense in {"炼狱", "炼狱篇", "净界", "净界篇", "神曲·炼狱篇", "神曲·净界篇"}:
            current_realm = "purgatorio"
            continue
        if dense in {"天堂", "天堂篇", "天国", "天国篇", "神曲·天堂篇", "神曲·天国篇"}:
            current_realm = "paradiso"
            continue

        num = None
        if work_id == "zh_zhu":
            match = re.search(r"第([一二三四五六七八九十百〇零两]+)歌", dense)
            if match:
                num = chinese_to_int(match.group(1))
        elif work_id == "zh_wang":
            match = re.search(r"第([一二三四五六七八九十百〇零两]+)篇", dense)
            if match:
                num = chinese_to_int(match.group(1))
        else:
            match = re.search(r"第([一二三四五六七八九十百〇零两]+)章", dense)
            if match:
                num = chinese_to_int(match.group(1))
        if num:
            file_path, _, anchor = src.partition("#")
            entries.append(({"inferno": 0, "purgatorio": 34, "paradiso": 67}[current_realm] + num, file_path, anchor or None))

    entries.sort(key=lambda item: item[0])
    cantos: dict[int, list[str]] = {}
    with zipfile.ZipFile(epub_path) as zf:
        for idx, (global_idx, file_path, anchor) in enumerate(entries):
            next_anchor = None
            if idx + 1 < len(entries) and entries[idx + 1][1] == file_path:
                next_anchor = entries[idx + 1][2]
            soup = parse_xml_fragment(zf.read(resolve_zip_path(zf, file_path)))
            if anchor:
                target = find_element_by_id(soup, anchor)
                if target:
                    fragments = []
                    seen = False
                    for elem in soup.iter():
                        if elem is target:
                            seen = True
                            continue
                        if not seen:
                            continue
                        if next_anchor and elem.attrib.get("id") == next_anchor:
                            break
                        if strip_tag(elem.tag) in {"p", "div"}:
                            fragments.append(ET.tostring(elem, encoding="unicode"))
                    cantos[global_idx] = extract_lines_from_xml(parse_xml_fragment("<root>" + "".join(fragments) + "</root>"))
                    continue
            cantos[global_idx] = extract_lines_from_xml(soup)
    return cantos


def split_preserve_couplets(lines: list[str], target_rows: int) -> list[str]:
    if not lines:
        return []
    if len(lines) <= target_rows:
        return lines
    chunk_size = max(1, round(len(lines) / target_rows))
    chunks = []
    for index in range(0, len(lines), chunk_size):
        chunks.append(" ".join(lines[index : index + chunk_size]))
    return chunks


NOTE_SECTION_MARKERS = {"译注", "注释", "题解", "说明", "解说"}
NOTE_KEYWORDS = (
    "象征",
    "寓意",
    "指",
    "见《",
    "《旧约》",
    "《新约》",
    "《神曲》",
    "中世纪",
    "根据",
    "传说",
    "公元",
    "这里",
    "字面的意义",
)


def build_panel_id(work_id: str, kind: str) -> str:
    return f"{work_id}:{kind}"


def looks_like_note_citation(line: str) -> bool:
    return line.startswith("（《") or line.startswith("(《") or line.startswith("（见《") or line.startswith("见《")


def looks_like_gloss_note_title(line: str) -> bool:
    return len(line) <= 12 and not re.search(r"[，。？！；：、“”‘’（）()/]", line)


def looks_like_gloss_note_quote(line: str) -> bool:
    return "/" in line and len(line) >= 12


def looks_like_explanatory_note(line: str) -> bool:
    return len(line) >= 18 and any(keyword in line for keyword in NOTE_KEYWORDS)


def split_text_and_notes(work_id: str, lines: list[str]) -> tuple[list[str], list[str]]:
    if not lines:
        return [], []

    text_lines: list[str] = []
    note_lines: list[str] = []
    notes_mode = False
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line:
            index += 1
            continue

        if line in NOTE_SECTION_MARKERS:
            notes_mode = True
            index += 1
            continue

        if notes_mode:
            note_lines.append(line)
            index += 1
            continue

        if work_id == "zh_huang" and index + 2 < len(lines):
            if (
                looks_like_gloss_note_title(line)
                and looks_like_gloss_note_quote(lines[index + 1])
                and looks_like_note_citation(lines[index + 2])
            ):
                note_lines.extend(lines[index : index + 3])
                index += 3
                continue

        if work_id == "zh_huang" and looks_like_note_citation(line):
            note_lines.append(line)
            index += 1
            continue

        text_lines.append(line)
        index += 1

    if work_id in {"zh_tian", "zh_zhu"} and len(text_lines) >= 18:
        candidate_start: int | None = None
        note_run = 0
        for idx in range(max(8, len(text_lines) // 3), len(text_lines)):
            if looks_like_explanatory_note(text_lines[idx]):
                if candidate_start is None:
                    candidate_start = idx
                note_run += 1
                if note_run >= 3:
                    note_lines = text_lines[candidate_start:] + note_lines
                    text_lines = text_lines[:candidate_start]
                    break
            else:
                candidate_start = None
                note_run = 0

    return text_lines, note_lines


def strip_markdown_markup(text: str) -> str:
    cleaned = text.replace("**", "")
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    return cleaned.strip()


def note_anchor_from_content(content: str) -> str:
    quote_match = re.search(r"[“\"《](.{2,18}?)[”\"》]", content)
    if quote_match:
        return quote_match.group(1).strip()
    head = re.split(r"[：:，。；、（）()]", content, maxsplit=1)[0].strip()
    head = re.sub(r"^[0-9０-９一二三四五六七八九十]+[.)、．]?\s*", "", head)
    if len(head) > 18:
        head = head[:18]
    return head


def build_note_entries(note_lines: list[str]) -> list[dict[str, Any]]:
    entries = []
    for number, line in enumerate((item.strip() for item in note_lines if item.strip()), start=1):
        entries.append({"number": number, "content": line, "anchor": note_anchor_from_content(line)})
    return entries


def assign_note_markers(text_lines: list[str], note_entries: list[dict[str, Any]]) -> dict[int, list[int]]:
    markers: dict[int, list[int]] = defaultdict(list)
    if not text_lines or not note_entries:
        return markers

    used_positions: set[tuple[int, int]] = set()
    line_count = len(text_lines)
    for entry in note_entries:
        anchor = entry.get("anchor", "")
        found_index: int | None = None
        if anchor and len(anchor) >= 2:
            for line_index, line in enumerate(text_lines):
                if anchor in line and (line_index, entry["number"]) not in used_positions:
                    found_index = line_index
                    break
        if found_index is None:
            found_index = min(line_count - 1, max(0, round(entry["number"] * line_count / (len(note_entries) + 1)) - 1))
        markers[found_index].append(entry["number"])
        used_positions.add((found_index, entry["number"]))
    return markers


def render_text_html(text_lines: list[str], note_entries: list[dict[str, Any]] | None = None) -> str:
    markers = assign_note_markers(text_lines, note_entries or [])
    rendered_lines = []
    for index, line in enumerate(text_lines):
        suffix = "".join(
            f'<sup class="reader-note-ref" title="注释 {number}">{number}</sup>'
            for number in markers.get(index, [])
        )
        rendered_lines.append(f"{html.escape(line)}{suffix}")
    return "<br/>".join(rendered_lines)


def render_notes_html(note_entries: list[dict[str, Any]]) -> str:
    if not note_entries:
        return ""
    items = [
        f'<li value="{entry["number"]}"><span class="reader-note-index">{entry["number"]}</span><div>{html.escape(entry["content"])}</div></li>'
        for entry in note_entries
    ]
    return f'<ol class="reader-note-list">{"".join(items)}</ol>'


def build_reader_cantos(work_lines: dict[str, dict[int, list[str]]]) -> list[dict[str, Any]]:
    reader_cantos: list[dict[str, Any]] = []
    for global_idx in range(1, 101):
        realm, canto_number = realm_from_global_index(global_idx)
        versions = {work["id"]: work_lines.get(work["id"], {}).get(global_idx, []) for work in WORKS}
        panels = []
        for work in WORKS:
            text_lines, note_lines = split_text_and_notes(work["id"], versions[work["id"]])
            text_content = "\n".join(text_lines).strip()
            note_entries = build_note_entries(note_lines) if work["id"] in NUMBERED_NOTES_WORK_IDS else []
            note_content = (
                "\n".join(f"{entry['number']}. {entry['content']}" for entry in note_entries).strip()
                if note_entries
                else "\n".join(note_lines).strip()
            )
            panels.append(
                {
                    "id": build_panel_id(work["id"], "text"),
                    "workId": work["id"],
                    "kind": "text",
                    "label": work["displayTitle"],
                    "content": text_content,
                    "contentHtml": render_text_html(text_lines, note_entries if work["id"] in NUMBERED_NOTES_WORK_IDS else None),
                }
            )
            if note_content and work["id"] not in NOTELESS_WORK_IDS:
                panels.append(
                    {
                        "id": build_panel_id(work["id"], "notes"),
                        "workId": work["id"],
                        "kind": "notes",
                        "label": f"{work['displayTitle']}注释",
                        "content": note_content,
                        "contentHtml": render_notes_html(note_entries) if note_entries else render_text_html(note_lines),
                        "noteEntries": [{"number": entry["number"], "content": entry["content"]} for entry in note_entries] if note_entries else [],
                    }
                )
        reader_cantos.append(
            {
                "id": global_idx,
                "realm": realm,
                "realmLabel": REALM_LABELS[realm],
                "cantoNumber": canto_number,
                "globalNumber": global_idx,
                "title": f"{REALM_LABELS[realm]} {CN_NUMBERS[canto_number]}歌",
                "summary": f"{REALM_LABELS[realm]}第 {canto_number} 歌整歌对读。",
                "panels": panels,
            }
        )
    return reader_cantos


def realm_label_for_canto(canto_id: int) -> str:
    realm, canto_number = realm_from_global_index(canto_id)
    return f"{REALM_LABELS[realm]} {CN_NUMBERS[canto_number]}歌"


def normalize_category(category: str, name_zh: str, name_en: str, description: str) -> str:
    if category != "Other":
        if category == "Artifact":
            return "Artifact"
        if category == "Place":
            return "Place"
        if category == "Person":
            return "Person"
        if category == "Document":
            return "Document"
        if category == "Concept":
            return "Concept"
        if category == "Event":
            return "Event"
        if category == "Period":
            return "Period"
        if category == "Organization":
            return "Organization"
    haystack = f"{name_zh} {name_en} {description}".lower()
    if any(keyword in haystack for keyword in ["battle", "war", "dialogue", "expedition", "战役", "战争", "远征", "对话", "相遇"]):
        return "Event"
    if any(keyword in haystack for keyword in ["诗人", "皇帝", "国王", "教皇", "圣人", "virgil", "dante", "poet", "saint", "king", "queen", "维吉尔", "但丁", "贝雅特丽"]):
        return "Person"
    if any(keyword in haystack for keyword in ["circle", "forest", "river", "mountain", "heaven", "city", "gate", "lake", "sphere", "森林", "地狱", "河", "山", "门", "城", "天", "冰湖"]):
        return "Place"
    if any(keyword in haystack for keyword in ["canto", "comedy", "treatise", "book", "letter", "歌", "文本", "文献", "诗篇"]):
        return "Document"
    if any(keyword in haystack for keyword in ["grace", "justice", "love", "sin", "virtue", "罪", "爱", "恩典", "正义", "德性"]):
        return "Concept"
    return "Other"


def build_searchable_canto_text(reader_cantos: list[dict[str, Any]]) -> dict[int, str]:
    payload: dict[int, str] = {}
    for canto in reader_cantos:
        merged = [panel["content"] for panel in canto["panels"] if panel["kind"] == "text" and panel["content"]]
        payload[canto["id"]] = "\n".join(merged)
    return payload


def alias_matches(alias: str, haystack: str) -> bool:
    alias = alias.strip()
    if not alias:
        return False
    if alias.lower() in STOP_ALIASES:
        return False
    if re.search(r"[\u4e00-\u9fff]", alias):
        return alias in haystack
    pattern = rf"\b{re.escape(alias.lower())}\b"
    return re.search(pattern, haystack.lower()) is not None


def copy_illustrations() -> list[dict[str, Any]]:
    illustrations = []
    for spec in ILLUSTRATION_SPECS:
        target_name = f"{spec['id']}{spec['source'].suffix.lower()}"
        target_path = PUBLIC_MEDIA_DIR / target_name
        if spec["source"].resolve() != target_path.resolve():
            shutil.copy2(spec["source"], target_path)
        width, height = image_size(target_path)
        illustrations.append(
            {
                "id": spec["id"],
                "src": f"/media/{target_name}",
                "title": spec["title"],
                "credit": spec["credit"],
                "usage": spec["usage"],
                "source": spec["source"].name,
                "width": width,
                "height": height,
            }
        )
    return illustrations


def wikipedia_summary_url(page: str) -> str:
    return f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page, safe='()_,')}"


def fetch_remote_json(url: str) -> dict[str, Any]:
    if url in REMOTE_JSON_CACHE:
        return REMOTE_JSON_CACHE[url]
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, context=ssl._create_unverified_context(), timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
                REMOTE_JSON_CACHE[url] = payload
                return payload
        except Exception as error:  # noqa: PERF203
            last_error = error
            time.sleep(1.2 * (attempt + 1))
    raise last_error or RuntimeError(f"Failed to fetch {url}")


def fetch_remote_bytes(url: str) -> bytes:
    if url in REMOTE_BYTES_CACHE:
        return REMOTE_BYTES_CACHE[url]
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, context=ssl._create_unverified_context(), timeout=20) as response:
                payload = response.read()
                REMOTE_BYTES_CACHE[url] = payload
                return payload
        except Exception as error:  # noqa: PERF203
            last_error = error
            time.sleep(1.2 * (attempt + 1))
    raise last_error or RuntimeError(f"Failed to fetch {url}")


def image_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        data = handle.read()
    return image_size_from_bytes(data)


def image_size_from_bytes(data: bytes) -> tuple[int, int]:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data.startswith(b"\xff\xd8"):
        index = 2
        while index + 1 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            index += 2
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                length = int.from_bytes(data[index : index + 2], "big")
                if index + 5 >= len(data):
                    break
                height = int.from_bytes(data[index + 3 : index + 5], "big")
                width = int.from_bytes(data[index + 5 : index + 7], "big")
                return width, height
            if index + 2 > len(data):
                break
            length = int.from_bytes(data[index : index + 2], "big")
            index += length
        raise RuntimeError("Unsupported JPEG structure")
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP" and len(data) >= 30:
        chunk = data[12:16]
        if chunk == b"VP8X" and len(data) >= 30:
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return width, height
        if chunk == b"VP8 " and len(data) >= 30:
            width = int.from_bytes(data[26:28], "little") & 0x3FFF
            height = int.from_bytes(data[28:30], "little") & 0x3FFF
            return width, height
        if chunk == b"VP8L" and len(data) >= 25:
            bits = int.from_bytes(data[21:25], "little")
            width = (bits & 0x3FFF) + 1
            height = ((bits >> 14) & 0x3FFF) + 1
            return width, height
    raise RuntimeError(f"Unsupported image format for size detection: {path}")


def resolve_core_graph_image_spec(entity_id: str) -> tuple[str, str]:
    spec = CORE_GRAPH_IMAGE_SPECS[entity_id]
    if spec.get("url"):
        return spec["url"], spec.get("source", Path(spec["url"]).name)

    payload = fetch_remote_json(wikipedia_summary_url(spec["page"]))
    thumbnail = payload.get("thumbnail", {}).get("source")
    if not thumbnail:
        raise RuntimeError(f"No thumbnail found for core graph node {entity_id} ({spec['page']})")
    return thumbnail, spec["page"]


def save_remote_image_to_square(source_url: str, target_path: Path) -> None:
    target_path.write_bytes(fetch_remote_bytes(source_url))


GRAPH_FALLBACK_SOURCES: dict[str, list[str]] = {
    "Person": ["dante-portrait", "inferno-medieval", "purgatorio-medieval", "paradiso-medieval"],
    "Place": ["overview-structure", "inferno-structure", "purgatorio-structure", "paradiso-structure"],
    "Event": ["inferno-structure", "purgatory-plan", "overview-structure", "overview-medieval"],
    "Concept": ["dante-diagram", "overview-medieval", "overview-structure", "paradiso-structure"],
    "Document": ["overview-structure", "dante-diagram", "overview-medieval"],
    "Organization": ["overview-structure", "dante-diagram", "inferno-structure"],
    "Period": ["overview-medieval", "dante-diagram", "overview-structure"],
    "Artifact": ["purgatory-plan", "overview-medieval", "inferno-structure"],
    "Other": ["overview-medieval", "dante-diagram", "overview-structure"],
}


def illustration_path_from_src(src: str) -> Path:
    return PUBLIC_MEDIA_DIR / Path(src).name


def crop_square_image(source_path: Path, target_path: Path, seed: str) -> None:
    if not target_path.exists():
        shutil.copy2(source_path, target_path)


def build_core_graph_illustrations(
    entity_catalog: list[dict[str, Any]],
    graph_core: dict[str, Any],
    illustrations: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    illustration_by_id = {item["id"]: item for item in illustrations}
    graph_nodes = {node["id"]: node for node in graph_core["nodes"]}

    for entity in entity_catalog:
        if entity["id"] not in graph_nodes:
            continue

        file_name = f"{slugify(entity['id'])}.jpg"
        target_path = CORE_GRAPH_MEDIA_DIR / file_name
        if entity["id"] in CORE_GRAPH_IMAGE_SPECS:
            source_name = CORE_GRAPH_IMAGE_SPECS[entity["id"]].get("source")
            if not target_path.exists():
                remote_url, resolved_source_name = resolve_core_graph_image_spec(entity["id"])
                save_remote_image_to_square(remote_url, target_path)
                source_name = source_name or resolved_source_name
            generated = {
                "id": f"core-graph-{entity['id']}",
                "src": f"/media/graph-core/{file_name}",
                "title": CORE_GRAPH_IMAGE_SPECS[entity["id"]]["title"],
                "credit": CORE_GRAPH_IMAGE_SPECS[entity["id"]]["credit"],
                "usage": ["graph", "entity"],
                "source": source_name or file_name,
            }
        else:
            source_illustration = entity.get("illustration")
            if not source_illustration:
                candidate_ids = GRAPH_FALLBACK_SOURCES.get(entity["category"], GRAPH_FALLBACK_SOURCES["Other"])
                occurrence_realms = [item["realm"] for item in entity.get("occurrences", [])]
                if "inferno" in occurrence_realms and "inferno-medieval" in illustration_by_id:
                    candidate_ids = ["inferno-medieval", *candidate_ids]
                elif "purgatorio" in occurrence_realms and "purgatorio-medieval" in illustration_by_id:
                    candidate_ids = ["purgatorio-medieval", *candidate_ids]
                elif "paradiso" in occurrence_realms and "paradiso-medieval" in illustration_by_id:
                    candidate_ids = ["paradiso-medieval", *candidate_ids]
                source_illustration = next((illustration_by_id[item_id] for item_id in candidate_ids if item_id in illustration_by_id), None)
            if not source_illustration:
                continue
            crop_square_image(illustration_path_from_src(source_illustration["src"]), target_path, entity["id"])
            generated = {
                "id": f"core-graph-{entity['id']}",
                "src": f"/media/graph-core/{file_name}",
                "title": f"{entity['nameZh']}配图",
                "credit": source_illustration["credit"],
                "usage": ["graph", "entity"],
                "source": Path(source_illustration["src"]).name,
            }
        if not entity.get("illustration"):
            entity["illustration"] = generated
        graph_nodes[entity["id"]]["image"] = generated

    return entity_catalog, graph_core


def find_existing_entity(raw_entities: dict[str, dict[str, Any]], candidates: list[str]) -> str | None:
    normalized_candidates = [candidate.strip() for candidate in candidates if candidate.strip()]
    lower_candidates = {candidate.lower() for candidate in normalized_candidates}

    exact_matches: list[tuple[int, str]] = []
    fuzzy_matches: list[tuple[int, str]] = []
    for entity_id, entity in raw_entities.items():
        values = {
            entity_id,
            entity["nameZh"],
            entity["nameEn"],
            entity["nameIt"],
            *entity.get("aliases", []),
        }
        normalized_values = {value.strip() for value in values if value}
        if any(value.lower() in lower_candidates for value in normalized_values):
            exact_matches.append((entity.get("degree", 0), entity_id))
            continue
        haystack = " ".join(normalized_values).lower()
        if any(candidate.lower() in haystack for candidate in normalized_candidates):
            fuzzy_matches.append((entity.get("degree", 0), entity_id))
    if exact_matches:
        return max(exact_matches)[1]
    if fuzzy_matches:
        return max(fuzzy_matches)[1]
    return None


def entity_matches_alias(entity: dict[str, Any], alias: str) -> bool:
    values = {
        entity["nameZh"],
        entity["nameEn"],
        entity["nameIt"],
        entity["entityKey"],
        *entity.get("aliases", []),
    }
    normalized_values = {value.strip() for value in values if value}
    if re.search(r"[\u4e00-\u9fff]", alias):
        return alias in normalized_values
    alias_lower = alias.lower()
    return any(value.lower() == alias_lower for value in normalized_values)


def merge_manual_entity_groups(raw_entities: dict[str, dict[str, Any]]) -> dict[str, str]:
    rewrite_map: dict[str, str] = {}
    for group in ENTITY_MERGE_GROUPS:
        matches = [
            entity_id
            for entity_id, entity in raw_entities.items()
            if any(entity_matches_alias(entity, alias) for alias in group["aliases"])
        ]
        canonical_id = group["id"]
        if matches:
            primary_id = matches[0]
            primary = raw_entities[primary_id]
            for duplicate_id in matches[1:]:
                duplicate = raw_entities.pop(duplicate_id)
                rewrite_map[duplicate_id] = primary_id
                primary["aliases"] = list({*primary["aliases"], *duplicate.get("aliases", []), duplicate["nameZh"], duplicate["nameEn"], duplicate["nameIt"]})
                primary["relatedEntities"] = list({*primary.get("relatedEntities", []), *duplicate.get("relatedEntities", [])})
                primary["degree"] = max(primary.get("degree", 0), duplicate.get("degree", 0))
            primary["nameZh"] = group["nameZh"]
            primary["nameIt"] = group["nameIt"]
            primary["nameEn"] = group["nameEn"]
            primary["category"] = group["category"]
            primary["description"] = group["description"]
            primary["aliases"] = list({*primary["aliases"], *group["aliases"], group["nameZh"], group["nameIt"], group["nameEn"]})
            if primary_id != canonical_id:
                raw_entities[canonical_id] = {**primary, "id": canonical_id, "entityKey": canonical_id}
                raw_entities.pop(primary_id, None)
                rewrite_map[primary_id] = canonical_id
                for source_id, target_id in list(rewrite_map.items()):
                    if target_id == primary_id:
                        rewrite_map[source_id] = canonical_id
        else:
            raw_entities[canonical_id] = {
                "id": canonical_id,
                "entityKey": canonical_id,
                "nameZh": group["nameZh"],
                "nameIt": group["nameIt"],
                "nameEn": group["nameEn"],
                "description": group["description"],
                "degree": 12,
                "relatedEntities": [],
                "aliases": list({*group["aliases"], group["nameZh"], group["nameIt"], group["nameEn"]}),
                "category": group["category"],
            }
    return rewrite_map


def should_exclude_entity(entity: dict[str, Any]) -> bool:
    candidates = {
        entity["id"],
        entity["nameZh"],
        entity["nameIt"],
        entity["nameEn"],
        *entity.get("aliases", []),
    }
    if any(candidate in EXCLUDED_ENTITY_IDS or candidate in EXCLUDED_ENTITY_NAMES for candidate in candidates):
        return True
    if any(
        re.fullmatch(pattern, candidate or "")
        for pattern in EXCLUDED_ENTITY_PATTERNS
        for candidate in candidates
        if candidate
    ):
        return True
    ascii_name = entity["nameZh"]
    if (
        entity["nameZh"] == entity["nameEn"]
        and re.fullmatch(r"[A-Za-z][A-Za-z .,'-]{2,}", ascii_name)
        and entity["category"] in {"Other", "Document", "Place", "Person"}
        and entity.get("degree", 0) <= 2
    ):
        return True
    return False


def build_entity_catalog(reader_cantos: list[dict[str, Any]], illustrations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, str]]:
    graph_data = json.loads(GRAPH_DATA_PATH.read_text())
    entity_details = json.loads(ENTITY_DETAILS_PATH.read_text())
    searchable_cantos = build_searchable_canto_text(reader_cantos)
    illustration_by_id = {item["id"]: item for item in illustrations}

    raw_entities: dict[str, dict[str, Any]] = {}
    for node in graph_data["nodes"]:
        detail = entity_details.get(node["id"], {})
        name = detail.get("name", node["label"])
        raw_entities[node["id"]] = {
            "id": node["id"],
            "entityKey": node["id"],
            "nameZh": name,
            "nameIt": name if re.search(r"[A-Za-z]", name) else name,
            "nameEn": name if re.search(r"[A-Za-z]", name) else name,
            "description": strip_markdown_markup(detail.get("description", "") or ""),
            "degree": detail.get("degree", node.get("degree", 0)),
            "relatedEntities": detail.get("neighbors", []),
            "aliases": list({name, node["id"]}),
            "category": normalize_category(detail.get("category", node.get("category", "Other")), name, name, detail.get("description", "")),
        }

    canonical_map: dict[str, str] = {}
    for spec in FEATURED_ENTITY_SPECS:
        existing = find_existing_entity(raw_entities, spec["match"])
        canonical_map[spec["canonical"]] = existing or f"featured:{spec['canonical']}"
        if existing:
            entity = raw_entities[existing]
            fallback = spec["fallback"]
            entity["nameZh"] = fallback["nameZh"]
            entity["nameEn"] = fallback["nameEn"]
            entity["nameIt"] = fallback["nameIt"]
            entity["description"] = fallback["description"]
            entity["category"] = fallback["category"]
            entity["degree"] = max(entity.get("degree", 0), 16)
            entity["aliases"] = list({*entity["aliases"], *fallback["aliases"]})
        else:
            fallback = spec["fallback"]
            raw_entities[canonical_map[spec["canonical"]]] = {
                "id": canonical_map[spec["canonical"]],
                "entityKey": canonical_map[spec["canonical"]],
                "nameZh": fallback["nameZh"],
                "nameIt": fallback["nameIt"],
                "nameEn": fallback["nameEn"],
                "description": fallback["description"],
                "degree": 16,
                "relatedEntities": [],
                "aliases": fallback["aliases"],
                "category": fallback["category"],
            }

    protected_ids = set(canonical_map.values())
    for spec in FEATURED_ENTITY_SPECS:
        canonical_id = canonical_map[spec["canonical"]]
        aliases = {
            alias.lower()
            for alias in [
                spec["fallback"]["nameZh"],
                spec["fallback"]["nameEn"],
                spec["fallback"]["nameIt"],
                *spec["fallback"]["aliases"],
            ]
            if len(alias) >= 3
        }
        for entity_id, entity in list(raw_entities.items()):
            if entity_id in protected_ids or entity_id == canonical_id:
                continue
            haystack = f"{entity['nameZh']} {entity['nameEn']} {entity['nameIt']} {entity['entityKey']}".lower()
            if any(alias in haystack for alias in aliases):
                raw_entities.pop(entity_id, None)

    rewrite_map = merge_manual_entity_groups(raw_entities)
    if rewrite_map:
        for key, value in list(canonical_map.items()):
            canonical_map[key] = rewrite_map.get(value, value)
        for node in graph_data["nodes"]:
            node["id"] = rewrite_map.get(node["id"], node["id"])
        for link in graph_data["links"]:
            link["source"] = rewrite_map.get(link["source"], link["source"])
            link["target"] = rewrite_map.get(link["target"], link["target"])
        for entity in raw_entities.values():
            entity["relatedEntities"] = [rewrite_map.get(related, related) for related in entity.get("relatedEntities", [])]

    category_overrides = {
        "天使": "Person",
        "God": "Concept",
        "上帝": "Concept",
        "神": "Concept",
        "神恩": "Concept",
        "灵魂": "Concept",
        "Soul": "Concept",
        "佛罗伦萨": "Place",
        "Florence": "Place",
        "眼睛": "Other",
        "Beatrice": "Person",
        "贝雅特丽齐": "Person",
        "贝阿特丽切": "Person",
        "维吉尔": "Person",
        "Inferno": "Place",
        "Paradise": "Place",
        "Heaven": "Place",
        "Dionysius": "Person",
        "意大利": "Place",
        "教会": "Organization",
        "玫瑰花座": "Place",
        "愤怒女神": "Person",
        "基督": "Person",
        "耶稣": "Person",
        "圣经": "Document",
        "天国": "Place",
    }
    for entity in raw_entities.values():
        override = category_overrides.get(entity["nameZh"]) or category_overrides.get(entity["nameEn"])
        if override:
            entity["category"] = override
        entity["aliases"] = sorted(set(entity.get("aliases", [])))

    raw_entities = {
        entity_id: entity
        for entity_id, entity in raw_entities.items()
        if not should_exclude_entity(entity)
    }
    graph_data["nodes"] = [node for node in graph_data["nodes"] if node["id"] in raw_entities]
    graph_data["links"] = [
        link
        for link in graph_data["links"]
        if link["source"] in raw_entities and link["target"] in raw_entities and link["source"] != link["target"]
    ]

    mentions: list[dict[str, Any]] = []
    for entity in raw_entities.values():
        alias_candidates = [alias for alias in entity["aliases"] if len(alias.strip()) >= 2]
        occurrences = []
        for canto in reader_cantos:
            text = searchable_cantos[canto["id"]]
            if any(alias_matches(alias, text) for alias in alias_candidates):
                occurrences.append(
                    {
                        "cantoId": canto["id"],
                        "realm": canto["realm"],
                        "cantoNumber": canto["cantoNumber"],
                        "label": realm_label_for_canto(canto["id"]),
                    }
                )
        entity["occurrences"] = occurrences

    for spec in FEATURED_ENTITY_SPECS:
        entity_id = canonical_map[spec["canonical"]]
        if entity_id not in raw_entities:
            fallback = spec["fallback"]
            raw_entities[entity_id] = {
                "id": entity_id,
                "entityKey": entity_id,
                "nameZh": fallback["nameZh"],
                "nameIt": fallback["nameIt"],
                "nameEn": fallback["nameEn"],
                "description": fallback["description"],
                "degree": 12,
                "relatedEntities": [],
                "aliases": fallback["aliases"],
                "category": fallback["category"],
            }
        fallback_occurrences = spec["fallback"].get("occurrences", [])
        if fallback_occurrences:
            raw_entities[entity_id]["occurrences"] = [
                {
                    "cantoId": canto_id,
                    "realm": realm_from_global_index(canto_id)[0],
                    "cantoNumber": realm_from_global_index(canto_id)[1],
                    "label": realm_label_for_canto(canto_id),
                }
                for canto_id in fallback_occurrences
            ]

    curated_relations = {
        "virgil": ["dante", "beatrice"],
        "beatrice": ["dante", "virgil", "bernard"],
        "francesca": ["paolo", "minos"],
        "lucifer": ["ugolino"],
        "cato": ["virgil", "dante"],
        "matelda": ["beatrice"],
        "piccarda": ["beatrice"],
        "cacciaguida": ["dante"],
    }
    for left, rights in curated_relations.items():
        left_id = canonical_map.get(left)
        if not left_id:
            continue
        raw_entities[left_id]["relatedEntities"] = list({*raw_entities[left_id]["relatedEntities"], *(canonical_map.get(item, item) for item in rights)})

    featured_illustrations = {
        canonical_map["dante"]: illustration_by_id.get("dante-portrait"),
        canonical_map["virgil"]: illustration_by_id.get("inferno-medieval"),
        canonical_map["beatrice"]: illustration_by_id.get("paradiso-medieval"),
        canonical_map["lucifer"]: illustration_by_id.get("inferno-structure"),
        canonical_map["cato"]: illustration_by_id.get("purgatorio-medieval"),
        canonical_map["bernard"]: illustration_by_id.get("paradiso-structure"),
        "realm-inferno": illustration_by_id.get("inferno-medieval"),
        "realm-purgatorio": illustration_by_id.get("purgatorio-medieval"),
        "realm-paradiso": illustration_by_id.get("paradiso-medieval"),
        "work-divine-comedy": illustration_by_id.get("overview-structure"),
    }

    entity_catalog = []
    for entity in raw_entities.values():
        mentions.extend(
            {
                "entityId": entity["id"],
                "cantoId": occurrence["cantoId"],
                "realm": occurrence["realm"],
                "cantoNumber": occurrence["cantoNumber"],
                "label": occurrence["label"],
            }
            for occurrence in entity["occurrences"]
        )
        entity_catalog.append(
            {
                "id": entity["id"],
                "entityKey": entity["entityKey"],
                "nameZh": entity["nameZh"],
                "nameIt": entity["nameIt"],
                "nameEn": entity["nameEn"],
                "category": entity["category"],
                "description": strip_markdown_markup(entity["description"] or "暂无说明。"),
                "summary": strip_markdown_markup((entity["description"] or entity["nameZh"]).split("。")[0]),
                "degree": entity["degree"],
                "aliases": sorted(set(entity["aliases"])),
                "occurrences": entity["occurrences"],
                "relatedEntities": [related for related in entity["relatedEntities"] if related in raw_entities],
                "illustration": featured_illustrations.get(entity["id"]),
                "searchIndex": " ".join(sorted(set([entity["nameZh"], entity["nameIt"], entity["nameEn"], *entity["aliases"]]))).lower(),
            }
        )

    entity_catalog.sort(key=lambda item: (-len(item["occurrences"]), -item["degree"], item["nameZh"]))
    return entity_catalog, mentions, graph_data, canonical_map


def build_graph_payloads(entity_catalog: list[dict[str, Any]], raw_graph: dict[str, Any], canonical_map: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    entity_map = {entity["id"]: entity for entity in entity_catalog}
    full_nodes = [
        {
            "id": entity["id"],
            "label": entity["nameZh"],
            "name": entity["nameZh"],
            "category": entity["category"],
            "degree": entity["degree"],
            "image": entity.get("illustration"),
        }
        for entity in entity_catalog
    ]
    raw_edges = [
        {"id": f"edge-{index}", "source": link["source"], "target": link["target"]}
        for index, link in enumerate(raw_graph["links"], start=1)
        if link["source"] in entity_map and link["target"] in entity_map
    ]
    seen_pairs: set[tuple[str, str]] = set()
    deduped_edges = []
    for edge in raw_edges:
        pair = tuple(sorted((edge["source"], edge["target"])))
        if pair in seen_pairs or edge["source"] == edge["target"]:
            continue
        seen_pairs.add(pair)
        deduped_edges.append(edge)
    raw_edges = deduped_edges

    synthetic_edges = []
    featured_pairs = [
        ("dante", "virgil"),
        ("dante", "beatrice"),
        ("francesca", "paolo"),
        ("francesca", "minos"),
        ("virgil", "cato"),
        ("beatrice", "bernard"),
        ("dante", "cacciaguida"),
        ("beatrice", "piccarda"),
        ("beatrice", "justinian"),
    ]
    for index, (left, right) in enumerate(featured_pairs, start=1):
        left_id = canonical_map.get(left)
        right_id = canonical_map.get(right)
        if left_id in entity_map and right_id in entity_map:
            synthetic_edges.append({"id": f"featured-edge-{index}", "source": left_id, "target": right_id})

    edge_lookup = {(edge["source"], edge["target"]) for edge in raw_edges}
    full_edges = raw_edges[:]
    for edge in synthetic_edges:
        if (edge["source"], edge["target"]) not in edge_lookup and (edge["target"], edge["source"]) not in edge_lookup:
            full_edges.append(edge)

    core_seed_ids = {
        canonical_map["dante"],
        canonical_map["virgil"],
        canonical_map["beatrice"],
        canonical_map["francesca"],
        canonical_map["paolo"],
        canonical_map["farinata"],
        canonical_map["ulysses"],
        canonical_map["lucifer"],
        canonical_map["cato"],
        canonical_map["statius"],
        canonical_map["matelda"],
        canonical_map["piccarda"],
        canonical_map["justinian"],
        canonical_map["cacciaguida"],
        canonical_map["bernard"],
        canonical_map["ugolino"],
    }

    category_rank = {
        "Person": 0,
        "Place": 1,
        "Event": 2,
        "Concept": 3,
        "Document": 4,
        "Organization": 5,
        "Period": 6,
        "Artifact": 7,
        "Other": 8,
    }

    manual_core_labels = [
        "但丁",
        "维吉尔",
        "贝雅特丽齐",
        "弗兰切斯卡",
        "弥诺斯",
        "法里纳塔",
        "尤利西斯",
        "路西法",
        "乌戈利诺",
        "小加图",
        "斯塔提乌斯",
        "玛泰尔妲",
        "皮卡尔达",
        "查士丁尼",
        "卡恰圭达",
        "圣伯尔纳",
        "罗马",
        "佛罗伦萨",
        "炼狱山",
        "黑暗森林",
        "地狱",
        "炼狱",
        "天堂",
        "神曲",
        "忘川",
    ]

    ranked_core_ids: list[str] = []
    seen_core_labels: set[str] = set()

    def add_core_id(entity_id: str | None) -> None:
        if not entity_id or entity_id not in entity_map:
            return
        label = entity_map[entity_id]["nameZh"]
        if label in seen_core_labels:
            return
        ranked_core_ids.append(entity_id)
        seen_core_labels.add(label)

    for entity_id in core_seed_ids:
        add_core_id(entity_id)

    for label in manual_core_labels:
        match = next(
            (
                entity["id"]
                for entity in entity_catalog
                if entity["nameZh"] == label or entity["nameEn"] == label or entity["nameIt"] == label
            ),
            None,
        )
        add_core_id(match)

    for entity in sorted(
        entity_catalog,
        key=lambda item: (
            category_rank.get(item["category"], 99),
            -item["degree"],
            -len(item["occurrences"]),
            item["nameZh"],
        ),
    ):
        if entity["id"] in core_seed_ids:
            continue
        if entity["category"] in {"Other", "Person", "Document", "Organization", "Artifact", "Period"}:
            continue
        if entity["category"] in {"Place", "Event", "Concept"} and (entity["degree"] < 4 or len(entity["occurrences"]) < 3):
            continue
        add_core_id(entity["id"])
        if len(ranked_core_ids) >= 60:
            break

    core_node_ids = set(ranked_core_ids)
    core_nodes = [node for node in full_nodes if node["id"] in core_node_ids]
    core_nodes.sort(
        key=lambda node: (
            0 if node["id"] in core_seed_ids else 1,
            category_rank.get(node["category"], 99),
            -node["degree"],
            node["label"],
        )
    )
    core_node_ids = {node["id"] for node in core_nodes}
    core_edges = [edge for edge in full_edges if edge["source"] in core_node_ids and edge["target"] in core_node_ids]

    return (
        {"nodes": core_nodes, "links": core_edges},
        {"nodes": full_nodes, "links": full_edges},
    )


def build_map_scenes(entity_catalog: list[dict[str, Any]], illustrations: list[dict[str, Any]], canonical_map: dict[str, str]) -> dict[str, Any]:
    entity_map = {entity["id"]: entity for entity in entity_catalog}
    illustration_map = {item["id"]: item for item in illustrations}

    overview_panels = []
    realms_payload = {}

    for realm in REALMS:
        panel = {
            "realm": realm,
            "title": REALM_ENGLISH[realm],
            "subtitle": REALM_LABELS[realm],
            "href": f"/{realm}" if realm != "purgatorio" else "/purgatorio",
            "layers": [
                {"id": "medieval", "image": illustration_map[f"overview-{realm}-menu"]},
                {"id": "structure", "image": illustration_map[f"{realm}-structure"]},
            ],
            "cantoGrid": [{"cantoId": offset, "label": str(index)} for offset, index in enumerate(range(1, 35 if realm == "inferno" else 34), start={"inferno": 1, "purgatorio": 35, "paradiso": 68}[realm])],
        }
        overview_panels.append(panel)

        regions = []
        for region_id, name, canto_range, box in REGION_DEFS[realm]:
            regions.append(
                {
                    "id": region_id,
                    "name": name,
                    "type": "region",
                    "cantoRange": list(canto_range),
                    "box": box,
                    "summary": f"{name}，对应 {REALM_LABELS[realm]} 第 {canto_range[0]} 至 {canto_range[1]} 歌。",
                }
            )

        hotspots = []
        for hotspot in SCENE_HOTSPOTS[realm]:
            target_id = canonical_map.get(hotspot["entity"], hotspot["entity"])
            record = entity_map.get(target_id)
            canto_ids = [item["cantoId"] for item in record["occurrences"]] if record else []
            hotspots.append(
                {
                    "id": hotspot["id"],
                    "kind": hotspot["kind"],
                    "entityId": target_id,
                    "label": hotspot["label"],
                    "x": hotspot["x"],
                    "y": hotspot["y"],
                    "summary": record["summary"] if record else hotspot["label"],
                    "cantoIds": canto_ids,
                }
            )

        realms_payload[realm] = {
            "id": realm,
            "realm": realm,
            "title": REALM_LABELS[realm],
            "englishTitle": REALM_ENGLISH[realm],
            "layers": [
                {"id": "medieval", "label": "中世纪插图", "image": illustration_map[f"{realm}-medieval"]},
                {"id": "structure", "label": "结构示意图", "image": illustration_map[f"{realm}-structure"]},
            ],
            "regions": regions,
            "hotspots": hotspots,
            "defaultCantoId": {"inferno": 1, "purgatorio": 35, "paradiso": 68}[realm],
        }

    return {
        "overview": {
            "id": "overview",
            "title": "神曲阅读",
            "layers": [
                {"id": "medieval", "image": illustration_map["overview-medieval"], "label": "中世纪插图"},
                {"id": "structure", "image": illustration_map["overview-structure"], "label": "结构示意图"},
            ],
            "panels": overview_panels,
        },
        "realms": realms_payload,
    }


def parse_epic_comparisons() -> list[dict[str, Any]]:
    def clean_cell(value: str) -> str:
        return strip_markdown_markup(value.replace("\xa0", " ").strip())

    rows = [line for line in COMPARISON_MD_PATH.read_text().splitlines() if line.strip().startswith("|")]
    headers = [clean_cell(cell) for cell in rows[0].split("|")[1:-1]]
    payload = []
    for row in rows[2:]:
        cells = [clean_cell(cell) for cell in row.split("|")[1:-1]]
        if len(cells) == len(headers):
            payload.append(dict(zip(headers, cells)))
    return payload


def build_page_payloads(illustrations: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    illustration_map = {item["id"]: item for item in illustrations}
    dante_page = {
        "hero": HERO,
        "timeline": DANTE_TIMELINE,
        "illustrations": [illustration_map["dante-portrait"]],
        "sections": [
            {
                "title": "时代背景",
                "body": "意大利城邦政治、教皇与帝国的张力、商贸繁荣与派系冲突，共同塑造了但丁的世界。",
            },
            {
                "title": "为什么要写《神曲》",
                "body": "《神曲》既是流放者的自我解释，也是对秩序、正义和灵魂命运的宏大回应。",
            },
            {
                "title": "写作位置",
                "body": "《神曲》并不是安稳书房里的作品，而是在流放、辗转、失乡与政治失意中完成的精神建造。",
            },
        ],
    }
    about_page = {
        "sections": ABOUT_SECTIONS,
        "illustrations": [],
    }
    return dante_page, about_page


def write_json(name: str, payload: Any) -> None:
    (PUBLIC_DATA_DIR / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def write_supporting_json(
    works: list[dict[str, Any]],
    reader_cantos: list[dict[str, Any]],
    entity_catalog: list[dict[str, Any]],
    entity_mentions: list[dict[str, Any]],
    map_scenes: dict[str, Any],
    illustrations: list[dict[str, Any]],
    graph_core: dict[str, Any],
    graph_full: dict[str, Any],
    dante_page: dict[str, Any],
    about_page: dict[str, Any],
    epic_comparisons: list[dict[str, Any]],
) -> None:
    write_json(
        "manifest.json",
        {
            "counts": {
                "works": len(works),
                "cantos": len(reader_cantos),
                "entities": len(entity_catalog),
                "graphNodes": len(graph_full["nodes"]),
                "graphEdges": len(graph_full["links"]),
            },
            "hero": HERO,
            "defaultReaderColumns": build_default_reader_columns(),
            "defaultReaderColumnCount": 4,
        },
    )
    write_json("works.json", works)
    write_json("reader-cantos.json", reader_cantos)
    write_json("entity-catalog.json", entity_catalog)
    write_json("entity-mentions.json", entity_mentions)
    write_json("map-scenes.json", map_scenes)
    write_json("illustrations.json", illustrations)
    write_json("graph-core.json", graph_core)
    write_json("graph-full.json", graph_full)
    write_json("dante-page.json", dante_page)
    write_json("about-page.json", about_page)
    write_json("epic-comparisons.json", epic_comparisons)
    (DB_DIR / "README.md").write_text(
        textwrap.dedent(
            """
            # Divine Comedy Data

            - `divine_comedy.db`: SQLite 数据底座，供后续本地服务、检索与扩展开发使用。
            - `../public/data/*.json`: 静态站消费的镜像数据。
            """
        ).strip()
        + "\n"
    )


def build_database(
    works: list[dict[str, Any]],
    reader_cantos: list[dict[str, Any]],
    entity_catalog: list[dict[str, Any]],
    entity_mentions: list[dict[str, Any]],
    map_scenes: dict[str, Any],
    illustrations: list[dict[str, Any]],
    graph_core: dict[str, Any],
    graph_full: dict[str, Any],
    epic_comparisons: list[dict[str, Any]],
) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE works (
          id TEXT PRIMARY KEY,
          title TEXT,
          display_title TEXT,
          translator TEXT,
          language TEXT,
          source TEXT,
          kind TEXT,
          format TEXT
        );
        CREATE TABLE cantos (
          id INTEGER PRIMARY KEY,
          realm TEXT,
          realm_label TEXT,
          canto_number INTEGER,
          global_number INTEGER,
          title TEXT,
          summary TEXT
        );
        CREATE TABLE reader_panels (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          canto_id INTEGER,
          panel_id TEXT,
          work_id TEXT,
          panel_kind TEXT,
          content TEXT,
          content_html TEXT,
          notes_json TEXT,
          FOREIGN KEY(canto_id) REFERENCES cantos(id),
          FOREIGN KEY(work_id) REFERENCES works(id)
        );
        CREATE TABLE entities (
          id TEXT PRIMARY KEY,
          entity_key TEXT,
          name_zh TEXT,
          name_it TEXT,
          name_en TEXT,
          category TEXT,
          description TEXT,
          summary TEXT,
          degree INTEGER,
          aliases_json TEXT,
          illustration_json TEXT
        );
        CREATE TABLE entity_mentions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          entity_id TEXT,
          canto_id INTEGER,
          realm TEXT,
          canto_number INTEGER,
          label TEXT,
          FOREIGN KEY(entity_id) REFERENCES entities(id),
          FOREIGN KEY(canto_id) REFERENCES cantos(id)
        );
        CREATE TABLE map_hotspots (
          id TEXT PRIMARY KEY,
          scene_id TEXT,
          hotspot_kind TEXT,
          label TEXT,
          x REAL,
          y REAL,
          payload_json TEXT
        );
        CREATE TABLE illustrations (
          id TEXT PRIMARY KEY,
          src TEXT,
          title TEXT,
          credit TEXT,
          source TEXT,
          usage_json TEXT
        );
        CREATE TABLE graph_nodes (
          id TEXT,
          label TEXT,
          category TEXT,
          degree INTEGER,
          image_json TEXT,
          scope TEXT,
          PRIMARY KEY (id, scope)
        );
        CREATE TABLE graph_edges (
          id TEXT,
          source TEXT,
          target TEXT,
          scope TEXT,
          PRIMARY KEY (id, scope)
        );
        CREATE TABLE epic_comparisons (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          payload_json TEXT NOT NULL
        );
        CREATE INDEX idx_cantos_realm_number ON cantos(realm, canto_number);
        CREATE INDEX idx_reader_panels_canto_work ON reader_panels(canto_id, work_id, panel_kind);
        CREATE INDEX idx_entities_names ON entities(name_zh, name_it, name_en);
        CREATE INDEX idx_entity_mentions_entity_canto ON entity_mentions(entity_id, canto_id);
        CREATE INDEX idx_map_hotspots_scene_kind ON map_hotspots(scene_id, hotspot_kind);
        CREATE VIRTUAL TABLE reader_search USING fts5(canto_id, panel_id, work_id, panel_kind, content);
        """
    )

    conn.executemany(
        "INSERT INTO works (id, title, display_title, translator, language, source, kind, format) VALUES (:id, :title, :displayTitle, :translator, :language, :source, :kind, :format)",
        works,
    )
    conn.executemany(
        "INSERT INTO cantos (id, realm, realm_label, canto_number, global_number, title, summary) VALUES (:id, :realm, :realmLabel, :cantoNumber, :id, :title, :summary)",
        reader_cantos,
    )

    reader_rows = []
    search_rows = []
    for canto in reader_cantos:
        for panel in canto["panels"]:
            reader_rows.append(
                {
                    "canto_id": canto["id"],
                    "panel_id": panel["id"],
                    "work_id": panel["workId"],
                    "panel_kind": panel["kind"],
                    "content": panel["content"],
                    "content_html": panel.get("contentHtml"),
                    "notes_json": json.dumps(panel.get("noteEntries"), ensure_ascii=False) if panel.get("noteEntries") else None,
                }
            )
            search_rows.append((canto["id"], panel["id"], panel["workId"], panel["kind"], panel["content"]))
    conn.executemany(
        "INSERT INTO reader_panels (canto_id, panel_id, work_id, panel_kind, content, content_html, notes_json) VALUES (:canto_id, :panel_id, :work_id, :panel_kind, :content, :content_html, :notes_json)",
        reader_rows,
    )
    conn.executemany("INSERT INTO reader_search (canto_id, panel_id, work_id, panel_kind, content) VALUES (?, ?, ?, ?, ?)", search_rows)

    conn.executemany(
        "INSERT INTO entities (id, entity_key, name_zh, name_it, name_en, category, description, summary, degree, aliases_json, illustration_json) VALUES (:id, :entityKey, :nameZh, :nameIt, :nameEn, :category, :description, :summary, :degree, :aliases_json, :illustration_json)",
        [
            {
                **entity,
                "aliases_json": json.dumps(entity["aliases"], ensure_ascii=False),
                "illustration_json": json.dumps(entity["illustration"], ensure_ascii=False) if entity["illustration"] else None,
            }
            for entity in entity_catalog
        ],
    )
    conn.executemany(
        "INSERT INTO entity_mentions (entity_id, canto_id, realm, canto_number, label) VALUES (:entityId, :cantoId, :realm, :cantoNumber, :label)",
        [{"entityId": item["entityId"], "cantoId": item["cantoId"], "realm": item["realm"], "cantoNumber": item["cantoNumber"], "label": item["label"]} for item in entity_mentions],
    )

    hotspot_rows = []
    for scene_id, scene in map_scenes["realms"].items():
        for region in scene["regions"]:
            hotspot_rows.append(
                {
                    "id": region["id"],
                    "id": f"{scene_id}:{region['id']}",
                    "scene_id": scene_id,
                    "hotspot_kind": "region",
                    "label": region["name"],
                    "x": region["box"]["x"],
                    "y": region["box"]["y"],
                    "payload_json": json.dumps(region, ensure_ascii=False),
                }
            )
        for hotspot in scene["hotspots"]:
            hotspot_rows.append(
                {
                    "id": hotspot["id"],
                    "id": f"{scene_id}:{hotspot['id']}",
                    "scene_id": scene_id,
                    "hotspot_kind": hotspot["kind"],
                    "label": hotspot["label"],
                    "x": hotspot["x"],
                    "y": hotspot["y"],
                    "payload_json": json.dumps(hotspot, ensure_ascii=False),
                }
            )
    conn.executemany(
        "INSERT INTO map_hotspots (id, scene_id, hotspot_kind, label, x, y, payload_json) VALUES (:id, :scene_id, :hotspot_kind, :label, :x, :y, :payload_json)",
        hotspot_rows,
    )

    conn.executemany(
        "INSERT INTO illustrations (id, src, title, credit, source, usage_json) VALUES (:id, :src, :title, :credit, :source, :usage_json)",
        [{**item, "usage_json": json.dumps(item["usage"], ensure_ascii=False)} for item in illustrations],
    )

    conn.executemany(
        "INSERT INTO graph_nodes (id, label, category, degree, image_json, scope) VALUES (:id, :label, :category, :degree, :image_json, 'core')",
        [{**node, "image_json": json.dumps(node.get('image'), ensure_ascii=False) if node.get('image') else None} for node in graph_core["nodes"]],
    )
    conn.executemany(
        "INSERT INTO graph_edges (id, source, target, scope) VALUES (:id, :source, :target, 'core')",
        graph_core["links"],
    )
    conn.executemany(
        "INSERT INTO graph_nodes (id, label, category, degree, image_json, scope) VALUES (:id, :label, :category, :degree, :image_json, 'full')",
        [{**node, "image_json": json.dumps(node.get('image'), ensure_ascii=False) if node.get('image') else None} for node in graph_full["nodes"]],
    )
    conn.executemany(
        "INSERT INTO graph_edges (id, source, target, scope) VALUES (:id, :source, :target, 'full')",
        graph_full["links"],
    )
    conn.executemany("INSERT INTO epic_comparisons (payload_json) VALUES (?)", [(json.dumps(row, ensure_ascii=False),) for row in epic_comparisons])
    conn.commit()
    conn.close()


def main() -> None:
    ensure_dirs()
    clear_generated_json()

    work_lines = {
        "it_pg1012": load_italian_cantos(Path(WORKS[0]["source"])),
        "en_pg8800": load_english_cantos(Path(WORKS[1]["source"])),
        "zh_zhu": load_chinese_cantos(Path(WORKS[2]["source"]), "zh_zhu"),
        "zh_wang": load_chinese_cantos(Path(WORKS[3]["source"]), "zh_wang"),
        "zh_tian": load_chinese_cantos(Path(WORKS[4]["source"]), "zh_tian"),
        "zh_huang": load_chinese_cantos(Path(WORKS[5]["source"]), "zh_huang"),
    }
    reader_cantos = build_reader_cantos(work_lines)
    illustrations = copy_illustrations()
    entity_catalog, entity_mentions, raw_graph, canonical_map = build_entity_catalog(reader_cantos, illustrations)
    graph_core, graph_full = build_graph_payloads(entity_catalog, raw_graph, canonical_map)
    entity_catalog, graph_core = build_core_graph_illustrations(entity_catalog, graph_core, illustrations)
    entity_lookup = {entity["id"]: entity for entity in entity_catalog}
    graph_full["nodes"] = [
        {
            **node,
            "image": entity_lookup.get(node["id"], {}).get("illustration"),
        }
        for node in graph_full["nodes"]
    ]
    map_scenes = build_map_scenes(entity_catalog, illustrations, canonical_map)
    dante_page, about_page = build_page_payloads(illustrations)
    epic_comparisons = parse_epic_comparisons()

    write_supporting_json(
        WORKS,
        reader_cantos,
        entity_catalog,
        entity_mentions,
        map_scenes,
        illustrations,
        graph_core,
        graph_full,
        dante_page,
        about_page,
        epic_comparisons,
    )
    build_database(
        WORKS,
        reader_cantos,
        entity_catalog,
        entity_mentions,
        map_scenes,
        illustrations,
        graph_core,
        graph_full,
        epic_comparisons,
    )
    print(f"Generated {len(reader_cantos)} reader cantos, {len(entity_catalog)} entities, {len(entity_mentions)} real mentions.")
    print(f"SQLite written to {DB_PATH}")


if __name__ == "__main__":
    main()
