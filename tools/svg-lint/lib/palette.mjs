// tools/svg-lint/lib/palette.mjs
// The sole numeric source for the house palette, copied verbatim from SKILL.md "Colors" and "Arrowhead definitions".
// All check modules must read values from here; writing hex literals inline is not allowed.

export const BASE_TEXT = {
  primary: '#1e293b',
  secondary: '#64748b',
  muted: '#94a3b8',
};

export const SEMANTIC = [
  { name: 'input', fill: '#dbeafe', stroke: '#3b82f6', text: '#1e40af' },
  { name: 'processing', fill: '#fef3c7', stroke: '#f59e0b', text: '#b45309' },
  { name: 'output', fill: '#d1fae5', stroke: '#22c55e', text: '#166534' },
  { name: 'analysis', fill: '#f3e8ff', stroke: '#a855f7', text: '#6b21a8' },
  { name: 'warning', fill: '#fce7f3', stroke: '#ec4899', text: '#9d174d' },
];

export const ARROW_COLORS = {
  arrow: '#64748b',
  'arrow-blue': '#3b82f6',
  'arrow-orange': '#f59e0b',
  'arrow-green': '#22c55e',
  'arrow-purple': '#a855f7',
  'arrow-red': '#ef4444',
};

export const GROUP_BOX = {
  fill: '#f8fafc',
  stroke: '#94a3b8',
  dasharray: '6,4',
};

export const ALLOWED_COLORS = new Set([
  ...Object.values(BASE_TEXT),
  ...SEMANTIC.flatMap((s) => [s.fill, s.stroke, s.text]),
  ...Object.values(ARROW_COLORS),
  GROUP_BOX.fill,
  GROUP_BOX.stroke,
  'none',
  '#ffffff',
]);

export const semanticByFill = (hex) => SEMANTIC.find((s) => s.fill === hex);
export const semanticByStroke = (hex) => SEMANTIC.find((s) => s.stroke === hex);


// ---------------------------------------------------------------------------
// CourseLingo 本地增补（上游文件仅此一处改动）
//
// 目的：我们的品牌色不在上游房规调色板里，若不登记，每张图都会因
// palette-conformance 产生告警；而房规要求「0 error 且 0 warning」。
// 只做**追加**，不动上游任何既有取值 —— 上游的检查语义完全不变。
// ---------------------------------------------------------------------------
ALLOWED_COLORS.add('#2563eb'); // CourseLingo 主蓝
ALLOWED_COLORS.add('#1f2937'); // CourseLingo 正文深色
ALLOWED_COLORS.add('#1d4ed8'); // 主蓝（深/悬停）
ALLOWED_COLORS.add('#eff6ff'); // 主蓝极浅底
