import { useState, useRef } from 'react'
import PixelSnow from './PixelSnow/PixelSnow'

/* ── Status colour map ── */
const STATUS_STYLES: Record<string, { badgeBg: string; badgeColor: string; badgeBorder: string; glow: string }> = {
  'Completed': { 
    badgeBg: 'rgba(74,120,80,0.25)', 
    badgeColor: '#8fbc8f', 
    badgeBorder: 'rgba(100,160,100,0.45)',
    glow: '0 0 10px rgba(143,188,143,0.3)'
  },
  'In Progress': { 
    badgeBg: 'rgba(255,153,0,0.22)', 
    badgeColor: '#FF9900', 
    badgeBorder: 'rgba(255,153,0,0.45)',
    glow: '0 0 15px rgba(255,153,0,0.4)'
  },
  'Left for now': { 
    badgeBg: 'rgba(255,153,0,0.22)', 
    badgeColor: '#FF9900', 
    badgeBorder: 'rgba(255,153,0,0.45)',
    glow: '0 0 15px rgba(255,153,0,0.4)'
  },
  'Incomplete': { 
    badgeBg: 'rgba(0,229,255,0.18)', 
    badgeColor: '#00E5FF', 
    badgeBorder: 'rgba(0,229,255,0.40)',
    glow: '0 0 15px rgba(0,229,255,0.4)'
  },
  'Not Started': { 
    badgeBg: 'rgba(32,178,170,0.18)', 
    badgeColor: '#5fd6d0', 
    badgeBorder: 'rgba(40,200,195,0.40)',
    glow: 'none'
  },
}

const BASE_ACTIVITIES = [
  {
    subject: 'Computer Science', topic: 'Data Structures: Trees & Graphs',
    task: 'Implement a binary search tree with insert, delete, and in-order traversal methods.',
    status: 'In Progress',
    ...STATUS_STYLES['In Progress'],
  },
  {
    subject: 'Mathematics', topic: 'Linear Algebra: Eigenvalues',
    task: 'Solve eigenvalue decomposition problems and apply them to PCA and dimensionality reduction.',
    status: 'Incomplete',
    ...STATUS_STYLES['Incomplete'],
  },
  {
    subject: 'Physics', topic: 'Quantum Mechanics Basics',
    task: 'Review wave-particle duality, the Schrödinger equation, and the uncertainty principle.',
    status: 'Left for now',
    ...STATUS_STYLES['Left for now'],
  },
  {
    subject: 'Chemistry', topic: 'Organic Synthesis: Alkenes',
    task: "Practice addition reactions, Markovnikov's rule, and electrophilic addition mechanisms.",
    status: 'Completed',
    ...STATUS_STYLES['Completed'],
  },
  {
    subject: 'Biology', topic: 'Cell Division: Mitosis',
    task: 'Draw and label all 5 phases of mitosis and explain the role of spindle fibers.',
    status: 'Completed',
    ...STATUS_STYLES['Completed'],
  },
]

const CARDS = [
  { when: 'Today', lineColor: 'rgba(99,155,255,0.4)', activities: BASE_ACTIVITIES },
  { when: 'Yesterday', lineColor: 'rgba(180,150,255,0.4)', activities: BASE_ACTIVITIES.slice(0, 3) },
  { when: '2 days ago', lineColor: 'rgba(52,211,153,0.4)', activities: BASE_ACTIVITIES.slice(0, 2) },
  { when: '3 days ago', lineColor: 'rgba(251,191,36,0.4)', activities: BASE_ACTIVITIES },
  { when: '4 days ago', lineColor: 'rgba(244,114,182,0.4)', activities: BASE_ACTIVITIES.slice(0, 4) },
]

