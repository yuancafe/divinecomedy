import type { EntityCategory, Realm, WorkMeta } from '../types'

export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export function getRealmLabel(realm: Realm) {
  if (realm === 'inferno') return '地狱'
  if (realm === 'purgatorio') return '炼狱'
  return '天堂'
}

export function getCategoryLabel(category: EntityCategory) {
  const labels: Record<EntityCategory, string> = {
    Person: '人物',
    Place: '地点',
    Event: '事件',
    Concept: '概念',
    Document: '文献',
    Organization: '组织',
    Period: '时期',
    Artifact: '器物',
    Other: '其他',
  }
  return labels[category]
}

export function buildWorkLookup(works: WorkMeta[]) {
  return Object.fromEntries(works.map((work) => [work.id, work]))
}
