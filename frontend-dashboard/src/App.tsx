import Waves from "./components/Waves";
import ScrollStack from "./components/ScrollStack";
import MasteryGauge from "./components/MasteryGauge";
import FocusTimer from "./components/FocusTimer";
import Dock from "./components/Dock/Dock";
import { FaClipboardList, FaCalendarDays, FaBarsProgress, FaMap, FaHouse, FaGear, FaUser } from 'react-icons/fa6';

function App() {
  return (
    <div className="relative w-screen h-screen bg-[#0a0a0a] text-white overflow-hidden">
      <Waves />
      
      {/* Main Content Grid */}
      <div 
        className="absolute inset-0 z-50 pointer-events-none"
        style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gridTemplateRows: '1fr 1fr',
          width: '100vw',
          height: '100vh'
        }}
      >
        {/* Left Full Column */}
        <div style={{ gridColumn: '1', gridRow: '1 / 3', position: 'relative', overflowY: 'auto' }} className="pointer-events-auto">
          <ScrollStack />
        </div>

        {/* Top Right Quadrant (Row 1 -> 50vh height) */}
        <div style={{ gridColumn: '2', gridRow: '1', overflow: 'hidden', display: 'flex', alignItems: 'flex-start', justifyContent: 'flex-end' }} className="pointer-events-auto">
          <MasteryGauge />
        </div>
        {/* Bottom Right Quadrant (Row 2 -> 50vh height) */}
        <div style={{ gridColumn: '2', gridRow: '2', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }} className="p-6 pointer-events-auto">
          <FocusTimer />
        </div>
      </div>

      <Dock 
        items={[
          { icon: <FaHouse size={20} />, label: 'Home', onClick: () => console.log('Home!') },
          { icon: <FaClipboardList size={20} />, label: "Today's Task", onClick: () => console.log('Tasks!') },
          { icon: <FaCalendarDays size={20} />, label: 'Calendar', onClick: () => console.log('Calendar!') },
          { icon: <FaBarsProgress size={20} />, label: 'Practice', onClick: () => console.log('Practice!') },
          { icon: <FaMap size={20} />, label: 'Mindmap', onClick: () => console.log('Mindmap!') },
          { icon: <FaUser size={20} />, label: 'Profile', onClick: () => console.log('Profile!') },
          { icon: <FaGear size={20} />, label: 'Settings', onClick: () => console.log('Settings!') },
        ]}
        panelHeight={68}
        baseItemSize={50}
        magnification={70}
      />
    </div>
  );
}

export default App;
