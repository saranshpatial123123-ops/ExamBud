export default function Dashboard() {
  return (
    <div className="w-full h-screen absolute inset-0 pointer-events-none z-10 overflow-hidden">
      {/* Screen Division Lines */}
      {/* Horizontal Line */}
      <div className="fixed top-1/2 left-0 w-full h-[4px] bg-white -translate-y-1/2 z-[100]" />
      {/* Vertical Line */}
      <div className="fixed left-1/2 top-0 h-full w-[4px] bg-white -translate-x-1/2 z-[100]" />

      {/* Intersection Soft Glow */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-white/10 rounded-full blur-2xl flex items-center justify-center z-40"></div>

      <div className="w-full h-full grid grid-cols-2 grid-rows-2">
        {/* Top Left Quadrant */}
        <div className="relative pointer-events-auto p-4 border-r border-b border-transparent"></div>
        {/* Top Right Quadrant */}
        <div className="relative pointer-events-auto p-4 border-b border-transparent"></div>
        {/* Bottom Left Quadrant */}
        <div className="relative pointer-events-auto p-4 border-r border-transparent"></div>
        {/* Bottom Right Quadrant */}
        <div className="relative pointer-events-auto p-4 border-transparent"></div>
      </div>
    </div>
  );
}
