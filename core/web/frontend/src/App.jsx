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
  const headJoystickRef = useRef(null);
  const socketRef = useRef(null);
  
  const [gaitMode, setGaitMode] = useState('1'); // '1' = Tripod, '2' = Wave
  const [actionMode, setActionMode] = useState('linear'); // 'linear' or 'rotate'
  const [headPos, setHeadPos] = useState({ h: 1500, v: 1500 });
  const [balancing, setBalancing] = useState(false);
  const [relaxed, setRelaxed] = useState(false);
  const [speed, setSpeed] = useState(5);
  const [altitude, setAltitude] = useState(-100);
  const [sonarEnabled, setSonarEnabled] = useState(true);
  const [cameraEnabled, setCameraEnabled] = useState(true);
  const [faceEnabled, setFaceEnabled] = useState(false);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // For development, we might need to point to the backend port if running separately
    // But for production build served by FastAPI, the host is the same.
    const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    // Update to match backend router prefix /api/v1/ws with endpoint /ws
    const wsUrl = `${protocol}//${host}/api/v1/ws/ws`;

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
        } else if (data.type === 'error') {
          addLog(`ERROR: ${data.message}`, 'error');
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

  const lastMoveRef = useRef(0);

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
        // Limit updates to 10Hz
        const now = Date.now();
        if (now - lastMoveRef.current < 100) return;
        lastMoveRef.current = now;

        const rad = data.angle.radian;
        const dist = data.distance; // 0-75
        
        // Joystick Up (90 deg) -> dist*sin(PI/2) = dist
        const joyX = Math.cos(rad) * dist;
        const joyY = Math.sin(rad) * dist;
        
        // Scale to robot max 35
        const robotX = Math.round((joyY / 75) * 35);  // Forward
        const robotY = Math.round((-joyX / 75) * 35); // Left/Right
        
        let angle = 0;
        if (actionMode === 'rotate') {
            // In rotate mode, x movement determines turn angle
            angle = Math.round((joyX / 75) * 10); // Scale to -10 to 10
            sendCommand({ cmd: 'move', mode: 'gait', x: robotX, y: 0, speed: speed, angle: angle });
        } else {
            sendCommand({ cmd: 'move', mode: 'motion', x: robotX, y: robotY, speed: speed, angle: 0 });
        }
      });

      manager.on('end', () => sendCommand({ cmd: 'stop' }));
    }

    if (headJoystickRef.current) {
        const headManager = nipplejs.create({
          zone: headJoystickRef.current,
          mode: 'static',
          position: { left: '50%', top: '50%' },
          color: '#ff0055',
          size: 100
        });
  
        headManager.on('move', (evt, data) => {
          const now = Date.now();
          if (now - lastMoveRef.current < 100) return;
          lastMoveRef.current = now;
  
          const joyX = Math.cos(data.angle.radian) * data.distance;
          const joyY = Math.sin(data.angle.radian) * data.distance;
          
          // Scale to -90 to 90 (degrees offset from center)
          const h = Math.round((joyX / 50) * 90);
          const v = Math.round((joyY / 50) * 45); // Tilt range is usually smaller
          
          setHeadPos({ h, v });
          sendCommand({ cmd: 'camera', horizontal: h, vertical: v });
        });
  
        headManager.on('end', () => {
          // Optional: sendCommand({ cmd: 'camera', horizontal: 0, vertical: 0 }); 
          // Usually better to keep position
        });
      }
  }, [connected, actionMode]);

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
            PWR: {telemetry.battery.toFixed(1)}V
          </div>
        </div>
      </header>

      {/* Left Panel: État Système & Terminal */}
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
                <label>BATTERIE <span>{telemetry.battery.toFixed(1)}V</span></label>
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${Math.min(100, ((telemetry.battery - 6.0) / 2.4) * 100)}%`, background: '#2ecc71', boxShadow: '0 0 10px #2ecc71' }}></div>
                </div>
             </div>
          </div>
        </section>

        <section style={{flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0}}>
          <div className="section-title">TERMINAL DIAGNOSTIC</div>
          <div className="terminal" style={{marginTop: '10px', flex: 1, minHeight: 0}}>
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
          src={connected ? "/api/v1/camera/video_feed" : "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1200"} 
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
             ALT: {altitude}mm<br/>
             STB: {balancing ? 'ACTIVE' : 'OFF'}
          </div>
        </div>
      </main>

      {/* Central Control Bay (Under Camera) */}
      <div className="controls-bay">
        <section>
          <div className="section-title">NAVIGATION & VITESSE</div>
          <div style={{display: 'flex', justifyContent: 'space-around', margin: '15px 0', gap: '10px'}}>
            <button 
              className={`status-pill ${actionMode === 'linear' ? 'online' : 'offline'}`}
              onClick={() => setActionMode('linear')}
              style={{cursor: 'pointer', flex: 1}}
            >
              LINÉAIRE
            </button>
            <button 
              className={`status-pill ${actionMode === 'rotate' ? 'online' : 'offline'}`}
              onClick={() => setActionMode('rotate')}
              style={{cursor: 'pointer', flex: 1}}
            >
              ROTATION
            </button>
          </div>
          <div className="slider-group">
              <label>MODULATION VITESSE <span>{speed}</span></label>
              <input 
                type="range" 
                min="2" 
                max="10" 
                value={speed} 
                onChange={(e) => setSpeed(parseInt(e.target.value))}
                style={{width: '100%'}}
              />
          </div>
        </section>

        <section>
          <div className="section-title">SYSTÈMES & ALLURE</div>
          <div style={{display: 'flex', justifyContent: 'space-around', margin: '15px 0', gap: '10px'}}>
            <button 
              className={`status-pill ${gaitMode === '1' ? 'online' : 'offline'}`}
              onClick={() => { setGaitMode('1'); addLog('GAIT: TRIPOD'); }}
              style={{cursor: 'pointer', flex: 1}}
            >
              TRIPOD
            </button>
            <button 
              className={`status-pill ${gaitMode === '2' ? 'online' : 'offline'}`}
              onClick={() => { setGaitMode('2'); addLog('GAIT: WAVE'); }}
              style={{cursor: 'pointer', flex: 1}}
            >
              WAVE
            </button>
          </div>
          <div style={{display: 'flex', gap: '10px'}}>
            <button 
              className={`status-pill ${balancing ? 'online' : 'offline'}`}
              onClick={() => {
                const newState = !balancing;
                setBalancing(newState);
                sendCommand({ cmd: 'balance', enabled: newState });
                addLog(newState ? 'STABILISATION ACTIVE' : 'STABILISATION PASSIVE');
              }}
              style={{cursor: 'pointer', flex: 1}}
            >
              STABILISER
            </button>
            <button 
              className={`status-pill ${relaxed ? 'error' : 'offline'}`}
              onClick={() => {
                const newState = !relaxed;
                setRelaxed(newState);
                sendCommand({ cmd: 'relax', enabled: newState });
                addLog(newState ? 'SERVO POWER OFF (RELAX)' : 'SERVO POWER ON');
              }}
              style={{cursor: 'pointer', flex: 1}}
            >
              {relaxed ? 'ACTIVER' : 'RELAX'}
            </button>
          </div>
          <div style={{display: 'flex', flexDirection: 'column', gap: '5px', marginTop: '10px'}}>
             <div style={{display: 'flex', gap: '5px'}}>
               <button className={`status-pill ${sonarEnabled ? 'online' : 'offline'}`} onClick={() => { setSonarEnabled(!sonarEnabled); sendCommand({cmd: 'sonar', enabled: !sonarEnabled}); }} style={{cursor: 'pointer', fontSize: '0.6rem', flex: 1}}>SNR: {sonarEnabled ? 'ON' : 'OFF'}</button>
               <button className={`status-pill ${cameraEnabled ? 'online' : 'offline'}`} onClick={() => { setCameraEnabled(!cameraEnabled); sendCommand({cmd: 'camera_toggle', enabled: !cameraEnabled}); }} style={{cursor: 'pointer', fontSize: '0.6rem', flex: 1}}>CAM: {cameraEnabled ? 'ON' : 'OFF'}</button>
             </div>
             <button className={`status-pill ${faceEnabled ? 'online' : 'offline'}`} onClick={() => { setFaceEnabled(!faceEnabled); sendCommand({cmd: 'face', enabled: !faceEnabled}); }} style={{cursor: 'pointer', fontSize: '0.6rem', width: '100%'}}>RECON. FACIALE: {faceEnabled ? 'ON' : 'OFF'}</button>
             <button 
                className="status-pill online" 
                onClick={() => sendCommand({cmd: 'buzzer', enabled: true})} 
                style={{cursor: 'pointer', fontSize: '0.6rem', width: '100%', marginTop: '5px', background: '#f1c40f', color: '#000'}}
              >
                BEEP (SIGNAL SONORE)
              </button>
          </div>
        </section>

        <section>
          <div className="section-title">POSTURE & ALTITUDE</div>
          <div className="sliders" style={{marginTop: '10px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px'}}>
            <div className="slider-group">
                <label>ROLL <span>0°</span></label>
                <input type="range" min="-15" max="15" defaultValue="0" onChange={(e) => sendCommand({cmd: 'attitude', roll: parseFloat(e.target.value)})}/>
            </div>
            <div className="slider-group">
                <label>PITCH <span>0°</span></label>
                <input type="range" min="-15" max="15" defaultValue="0" onChange={(e) => sendCommand({cmd: 'attitude', pitch: parseFloat(e.target.value)})}/>
            </div>
            <div className="slider-group">
                <label>ALTITUDE <span>{altitude}</span></label>
                <input type="range" min="-150" max="-50" value={altitude} onChange={(e) => {
                  const val = parseInt(e.target.value);
                  setAltitude(val);
                  sendCommand({cmd: 'height', value: val});
                }}/>
            </div>
            <button className="status-pill online" style={{cursor: 'pointer', fontSize: '0.6rem'}} onClick={() => sendCommand({cmd: 'stand'})}>RESET POSTURE</button>
          </div>
        </section>
      </div>

      {/* Right Panel: Joysticks Only */}
      <aside className="panel panel-right">
        <section>
          <div className="section-title">DIRECTION</div>
          <div className="joystick-container" ref={moveJoystickRef} style={{height: '180px'}}>
            <div className="joystick-base"></div>
          </div>
        </section>

        <section>
          <div className="section-title">TÊTE / CAMÉRA</div>
          <div className="joystick-container" ref={headJoystickRef} style={{height: '180px'}}>
            <div className="joystick-base"></div>
          </div>
          <div style={{textAlign: 'center', fontSize: '0.7rem', color: 'var(--neon-blue)', marginTop: '5px'}}>
            PAN: {headPos.h} | TILT: {headPos.v}
          </div>
        </section>
      </aside>

    </div>
  );
};

export default App;
