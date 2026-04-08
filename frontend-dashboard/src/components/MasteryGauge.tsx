import { useState, useRef } from 'react'

/* ── helpers ── */
const DEG2RAD = Math.PI / 180
const CX = 140, CY = 148, R = 90
const START_DEG = 210
const SWEEP_DEG = 240

function polarToXY(deg: number, r = R) {
  const rad = deg * DEG2RAD
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) }
}

function arcPath(startDeg: number, endDeg: number, r = R): string {
  if (Math.abs(endDeg - startDeg) < 0.01) return ''
  const s = polarToXY(startDeg, r)
  const e = polarToXY(endDeg, r)
  const large = endDeg - startDeg > 180 ? 1 : 0
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`
}

/* ── configs ── */
const ZONES = [
  { label: 'Beginner',   range: '0–40',   from: 0,  to: 40,  color: '#5fd6d0', dimColor: 'rgba(32,178,170,0.08)'  },
  { label: 'Developing', range: '40–70',  from: 40, to: 70,  color: '#f59e0b', dimColor: 'rgba(245,158,11,0.08)'  },
  { label: 'Proficient', range: '70–100', from: 70, to: 100, color: '#22c55e', dimColor: 'rgba(34,197,94,0.08)'   },
]

function getZoneColor(v: number): string {
  if (v < 40) return '#5fd6d0'
  if (v < 70) return '#f59e0b'
  return '#22c55e'
}

const TICK_CFGS = Array.from({ length: 11 }).map((_, i) => ({ pct: i * 10, major: i % 5 === 0 }))
const LABEL_CFGS = [0, 50, 100]

interface SubjectEntry { name: string; value: number }
interface Props {
  subjects?: SubjectEntry[]
  showSlider?: boolean
}

const DEFAULT_SUBJECTS: SubjectEntry[] = [
  { name: 'Computer Science', value: 72 },
  { name: 'Mathematics',      value: 55 },
  { name: 'Physics',          value: 88 },
  { name: 'Chemistry',        value: 40 },
  { name: 'Biology',          value: 63 },
]

export default function MasteryGauge({ subjects = DEFAULT_SUBJECTS, showSlider = false }: Props) {
  const [idx, setIdx] = useState(0)
  const [internal, setInternal] = useState(72)

  /* ── animation state ── */
  const [animDir, setAnimDir] = useState<'prev' | 'next' | null>(null)
  const [animProgress, setAnimProgress] = useState(0)
  const [pendingIdx, setPendingIdx] = useState(0)
  const rafRef = useRef<number | null>(null)

  const easeInOutCubic = (t: number) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2

  /* ── needle sweep-in state ── */
  const [displayValue, setDisplayValue] = useState(subjects[0]?.value ?? 0)
  const sweepRef = useRef<number | null>(null)

  const sweepToValue = (target: number) => {
    if (sweepRef.current) cancelAnimationFrame(sweepRef.current)
    const t0 = performance.now()
    const duration = 700
    const easeOut = (t: number) => 1 - Math.pow(1 - t, 3)
    const tick = (now: number) => {
      const raw = Math.min((now - t0) / duration, 1)
      setDisplayValue(easeOut(raw) * target)
      if (raw < 1) sweepRef.current = requestAnimationFrame(tick)
    }
    setDisplayValue(0)
    sweepRef.current = requestAnimationFrame(tick)
  }

  const navigate = (dir: 'prev' | 'next') => {
    if (animDir !== null) return
    const newIdx = dir === 'next'
      ? (idx + 1) % subjects.length
      : (idx - 1 + subjects.length) % subjects.length

    setPendingIdx(newIdx)
    setAnimDir(dir)
    setAnimProgress(0)
    setDisplayValue(0) // reset immediately so sweep starts from 0

    const t0 = performance.now()
    const step = (now: number) => {
      const raw = Math.min((now - t0) / 500, 1)
      setAnimProgress(raw)
      if (raw < 1) {
        rafRef.current = requestAnimationFrame(step)
      } else {
        setIdx(newIdx)
        setAnimDir(null)
        setAnimProgress(0)
        // Sweep needle up once the gauge lands in center
        sweepToValue(subjects[newIdx]?.value ?? 0)
      }
    }
    rafRef.current = requestAnimationFrame(step)
  }

  /* ── derived values ── */
  const current = subjects[idx]
  const value   = showSlider ? internal : displayValue
  const isAnimating = animDir !== null
  const subject = isAnimating ? (subjects[pendingIdx]?.name ?? 'Subject') : (current?.name ?? 'Subject')

  const valAt = (i: number) => subjects[i]?.value ?? 0
  const easedT = easeInOutCubic(animProgress)

  /* ── property calculation ── */
  const GHOST_OFFSET_PX = 180
  const PROPS_CENTER = { x: 0, y: 0, sx: 1, arc: START_DEG, swp: SWEEP_DEG, w: 380, bl: 0, op: 1, ndl: 1, dtl: 1 }
  const PROPS_LEFT   = { x: -GHOST_OFFSET_PX, y: 0, sx: -1, arc: START_DEG, swp: SWEEP_DEG, w: 480, bl: 0, op: 0.45, ndl: 0, dtl: 0 }
  const PROPS_RIGHT  = { x: GHOST_OFFSET_PX, y: 0, sx: 1, arc: START_DEG, swp: SWEEP_DEG, w: 480, bl: 0, op: 0.45, ndl: 0, dtl: 0 }

  const lerp = (a: number, b: number, t: number) => a + (b - a) * t
  const lerpProps = (p1: typeof PROPS_CENTER, p2: typeof PROPS_CENTER, t: number) => ({
    x: lerp(p1.x, p2.x, t),
    y: lerp(p1.y, p2.y, t),
    sx: lerp(p1.sx, p2.sx, t),
    arc: lerp(p1.arc, p2.arc, t),
    swp: lerp(p1.swp, p2.swp, t),
    w: lerp(p1.w, p2.w, t),
    bl: lerp(p1.bl, p2.bl, t),
    op: lerp(p1.op, p2.op, t),
    ndl: lerp(p1.ndl, p2.ndl, t),
    dtl: lerp(p1.dtl, p2.dtl, t)
  })

  // Indices
  const prevIdx = (idx - 1 + subjects.length) % subjects.length
  const nextIdx = (idx + 1) % subjects.length
  const emergeIdx = animDir === 'next'
    ? (pendingIdx + 1) % subjects.length
    : (pendingIdx - 1 + subjects.length) % subjects.length
  const bumpedIdx = animDir === 'next' ? prevIdx : nextIdx

  // Props
  const enterSource = animDir === 'prev' ? PROPS_LEFT : PROPS_RIGHT
  const exitDest    = animDir === 'prev' ? PROPS_RIGHT : PROPS_LEFT
  const bumpedSource= animDir === 'prev' ? PROPS_RIGHT : PROPS_LEFT

  const enterProps  = isAnimating ? lerpProps(enterSource, PROPS_CENTER, easedT) : PROPS_CENTER
  const exitProps   = isAnimating ? lerpProps(PROPS_CENTER, exitDest, easedT) : PROPS_CENTER
  
  const emergeSite  = animDir === 'prev' ? PROPS_LEFT : PROPS_RIGHT
  const bumpedProps = isAnimating ? {
    ...bumpedSource,
    x: bumpedSource.x + (animDir === 'prev' ? 100 : -100) * easedT,
    y: bumpedSource.y,
    op: bumpedSource.op * (1 - easedT)
  } : bumpedSource

  /* ── unified renderer ── */
  const renderGauge = (val: number, props: typeof PROPS_CENTER, keyStr: string) => {
    const clampedVal = Math.min(Math.max(val, 0), 100)
    const zColor = getZoneColor(clampedVal)
    const gVtd = (v: number) => props.arc + (Math.min(Math.max(v,0),100)/100)*props.swp
    const track = arcPath(props.arc, props.arc + props.swp)

    const vd = gVtd(clampedVal)
    const ta = vd * DEG2RAD
    const pa = ta + Math.PI / 2
    const t_ = { x: CX + (R-8)*Math.cos(ta), y: CY + (R-8)*Math.sin(ta) }
    const tl = { x: CX - 18*Math.cos(ta),    y: CY - 18*Math.sin(ta) }
    const b1 = { x: tl.x + 3.5*Math.cos(pa), y: tl.y + 3.5*Math.sin(pa) }
    const b2 = { x: tl.x - 3.5*Math.cos(pa), y: tl.y - 3.5*Math.sin(pa) }
    const ndlPoints = `${t_.x},${t_.y} ${b1.x},${b1.y} ${b2.x},${b2.y}`

    return (
      <svg key={keyStr} viewBox="0 40 280 230" style={{
        position: 'absolute', top: 6, left: '50%',
        width: `${props.w}px`, maxWidth: '100%',
        opacity: props.op,
        filter: props.bl > 0 ? `blur(${props.bl}px)` : 'none',
        pointerEvents: 'none',
        transform: `translate(calc(-50% + ${props.x}px), ${props.y}px) scaleX(${props.sx})`,
      }}>
        <defs>
          <filter id="needle-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <radialGradient id="radial-face" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.03)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.15)" />
          </radialGradient>
        </defs>

        {props.dtl > 0.01 && (
          <circle cx={CX} cy={CY} r={R - 10} fill="url(#radial-face)" stroke="rgba(255,255,255,0.04)" strokeWidth={1} opacity={props.dtl} />
        )}

        {/* Solid Dark Trough (The Recessed Background) */}
        <path d={track} fill="none" stroke="rgba(0,0,0,0.4)" strokeWidth={16} strokeLinecap="round" />
        <path d={track} fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth={16} strokeLinecap="round" />

        {/* Spectrum Backdrop (Faint coloring of the whole curve) */}
        {ZONES.map(zone => (
          <path key={`bg-${zone.label}`}
            d={arcPath(gVtd(zone.from), gVtd(zone.to))}
            fill="none" stroke={zone.color} strokeWidth={14}
            opacity={0.06} strokeLinecap="butt"
          />
        ))}

        {ZONES.map(zone => {
          if (clampedVal <= zone.from) return null
          const fillTo = Math.min(clampedVal, zone.to)
          return (
            <path key={zone.label}
              d={arcPath(gVtd(zone.from), gVtd(fillTo))}
              fill="none" stroke={zone.color} strokeWidth={16}
              strokeLinecap={fillTo === zone.to ? 'butt' : 'round'}
              style={props.bl === 0 ? { filter: `drop-shadow(0 0 8px ${zone.color}90)` } : undefined}
            />
          )
        })}

        {props.dtl > 0.01 && TICK_CFGS.map(t => {
          const td = gVtd(t.pct)
          const inn = polarToXY(td, R - (t.major ? 16 : 10))
          const out = polarToXY(td, R - 1)
          return (
            <line key={t.pct} x1={inn.x} y1={inn.y} x2={out.x} y2={out.y}
              stroke={t.major ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.18)'}
              strokeWidth={t.major ? 2 : 1} strokeLinecap="round" opacity={props.dtl}
            />
          )
        })}

        {props.dtl > 0.01 && LABEL_CFGS.map(lp => {
          const pos = polarToXY(gVtd(lp), R + 24)
          return (
            <text key={lp} x={pos.x} y={pos.y} textAnchor="middle" dominantBaseline="middle"
              fontSize={9} fontWeight="600" fill="rgba(255,255,255,0.25)" fontFamily="system-ui, sans-serif" opacity={props.dtl}
            >{lp}</text>
          )
        })}

        {props.ndl > 0.01 && (
          <g opacity={props.ndl}>
            <polygon points={ndlPoints} fill="white" opacity={0.92} filter="url(#needle-glow)" />
            <circle cx={CX} cy={CY} r={13} fill="rgba(255,255,255,0.06)" />
            <circle cx={CX} cy={CY} r={9} fill="rgba(20,20,20,0.95)" stroke="rgba(255,255,255,0.25)" strokeWidth={1} />
            <circle cx={CX} cy={CY} r={4} fill={zColor} opacity={0.9} />
          </g>
        )}
      </svg>
    )
  }

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      padding: '6px 12px 10px', userSelect: 'none', width: '100%',
      justifyContent: 'flex-start', position: 'relative', overflow: 'hidden',
    }}>

      {/* ── Invisible Spacer for auto-height ── */}
      <svg viewBox="0 40 280 230" style={{ width: '100%', maxWidth: 380, visibility: 'hidden', pointerEvents: 'none' }} />

      {/* ── Gauges Rendered ── */}
      {!isAnimating ? (
        <>
          {renderGauge(valAt(prevIdx), PROPS_LEFT, 'ghost-l')}
          {renderGauge(valAt(nextIdx), PROPS_RIGHT, 'ghost-r')}
          {renderGauge(value, PROPS_CENTER, 'main')}
        </>
      ) : (
        <>
          {renderGauge(valAt(bumpedIdx), bumpedProps, 'bumped')}
          {renderGauge(valAt(emergeIdx) * easedT, emergeSite, 'emerge')}
          {renderGauge(valAt(idx), exitProps, 'exit')}
          {renderGauge(displayValue, enterProps, 'enter')}
        </>
      )}

      {/* ── Subject heading with arrow nav ── */}
      <div style={{
        width: '100%', maxWidth: 260, margin: '0 auto',
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '6px', marginTop: '2px', position: 'relative', zIndex: 5,
      }}>
        <button onClick={() => navigate('prev')} style={{
          background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: '50%', width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', color: 'rgba(255,255,255,0.6)', fontSize: '14px', flexShrink: 0,
          transition: 'background 0.2s',
        }}
          onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.12)')}
          onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
        >‹</button>

        <span style={{
          flex: 1,
          fontSize: '16px', fontWeight: 600, letterSpacing: '0.05em', color: 'rgba(255,255,255,0.75)',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          textAlign: 'center', padding: '0 8px',
          transition: 'opacity 0.2s',
        }}>{subject}</span>

        <button onClick={() => navigate('next')} style={{
          background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: '50%', width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', color: 'rgba(255,255,255,0.6)', fontSize: '14px', flexShrink: 0,
          transition: 'background 0.2s',
        }}
          onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.12)')}
          onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.06)')}
        >›</button>
      </div>



      {showSlider && (
        <input type="range" min={0} max={100} value={internal}
          onChange={e => setInternal(Number(e.target.value))}
          style={{ marginTop: 14, width: '80%', accentColor: '#aaa', cursor: 'pointer', position: 'relative', zIndex: 5 }}
        />
      )}
    </div>
  )
}
