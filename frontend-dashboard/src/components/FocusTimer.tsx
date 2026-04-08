import { useState, useEffect } from 'react';

export default function FocusTimer() {
  const [elapsed, setElapsed] = useState(0);

  // Smooth continuous requestAnimationFrame loop for both time and needle
  useEffect(() => {
    let frameId: number;
    const start = performance.now();
    const update = (now: number) => {
      setElapsed(now - start);
      frameId = requestAnimationFrame(update);
    };
    frameId = requestAnimationFrame(update);
    return () => cancelAnimationFrame(frameId);
  }, []);

  // Subjects cycle with unique deadlines for each
  const SUBJECTS = [
    { title: 'Binary Trees Set', course: 'COMPUTER SCIENCE', allocatedMs: 9 * 3600000 + 32 * 60000 + 24 * 1000 },
    { title: 'Calculus III Set', course: 'MATHEMATICS', allocatedMs: 2 * 3600000 + 15 * 60000 },
    { title: 'Quantum Mechanics', course: 'PHYSICS', allocatedMs: 5000 }, // 5 second test deadline!
    { title: 'Organic Synthesis', course: 'CHEMISTRY', allocatedMs: 1 * 3600000 + 20 * 60000 },
    { title: 'Cellular Mitosis', course: 'BIOLOGY', allocatedMs: 3 * 3600000 + 5 * 60000 }
  ];
  const [subjIdx, setSubjIdx] = useState(0);
  const currentSubject = SUBJECTS[subjIdx];

  // The timer connects dynamically to the active subject's deadline
  const currentMs = Math.max(0, currentSubject.allocatedMs - elapsed); // Counting DOWN
  const progressRatio = currentMs / currentSubject.allocatedMs;
  const isZero = currentMs === 0;

  // Dynamic urgency color mapping (Green -> Orange -> Turquoise)
  let clockColor = "#00FF7F"; // Green (plenty of time)
  if (progressRatio <= 0.1) {
    clockColor = "#00E5FF"; // Turquoise (final seconds)
  } else if (progressRatio <= 0.4) {
    clockColor = "#FF9900"; // Orange (warning)
  }
  if (isZero) clockColor = "#00FFFF"; // Bright Cyan pulse on zero

  const h = Math.floor(currentMs / 3600000) % 24;
  const m = Math.floor(currentMs / 60000) % 60;
  const hrs = h.toString().padStart(2, '0');
  const mins = m.toString().padStart(2, '0');

  // Continuous needle angle. Since currentMs is decreasing, the angle decreases (anticlockwise sweep)
  const totalSeconds = (currentMs % 60000) / 1000;
  let needleAngle = totalSeconds * 6 - 90;

  const cycleSubject = () => {
    setSubjIdx(prev => (prev + 1) % SUBJECTS.length);
  };
  
  const CX = 200;
  const CY = 200;

  // Render outer ring ticks (12 major, 12 minor)
  const outerTicks = Array.from({ length: 24 }).map((_, i) => ({
    deg: i * 15,
    major: i % 2 === 0,
    veryMajor: i % 6 === 0, // 0, 90, 180, 270
  }));

  // Render middle ring ticks (60 items)
  const innerTicks = Array.from({ length: 60 }).map((_, i) => ({
    deg: i * 6,
    major: i % 5 === 0,
  }));

  return (
    <div style={{
      width: '100%', height: '100%',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&display=swap');
        
        @keyframes digiBounce {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-6px) scale(1.05); }
        }
      `}</style>
      
      <svg viewBox="0 0 400 400" style={{
        width: '100%', maxWidth: '340px', maxHeight: '100%',
        filter: progressRatio <= 0.1
          ? 'drop-shadow(0 20px 40px rgba(0,0,0,0.6)) drop-shadow(0 0 20px rgba(0,229,255,0.3))'
          : 'drop-shadow(0 12px 20px rgba(0,0,0,0.4))',
        transition: 'filter 1s ease-in-out',
        userSelect: 'none'
      }}>
        <defs>
          {/* Casing Gradients */}
          <linearGradient id="body-gradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2c2d30" />
            <stop offset="100%" stopColor="#18181A" />
          </linearGradient>
          
          <linearGradient id="outer-bezel-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#252528" />
            <stop offset="100%" stopColor="#0a0a0b" />
          </linearGradient>

          <linearGradient id="inner-bezel-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0a0a0b" />
            <stop offset="100%" stopColor="#252528" />
          </linearGradient>

          <radialGradient id="screen-grad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#1e1e20" />
            <stop offset="90%" stopColor="#111112" />
            <stop offset="100%" stopColor="#080808" />
          </radialGradient>

          <filter id="neon-glow-subtle" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="1.5" result="blur1" />
            <feMerge>
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="neon-glow-urgent" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur1" />
            <feGaussianBlur stdDeviation="10" result="blur2" />
            <feMerge>
              <feMergeNode in="blur2" />
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="soft-red-glow">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g pointerEvents="none">
          {/* No confusing extra static tabs. Just the main clock housing. */}
        </g>
        
        {/* --- The Singular Active Clicker (Left Side / 180 degrees) --- */}
        <g 
          onClick={cycleSubject}
          style={{ cursor: 'pointer', transition: 'transform 0.1s', pointerEvents: 'all' }}
          onMouseDown={e => e.currentTarget.style.transform = 'translateX(3px)'}
          onMouseUp={e => e.currentTarget.style.transform = 'none'}
          onMouseLeave={e => e.currentTarget.style.transform = 'none'}
          className="focus-clicker"
        >
          {/* Button housing protruding far left OUTSIDE the r=170 casing ring (which aligns at x=30) */}
          <rect x={CX - 192} y={CY - 25} width={35} height={50} rx={8} fill="#1a1a1c" stroke="#2a2a2c" strokeWidth={1} />
          {/* Button inner tactile indent */}
          <rect x={CX - 188} y={CY - 15} width={10} height={30} rx={4} fill="#111" stroke="#333" strokeWidth={1} />
          {/* Leftmost textured ridge */}
          <rect x={CX - 194} y={CY - 10} width={4} height={20} rx={2} fill="#555" />
        </g>

        <g pointerEvents="none">
          {/* --- Main Casing Base --- */}
          <circle cx={CX} cy={CY} r={170} fill="url(#body-gradient)" stroke="#3a3a3e" strokeWidth={1} />
          <circle cx={CX} cy={CY} r={169} fill="none" stroke="#111" strokeWidth={3} />

        {/* --- Outer Ticks Track --- */}
        <circle cx={CX} cy={CY} r={160} fill="#141416" />
        {outerTicks.map(t => {
          const r1 = t.veryMajor ? 148 : (t.major ? 152 : 154);
          const r2 = 160;
          const rad = t.deg * (Math.PI / 180);
          return (
            <line key={`out-${t.deg}`}
              x1={CX + r1 * Math.cos(rad)} y1={CY + r1 * Math.sin(rad)}
              x2={CX + r2 * Math.cos(rad)} y2={CY + r2 * Math.sin(rad)}
              stroke={t.veryMajor ? "#666" : (t.major ? "#444" : "#333")} 
              strokeWidth={t.veryMajor ? 2 : 1.5}
            />
          );
        })}

        {/* --- Middle Bezel Geometry (Creates depth) --- */}
        {/* The slanted outer edge going down */}
        <circle cx={CX} cy={CY} r={145} fill="url(#outer-bezel-grad)" />
        {/* The slanted inner edge going up */}
        <circle cx={CX} cy={CY} r={120} fill="url(#inner-bezel-grad)" />

        {/* --- Inner Ticks Active Draining Gauge (Matching Total Time & Urgency) --- */}
        {innerTicks.map(t => {
          const r1 = 125;
          const r2 = t.major ? 138 : 133;
          const rad = t.deg * (Math.PI / 180);
          
          // Calculate if this tick should glow depending on the ratio of TOTAL time remaining
          const tickRel = (t.deg + 90) % 360;
          const targetAngle = progressRatio * 360;
          const isActive = tickRel <= targetAngle && targetAngle > 0.1;

          return (
            <line key={`in-${t.deg}`}
              x1={CX + r1 * Math.cos(rad)} y1={CY + r1 * Math.sin(rad)}
              x2={CX + r2 * Math.cos(rad)} y2={CY + r2 * Math.sin(rad)}
              stroke={isActive ? clockColor : "#1a1a1c"} 
              strokeWidth={t.major ? 2 : 1}
              style={{ transition: 'stroke 0.5s ease-in-out' }}
            />
          );
        })}

        {/* --- Photo-Exact Red Pill Arc --- */}
        <path 
          d={`M ${CX - 15} 338 A 138 138 0 0 0 ${CX + 15} 338`} 
          fill="none" stroke="#FF5053" strokeWidth={6} 
          strokeLinecap="round" filter="url(#soft-red-glow)" 
        />
        <path 
          d={`M ${CX - 15} 338 A 138 138 0 0 0 ${CX + 15} 338`} 
          fill="none" stroke="#FFF" strokeWidth={2} 
          strokeLinecap="round" opacity={0.4} 
        />

        {/* --- Inner Screen Glass --- */}
        <circle cx={CX} cy={CY} r={108} fill="url(#screen-grad)" />
        <circle cx={CX} cy={CY} r={108} fill="none" stroke="#000" strokeWidth={4} />

        {/* Screen ambient light reflection (glass effect) */}
        <path 
          d={`M 110 150 A 100 100 0 0 1 290 150 A 160 160 0 0 0 110 150`} 
          fill="rgba(255,255,255,0.02)" 
        />

        {/* --- Screen Content --- */}
        {/* Digital Time */}
        <g style={isZero ? { animation: 'digiBounce 0.6s cubic-bezier(0.28, 0.84, 0.42, 1) infinite', transformOrigin: `${CX}px ${CY - 25}px` } : {}}>
          <text 
            x={CX} y={CY - 25} 
            textAnchor="middle" dominantBaseline="alphabetic"
            fill={clockColor} 
            fontFamily="'JetBrains Mono', monospace" 
            fontWeight="700" 
            fontSize="48"
            letterSpacing="4"
            filter={isZero ? "url(#neon-glow-urgent)" : (progressRatio <= 0.1 ? "url(#neon-glow-urgent)" : "url(#neon-glow-subtle)")}
            style={{ transition: 'fill 1s ease-in-out' }}
          >
            {hrs}:{mins}
          </text>
        </g>

        {/* Subject labels */}
        <text x={CX} y={CY + 35} textAnchor="middle" fill="#999" fontSize="12" fontWeight="400" letterSpacing="0.5" style={{ transition: 'opacity 0.2s' }}>
          {currentSubject.title}
        </text>
        <text x={CX} y={CY + 52} textAnchor="middle" fill="#555" fontSize="10" fontWeight="600" letterSpacing="1.5" style={{ transition: 'opacity 0.2s' }}>
          {currentSubject.course}
        </text>

        {/* Pagination Dots (Dynamic Stepper) */}
        <g transform={`translate(${CX - ((SUBJECTS.length - 1) * 10) / 2}, ${CY + 75})`}>
          {SUBJECTS.map((_, i) => (
            <circle 
              key={i}
              cx={i * 10} 
              cy={0} 
              r={i === subjIdx ? 3.5 : 2.5} 
              fill={i === subjIdx ? "#FF5053" : "#333"} 
              filter={i === subjIdx ? "url(#soft-red-glow)" : undefined}
            />
          ))}
        </g>

        {/* --- The Analog Hand & Center Pivot --- */}
        {/* HRS O MIN labels aligned with center */}
        <text x={CX - 15} y={CY + 3} textAnchor="end" dominantBaseline="middle" fill="#444" fontSize="10" fontWeight="600" letterSpacing="1">
          HRS
        </text>
        <text x={CX + 15} y={CY + 3} textAnchor="start" dominantBaseline="middle" fill="#444" fontSize="10" fontWeight="600" letterSpacing="1">
          MIN
        </text>

        {/* Rotating Hand Group */}
        <g transform={`rotate(${needleAngle}, ${CX}, ${CY})`}>
          {/* Needle shadow */}
          <polygon points={`${CX-2},${CY} ${CX-1},${CY-100} ${CX+1},${CY-100} ${CX+2},${CY}`} fill="rgba(0,0,0,0.5)" filter="blur(2px)" />
          
          {/* Main sleek white hand */}
          <polygon points={`${CX-1.5},${CY} ${CX-0.5},${CY-100} ${CX+0.5},${CY-100} ${CX+1.5},${CY}`} fill="#FFF" opacity={0.9} />
          
          {/* Tail of the hand */}
          <line x1={CX} y1={CY} x2={CX} y2={CY+15} stroke="#FFF" strokeWidth={1.5} opacity={0.4} />
        </g>

          {/* Center Pivot Axis */}
          <circle cx={CX} cy={CY} r={8} fill="#111" stroke="#333" strokeWidth={1} />
          <circle cx={CX} cy={CY} r={3} fill="#D97A22" />
        </g>
      </svg>
    </div>
  );
}
