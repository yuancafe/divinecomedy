import type { Realm } from '../types'

const realmLabels: Record<Realm, string> = {
  inferno: '地狱篇',
  purgatorio: '炼狱篇',
  paradiso: '天堂篇',
}

const chineseNumbers = new Map<number, string>([
  [1, '第一'],
  [2, '第二'],
  [3, '第三'],
  [4, '第四'],
  [5, '第五'],
  [6, '第六'],
  [7, '第七'],
  [8, '第八'],
  [9, '第九'],
  [10, '第十'],
  [11, '第十一'],
  [12, '第十二'],
  [13, '第十三'],
  [14, '第十四'],
  [15, '第十五'],
  [16, '第十六'],
  [17, '第十七'],
  [18, '第十八'],
  [19, '第十九'],
  [20, '第二十'],
  [21, '第二十一'],
  [22, '第二十二'],
  [23, '第二十三'],
  [24, '第二十四'],
  [25, '第二十五'],
  [26, '第二十六'],
  [27, '第二十七'],
  [28, '第二十八'],
  [29, '第二十九'],
  [30, '第三十'],
  [31, '第三十一'],
  [32, '第三十二'],
  [33, '第三十三'],
  [34, '第三十四'],
])

type CategoryInput = {
  category: string
  nameZh: string
  nameEn: string
  description: string
}

type ReaderWork = {
  id: string
  language: string
  workId: string
  kind: 'text' | 'notes'
}

type Occurrence = {
  realm: Realm
  cantoNumber: number
}

function keywordMatch(text: string, keywords: string[]) {
  return keywords.some((keyword) => text.includes(keyword))
}

export function normalizeEntityCategory(input: CategoryInput) {
  if (input.category !== 'Other') {
    return input.category
  }

  const haystack = `${input.nameZh} ${input.nameEn} ${input.description}`.toLowerCase()
  const eventKeywords = ['battle', 'war', 'dialogue', 'expedition', '战役', '战争', '远征', '相遇', '对话']
  if (keywordMatch(haystack, eventKeywords)) {
    return 'Event'
  }

  const personKeywords = [
    '诗人',
    '国王',
    '皇帝',
    '教皇',
    '圣人',
    '修士',
    'guides dante',
    'roman poet',
    'virgil',
    '但丁',
    '贝雅特丽',
    '维吉尔',
  ]
  if (keywordMatch(haystack, personKeywords)) {
    return 'Person'
  }

  const placeKeywords = [
    'circle',
    'forest',
    'river',
    'mountain',
    'city',
    'gate',
    'lake',
    'sphere',
    'heaven',
    '地狱',
    '森林',
    '冰湖',
    '山',
    '天',
    '城',
    '门',
    '河',
  ]
  if (keywordMatch(haystack, placeKeywords)) {
    return 'Place'
  }

  const documentKeywords = ['canto', 'comedy', 'book', 'treatise', '文本', '诗篇', '歌', '文献']
  if (keywordMatch(haystack, documentKeywords)) {
    return 'Document'
  }

  const conceptKeywords = ['sin', 'virtue', 'grace', 'justice', 'love', '罪', '德性', '恩典', '正义', '爱']
  if (keywordMatch(haystack, conceptKeywords)) {
    return 'Concept'
  }

  return 'Other'
}

export function buildDefaultReaderColumns(works: ReaderWork[]) {
  const textPanels = works.filter((work) => work.kind === 'text')
  const itPanel = textPanels.find((work) => work.language === 'it')?.id
  const enPanel = textPanels.find((work) => work.language === 'en')?.id
  const zhTextPanels = textPanels.filter((work) => work.language === 'zh')
  const primaryZhPanel = zhTextPanels.find((work) => work.workId === 'zh_wang') ?? zhTextPanels[0]
  const notePanels = works.filter((work) => work.kind === 'notes' && work.language === 'zh')
  const matchingNotePanel =
    notePanels.find((work) => work.workId === primaryZhPanel?.workId)?.id ?? notePanels[0]?.id

  return [itPanel, enPanel, primaryZhPanel?.id, matchingNotePanel].filter(
    (value): value is string => Boolean(value),
  )
}

export function clampReaderColumnCount(value: number) {
  if (value <= 1) return 1 as const
  if (value >= 4) return 4 as const
  if (value === 2) return 2 as const
  return 3 as const
}

export function buildReaderColumnSlotKey(index: number, panelId: string) {
  return `${index}:${panelId}`
}

export function createDefaultReaderColumnWidths() {
  return [25, 25, 25, 25]
}

export function normalizeReaderColumnWidths(widths: number[], count: 1 | 2 | 3 | 4) {
  const result = Array.from({ length: 4 }, (_, index) => widths[index] ?? 25)
  const minimum = count >= 4 ? 12 : count === 3 ? 16 : 18
  const visible = result.slice(0, count).map((value) => Math.max(value, minimum))
  const sum = visible.reduce((total, value) => total + value, 0) || 1
  visible.forEach((value, index) => {
    result[index] = Number(((value / sum) * 100).toFixed(4))
  })
  return result
}

export function resizeReaderColumnWidths(
  widths: number[],
  count: 1 | 2 | 3 | 4,
  handleIndex: number,
  deltaPercent: number,
) {
  const result = normalizeReaderColumnWidths(widths, count)
  const minimum = count >= 4 ? 12 : count === 3 ? 16 : 18
  const left = result[handleIndex]
  const right = result[handleIndex + 1]
  const pair = left + right
  const nextLeft = Math.min(pair - minimum, Math.max(minimum, left + deltaPercent))
  const nextRight = pair - nextLeft
  result[handleIndex] = Number(nextLeft.toFixed(4))
  result[handleIndex + 1] = Number(nextRight.toFixed(4))
  return result
}

export function summarizeOccurrences(occurrences: Occurrence[]) {
  return occurrences.map(({ realm, cantoNumber }) => {
    const cantoLabel = chineseNumbers.get(cantoNumber) ?? `第${cantoNumber}`
    return `${realmLabels[realm]} ${cantoLabel}歌`
  })
}
