import { describe, expect, it } from 'vitest'

import {
  buildDefaultReaderColumns,
  buildReaderColumnSlotKey,
  clampReaderColumnCount,
  normalizeEntityCategory,
  summarizeOccurrences,
} from './site-data'

describe('normalizeEntityCategory', () => {
  it('promotes historical characters from generic Other to Person', () => {
    expect(
      normalizeEntityCategory({
        category: 'Other',
        nameEn: 'Virgil',
        nameZh: '维吉尔',
        description: '罗马诗人，受贝雅特丽齐之托引导但丁穿过地狱与炼狱。',
      }),
    ).toBe('Person')
  })

  it('recognizes spatial entities as Place', () => {
    expect(
      normalizeEntityCategory({
        category: 'Other',
        nameEn: 'Cocytus',
        nameZh: '科库托斯',
        description: '地狱最深处的冰湖，背叛者被永远冻在其中。',
      }),
    ).toBe('Place')
  })

  it('recognizes battles and major episodes as Event', () => {
    expect(
      normalizeEntityCategory({
        category: 'Other',
        nameEn: 'Battle of Campaldino',
        nameZh: '坎帕尔迪诺战役',
        description: '但丁青年时期亲历的重要战役。',
      }),
    ).toBe('Event')
  })
})

describe('buildDefaultReaderColumns', () => {
  it('prefers whole-canto text panels first and reserves the fourth slot for notes when available', () => {
    expect(
      buildDefaultReaderColumns([
        { id: 'zh_huang:text', workId: 'zh_huang', language: 'zh', kind: 'text' },
        { id: 'it_pg1012:text', workId: 'it_pg1012', language: 'it', kind: 'text' },
        { id: 'en_pg8800:text', workId: 'en_pg8800', language: 'en', kind: 'text' },
        { id: 'zh_wang:text', workId: 'zh_wang', language: 'zh', kind: 'text' },
        { id: 'zh_zhu:notes', workId: 'zh_zhu', language: 'zh', kind: 'notes' },
        { id: 'zh_wang:notes', workId: 'zh_wang', language: 'zh', kind: 'notes' },
      ]),
    ).toEqual(['it_pg1012:text', 'en_pg8800:text', 'zh_wang:text', 'zh_wang:notes'])
  })

  it('falls back to another notes panel when the chosen Chinese text has no notes', () => {
    expect(
      buildDefaultReaderColumns([
        { id: 'zh_huang:text', workId: 'zh_huang', language: 'zh', kind: 'text' },
        { id: 'it_pg1012:text', workId: 'it_pg1012', language: 'it', kind: 'text' },
        { id: 'en_pg8800:text', workId: 'en_pg8800', language: 'en', kind: 'text' },
        { id: 'zh_wang:text', workId: 'zh_wang', language: 'zh', kind: 'text' },
        { id: 'zh_zhu:notes', workId: 'zh_zhu', language: 'zh', kind: 'notes' },
      ]),
    ).toEqual(['it_pg1012:text', 'en_pg8800:text', 'zh_wang:text', 'zh_zhu:notes'])
  })
})

describe('clampReaderColumnCount', () => {
  it('keeps the column count inside the 1-4 range', () => {
    expect(clampReaderColumnCount(0)).toBe(1)
    expect(clampReaderColumnCount(2)).toBe(2)
    expect(clampReaderColumnCount(3)).toBe(3)
    expect(clampReaderColumnCount(9)).toBe(4)
  })
})

describe('buildReaderColumnSlotKey', () => {
  it('keeps duplicate panel selections isolated per column slot', () => {
    expect(buildReaderColumnSlotKey(0, 'zh_huang:text')).toBe('0:zh_huang:text')
    expect(buildReaderColumnSlotKey(1, 'zh_huang:text')).toBe('1:zh_huang:text')
  })
})

describe('summarizeOccurrences', () => {
  it('formats canto occurrences in Chinese by realm and canto number', () => {
    expect(
      summarizeOccurrences([
        { realm: 'inferno', cantoNumber: 5 },
        { realm: 'inferno', cantoNumber: 13 },
        { realm: 'paradiso', cantoNumber: 2 },
      ]),
    ).toEqual(['地狱篇 第五歌', '地狱篇 第十三歌', '天堂篇 第二歌'])
  })
})
