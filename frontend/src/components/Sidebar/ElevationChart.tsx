import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
import type { ElevationPoint } from '../../types'
import styles from './ElevationChart.module.css'

const W = 256
const H = 72
const PAD = { top: 6, right: 4, bottom: 18, left: 30 }
const INNER_W = W - PAD.left - PAD.right
const INNER_H = H - PAD.top - PAD.bottom

function Chart({ data, maxEle, minEle }: { data: ElevationPoint[]; maxEle: number; minEle: number }) {
  if (data.length < 2) return null

  const maxD = data[data.length - 1].d
  const eleRange = maxEle - minEle || 1

  const sx = (d: number) => PAD.left + (d / maxD) * INNER_W
  const sy = (ele: number) => PAD.top + (1 - (ele - minEle) / eleRange) * INNER_H

  const pts = data.map((p) => `${sx(p.d).toFixed(1)},${sy(p.ele).toFixed(1)}`).join(' ')
  const fill = [
    `${sx(data[0].d).toFixed(1)},${(PAD.top + INNER_H).toFixed(1)}`,
    pts,
    `${sx(data[data.length - 1].d).toFixed(1)},${(PAD.top + INNER_H).toFixed(1)}`,
  ].join(' ')

  const midD = maxD / 2

  return (
    <svg width={W} height={H} className={styles.svg}>
      {/* fill area */}
      <polygon points={fill} style={{ fill: 'var(--panel-border)' }} opacity="0.5" />
      {/* line */}
      <polyline points={pts} fill="none" style={{ stroke: 'var(--accent)' }} strokeWidth="1.5" strokeLinejoin="round" />
      {/* Y axis */}
      <text x={PAD.left - 3} y={PAD.top + 4} textAnchor="end" fontSize="9" style={{ fill: 'var(--text-secondary)' }}>{Math.round(maxEle)}m</text>
      <text x={PAD.left - 3} y={PAD.top + INNER_H} textAnchor="end" fontSize="9" style={{ fill: 'var(--text-secondary)' }}>{Math.round(minEle)}m</text>
      {/* X axis labels */}
      <text x={PAD.left} y={H - 2} fontSize="9" style={{ fill: 'var(--text-secondary)' }}>0 km</text>
      <text x={sx(midD)} y={H - 2} textAnchor="middle" fontSize="9" style={{ fill: 'var(--text-secondary)' }}>{midD.toFixed(0)} km</text>
      <text x={PAD.left + INNER_W} y={H - 2} textAnchor="end" fontSize="9" style={{ fill: 'var(--text-secondary)' }}>{maxD.toFixed(0)} km</text>
      {/* baseline */}
      <line x1={PAD.left} y1={PAD.top + INNER_H} x2={PAD.left + INNER_W} y2={PAD.top + INNER_H} style={{ stroke: 'var(--border)' }} strokeWidth="1" />
    </svg>
  )
}

export function ElevationChart() {
  const elevation = useRouteStore((s) => s.elevation)
  const maxElevation = useRouteStore((s) => s.maxElevation)
  const minElevation = useRouteStore((s) => s.minElevation)
  const geometry = useRouteStore((s) => s.geometry)
  const t = useT()

  if (geometry.length < 2) return null

  const hasData = elevation.length >= 2 && maxElevation !== null && minElevation !== null

  return (
    <div className={styles.wrapper}>
      <div className={styles.title}>{t('elevation.title')}</div>
      {hasData ? (
        <Chart data={elevation} maxEle={maxElevation!} minEle={minElevation!} />
      ) : (
        <div className={styles.noData}>{t('elevation.no_data')}</div>
      )}
    </div>
  )
}
