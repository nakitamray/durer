export type Unit = 'in' | 'cm'

export interface Paper {
  label: string
  width: number
  height: number
  unit: Unit
}

export interface Grid {
  unit: Unit
  cols: number
  rows: number
  drawing_width: number
  drawing_height: number
  cell_width: number
  cell_height: number
  offset_x: number
  offset_y: number
  col_labels: string[]
  row_labels: string[]
}

export interface Tone {
  grade: string
  gray: number
  coverage: number
}

export interface ValueStudy {
  image: string
  tones: Tone[]
}

export interface Cell {
  col: number
  row: number
}

export interface Shape {
  kind: 'ellipse' | 'box' | 'triangle' | 'polygon'
  fit: number
  share: number
  center: [number, number]
  points?: [number, number][]
  cx?: number
  cy?: number
  rx?: number
  ry?: number
  angle?: number
}

export interface ShapeStudy {
  width: number
  height: number
  drawing: boolean
  shapes: Shape[]
}

export type Point = [number, number]

export interface InkStroke {
  d: string
  length: number
  weight: number
}

export interface ContourStudy {
  width: number
  height: number
  drawing: boolean
  strokes: InkStroke[]
}

export interface Placement {
  box: [number, number, number, number]
  center: Point
  axis: [Point, Point]
  lean: number
}

export interface BlockIn {
  width: number
  height: number
  drawing: boolean
  placement: Placement
  big: Point[][]
  medium: Point[][]
}

export interface Notan {
  width: number
  height: number
  path: string
  shadow: number
}