export default function ScrollStack() {
  const [active, setActive] = useState(0)
  const busy = useRef(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const touchY = useRef(0)

  const go = (next: number) => {
    if (next < 0 || next >= CARDS.length || busy.current) return
    busy.current = true
    setActive(next)
    setTimeout(() => { busy.current = false }, 500)
  }

  const onWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    e.stopPropagation()
    go(e.deltaY > 0 ? active + 1 : active - 1)
  }

  const onClick = (e: React.MouseEvent) => {
    if (!rootRef.current) return
    const rect = rootRef.current.getBoundingClientRect()
    go(e.clientY - rect.top < rect.height / 2 ? active - 1 : active + 1)
  }

  const onTouchStart = (e: React.TouchEvent) => { touchY.current = e.touches[0].clientY }
  const onTouchEnd = (e: React.TouchEvent) => {
    const dy = touchY.current - e.changedTouches[0].clientY
    if (Math.abs(dy) > 30) go(dy > 0 ? active + 1 : active - 1)
  }

  const getCardStyle = (i: number): React.CSSProperties => {
    const base: React.CSSProperties = {
      position: 'absolute',
      top: 0, left: 0,
      width: '100%', height: '100%',
      overflow: 'hidden',
      border: '0.5px solid rgba(255,255,255,0.08)',
      transition: 'transform 0.45s cubic-bezier(0.32,0.72,0,1), opacity 0.38s ease',
      willChange: 'transform, opacity',
      background: 'rgba(255,255,255,0.015)',
      backdropFilter: 'blur(4px)',
      WebkitBackdropFilter: 'blur(4px)',
    }
    if (i === active) {
      return { ...base, transform: 'translateY(0px) scale(1)', opacity: 1, zIndex: 10 }
    } else if (i < active) {
      return { ...base, transform: 'translateY(-100%) scale(0.96)', opacity: 0, zIndex: 0, visibility: 'hidden' }
    } else {
      const depth = i - active
      return {
        ...base,
        transform: `translateY(${depth * 8}px) scale(${1 - depth * 0.025})`,
        opacity: depth === 1 ? 0.45 : depth === 2 ? 0.2 : 0,
        zIndex: 10 - depth,
      }
    }
  }

  const WaveLines = ({ color }: { color: string }) => (
    <svg viewBox="0 0 400 300" width="100%" height="100%"
      preserveAspectRatio="xMidYMid slice"
      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', opacity: 0.35, pointerEvents: 'none' }}>
      {[0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200].map((offset, idx) => (
        <path key={idx}
          d={`M-20,${150 + offset - 100} C80,${110 + offset - 100} 160,${190 + offset - 100} 240,${150 + offset - 100} S400,${110 + offset - 100} 460,${150 + offset - 100}`}
          stroke={color} strokeWidth={idx < 3 ? 1 : idx < 6 ? 0.7 : 0.4} fill="none" />
      ))}
    </svg>
  )

  return (
    <div
      ref={rootRef}
      onWheel={onWheel}
      onClick={onClick}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
      style={{
        position: 'absolute',
        top: 0, left: 0,
        width: '100%', height: '100%',
        overflow: 'hidden',
        cursor: 'pointer',
        userSelect: 'none',
      }}
    >
      {/* Background Pixel Snow */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, overflow: 'hidden', pointerEvents: 'none' }}>
        <PixelSnow 
          color="#ffffff"
          flakeSize={0.01}
          minFlakeSize={1.25}
          pixelResolution={200}
          speed={1.25}
          density={0.3}
          direction={125}
          brightness={1}
          depthFade={8}
          farPlane={20}
          gamma={0.4545}
          variant="square"
        />
      </div>

      {/* Cards */}
      {CARDS.map((card, i) => (
        <div key={i} style={getCardStyle(i)}>
          <WaveLines color={card.lineColor} />

          {/* Card content — fills full card height, no inner scroll */}
          <div
            style={{
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              visibility: i === active ? 'visible' : 'hidden',
              display: 'flex',
              flexDirection: 'column',
              padding: '24px 24px 48px 24px',
              gap: '8px',
              overflow: 'hidden',
            }}
          >
            {/* ── Date pill — once at top of card ── */}
            <div style={{ flexShrink: 0, marginBottom: '6px' }}>
              <div style={{
                display: 'inline-flex', alignItems: 'center',
                fontSize: '13px', letterSpacing: '0.1em', textTransform: 'uppercase',
                padding: '7px 22px', borderRadius: '999px', fontWeight: 700,
                color: 'rgba(255,255,255,0.95)',
                background: 'rgba(255,255,255,0.12)',
                border: '0.5px solid rgba(255,255,255,0.22)',
              }}>
                {card.when}
              </div>
            </div>

            {/* ── Tasks — each gets equal share of remaining space ── */}
            {card.activities.map((act, actIdx) => (
              <div
                key={actIdx}
                style={{
                  flex: 1,
                  minHeight: 0,
                  padding: '12px 16px',
                  borderRadius: '18px',
                  backgroundColor: 'rgba(0,0,0,0.22)',
                  border: (act.status === 'In Progress' || act.status === 'Left for now') 
                          ? '1.5px solid rgba(255,153,0,0.5)' 
                          : (act.status === 'Incomplete')
                          ? '1.5px solid rgba(0,229,255,0.6)'
                          : '0.5px solid rgba(255,255,255,0.09)',
                  boxShadow: (act.status === 'In Progress' || act.status === 'Left for now')
                             ? '0 0 20px rgba(255,153,0,0.2), inset 0 0 10px rgba(255,153,0,0.1)'
                             : (act.status === 'Incomplete')
                             ? '0 0 20px rgba(0,229,255,0.25), inset 0 0 12px rgba(0,229,255,0.1)'
                             : 'none',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '5px',
                }}
              >
                {/* Topic */}
                <div style={{
                  fontSize: '17px', fontWeight: 650, color: '#ffffff',
                  lineHeight: 1.3,
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}>
                  {act.topic}
                </div>

                {/* Description */}
                <div style={{
                  fontSize: '13.5px', color: 'rgba(255,255,255,0.58)',
                  lineHeight: 1.5,
                  flex: 1,
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                }}>
                  {act.task}
                </div>

                {/* Status pill — bigger, bottom-right */}
                <div style={{
                  alignSelf: 'flex-end',
                  flexShrink: 0,
                  fontSize: '12px', fontWeight: 600,
                  padding: '5px 18px',
                  borderRadius: '999px',
                  color: act.badgeColor,
                  background: act.badgeBg,
                  border: `1px solid ${act.badgeBorder}`,
                  boxShadow: act.glow,
                  letterSpacing: '0.04em',
                  marginTop: '2px',
                }}>
                  {act.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Navigation dots */}
      <div style={{
        position: 'absolute', bottom: '16px', left: 0, right: 0,
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        gap: '6px', zIndex: 100, pointerEvents: 'none',
      }}>
        {CARDS.map((_, i) => (
          <div key={i} style={{
            height: '5px',
            width: i === active ? '16px' : '5px',
            borderRadius: i === active ? '3px' : '50%',
            background: i === active ? 'rgba(255,255,255,0.85)' : 'rgba(255,255,255,0.2)',
            transition: 'all 0.25s ease',
          }} />
        ))}
      </div>
    </div>
  )
}
