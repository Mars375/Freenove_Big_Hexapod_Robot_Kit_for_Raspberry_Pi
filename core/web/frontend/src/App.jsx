import React, { useState, useEffect, useRef } from 'react';
import nipplejs from 'nipplejs';
import { 
  Zap, 
  Activity, 
  Navigation, 
  Settings, 
  Radio, 
  AlertTriangle,
  Cpu,
  BarChart2
} from 'lucide-react';

const App = () => {
  const [socket, setSocket] = useState(null);
  const [telemetry, setTelemetry] = useState({ ultrasonic: 0, battery: 0, roll: 0, pitch: 0, yaw: 0 });
  const [logs, setLogs] = useState([{ id: 1, text: 'SYSTEM INITIALIZED', type: 'system' }]);
  const [connected, setConnected] = useState(false);
  
  const moveJoystickRef = useRef(null);
  const transJoystickRef = useRef(null);
  const socketRef = useRef(null);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // For development, we might need to point to the backend port if running separately
    // But for production build served by FastAPI, the host is the same.
    const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    const wsUrl = `${protocol}//${host}/ws`;

    const connect = () => {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnected(true);
        addLog('UPLINK ESTABLISHED', 'system');
        socketRef.current = ws;
        setSocket(ws);
      };

      ws.onclose = () => {
        setConnected(false);
        addLog('UPLINK LOST - RECOGNITION IN PROGRESS', 'error');
        setTimeout(connect, 3000);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'telemetry') {
          setTelemetry(prev => ({ ...prev, ...data }));
        }
      };
    };

    connect();
    return () => socketRef.current?.close();
  }, []);

  const addLog = (text, type = 'normal') => {
    setLogs(prev => [{ id: Date.now(), text, type }, ...prev].slice(0, 50));
  };

  const sendCommand = (cmd) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(cmd));
    }
  };

  // Joysticks Initialization
  useEffect(() => {
    if (moveJoystickRef.current) {
      const manager = nipplejs.create({
        zone: moveJoystickRef.current,
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: '#00d2ff',
        size: 150
      });

      manager.on('move', (evt, data) => {
        const rad = data.angle.radian;
        const dist = data.distance; // 0-75
        const x = Math.round(Math.cos(rad) * 35 * (dist / 75));
        const y = Math.round(Math.sin(rad) * 35 * (dist / 75));
        sendCommand({ cmd: 'move', mode: 'custom', x, y, speed: 5 });
      });

      manager.on('end', () => sendCommand({ cmd: 'stop' }));
    }
  }, [connected]);

  return (
    <div className="hud-container">
      {/* Header */}
      <header>
        <div className="title-box">
          <div className="subtitle">INTERFACE DE CONTRÔLE AVANCÉE</div>
          <h1>HEXAPOD OS <span style={{color: 'var(--text-dim)'}}>v2.1</span></h1>
        </div>
        
        <div style={{display: 'flex', gap: '20px'}}>
          <div className={`status-pill ${connected ? 'online' : 'offline'}`}>
            {connected ? 'LINK SYNCED' : 'NO UPLINK'}
          </div>
          <div className="status-pill online">
            PWR: 12.4V
          </div>
        </div>
      </header>

      {/* Left Panel: Télémétrie & Logs */}
      <aside className="panel panel-left">
        <section>
          <div className="section-title">ÉTAT SYSTÈME</div>
          <div style={{marginTop: '15px', display: 'flex', flexDirection: 'column', gap: '10px'}}>
             <div className="slider-group">
                <label>SONAR <span>{telemetry.ultrasonic} cm</span></label>
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${Math.min(100, (telemetry.ultrasonic / 200) * 100)}%`, background: 'var(--neon-blue)', boxShadow: '0 0 10px var(--neon-blue)' }}></div>
                </div>
             </div>
             <div className="slider-group">
                <label>BATTERIE <span>98%</span></label>
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: '98%', background: '#2ecc71', boxShadow: '0 0 10px #2ecc71' }}></div>
                </div>
             </div>
          </div>
        </section>

        <section style={{flex: 1, display: 'flex', flexDirection: 'column'}}>
          <div className="section-title">TERMINAL DIAGNOSTIC</div>
          <div className="terminal" style={{marginTop: '10px', flex: 1}}>
            {logs.map(log => (
              <div key={log.id} className={`log-entry ${log.type}`}>
                {`> ${log.text}`}
              </div>
            ))}
          </div>
        </section>
      </aside>

      {/* Central Cockpit */}
      <main className="cockpit">
        <img 
          src={connected ? "/video_feed" : "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1200"} 
          alt="HUD Feed" 
          className="video-feed"
        />
        <div className="hud-overlay">
          <div className="reticle"></div>
          
          <div style={{position: 'absolute', top: '20px', left: '20px', fontSize: '0.8rem', color: 'var(--neon-blue)', fontFamily: 'var(--font-mono)'}}>
             CAM_STRM_01: ACTIVE<br/>
             FPS: 30.0<br/>
             RES: 640x480
          </div>

          <div style={{position: 'absolute', bottom: '20px', right: '20px', textAlign: 'right', fontSize: '0.8rem', color: 'var(--neon-blue)', fontFamily: 'var(--font-mono)'}}>
             HDG: 042°<br/>
             ALT: 100mm<br/>
             STB: YES
          </div>
        </div>
      </main>

      {/* Right Panel: Contrôles de Navigation */}
      <aside className="panel panel-right">
        <section>
          <div className="section-title">NAVIGATION LOCALE</div>
          <div className="joystick-container" ref={moveJoystickRef}>
            <div className="joystick-base"></div>
          </div>
        </section>

        <section>
          <div className="section-title">ATTITUDE & POSTURE</div>
          <div className="sliders" style={{marginTop: '15px'}}>
            <div className="slider-group">
                <label>ROLL <span>0°</span></label>
                <input type="range" min="-15" max="15" defaultValue="0" onChange={(e) => sendCommand({cmd: 'attitude', roll: parseFloat(e.target.value)})}/>
            </div>
            <div className="slider-group">
                <label>PITCH <span>0°</span></label>
                <input type="range" min="-15" max="15" defaultValue="0" onChange={(e) => sendCommand({cmd: 'attitude', pitch: parseFloat(e.target.value)})}/>
            </div>
            <div className="slider-group">
                <label>YAW <span>0°</span></label>
                <input type="range" min="-15" max="15" defaultValue="0" onChange={(e) => sendCommand({cmd: 'attitude', yaw: parseFloat(e.target.value)})}/>
            </div>
            <div className="slider-group" style={{marginTop: '10px'}}>
                <button className="status-pill online" style={{width: '100%', cursor: 'pointer'}} onClick={() => sendCommand({cmd: 'stand'})}>REDRESSER LE ROBOT</button>
            </div>
          </div>
        </section>
      </aside>
    </div>
  );
};

export default App;
