import type { Unit } from './types'

const EIGHTHS = ['', '⅛', '¼', '⅜', '½', '⅝', '¾', '⅞']

// artists measure in fractions, not decimals
export function length(value: number, unit: Unit): string {
  if (unit === 'cm') return `${+value.toFixed(1)} cm`

  const eighths = Math.round(value * 8)
  const whole = Math.floor(eighths / 8)
  const frac = EIGHTHS[eighths % 8]
  const approx = Math.abs(eighths / 8 - value) > 0.01 ? '≈ ' : ''
  const num = whole && frac ? `${whole} ${frac}` : frac || `${whole}`
  return `${approx}${num} in`
}

export function percent(n: number): string {
  return `${Math.round(n * 100)}%`
}
