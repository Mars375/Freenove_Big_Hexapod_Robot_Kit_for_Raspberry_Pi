/**
 * Hexapod Web Controller
 * Handles WebSocket communication and control inputs.
 */

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
let socket = null;

const logContainer = document.getElementById('log-container');
const wsStatus = document.getElementById('ws-status');
const sonarDisplay = document.getElementById('distance-overlay');

function addLog(msg, type = 'normal') {
  const div = document.createElement('div');
  div.className = `log-entry ${type}`;
  div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  logContainer.appendChild(div);
  logContainer.scrollTop = logContainer.scrollHeight;
}

function connect() {
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    wsStatus.textContent = 'ONLINE';
    wsStatus.className = 'value connected';
    addLog('Connected to robot', 'system');
  };

  socket.onclose = () => {
    wsStatus.textContent = 'OFFLINE';
    wsStatus.className = 'value disconnected';
    addLog('Disconnected from robot', 'danger');
    setTimeout(connect, 3000); // Reconnect
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'telemetry') {
      if (data.ultrasonic) {
        sonarDisplay.textContent = `Sonar: ${data.ultrasonic} cm`;
      }
    }
  };
}

// Initialize Joysticks
const joyMove = nipplejs.create({
  zone: document.getElementById('joy-move'),
  mode: 'static',
  position: { left: '50%', top: '50%' },
  color: '#00d2ff'
});

joyMove.on('move', (evt, data) => {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;

  // Map polar to cartesian movement
  const dist = data.distance; // 0 to 50
  const angle = data.angle.degree;
  const rad = data.angle.radian;

  // Forward = 90, Back = 270, Right = 0, Left = 180
  const x = Math.round(Math.cos(rad) * 35 * (dist / 50));
  const y = Math.round(Math.sin(rad) * 35 * (dist / 50));

  sendCommand({
    cmd: "move",
    mode: "custom",
    x: x,
    y: y,
    speed: 5
  });
});

joyMove.on('end', () => {
  sendCommand({ cmd: "stop" });
});

function sendCommand(data) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  }
}

// Attitude Sliders
const updateAttitude = () => {
  sendCommand({
    cmd: "attitude",
    roll: parseFloat(document.getElementById('roll-slider').value),
    pitch: parseFloat(document.getElementById('pitch-slider').value),
    yaw: parseFloat(document.getElementById('yaw-slider').value)
  });
};

['roll-slider', 'pitch-slider', 'yaw-slider'].forEach(id => {
  document.getElementById(id).addEventListener('input', updateAttitude);
});

document.getElementById('height-slider').addEventListener('input', (e) => {
  sendCommand({
    cmd: "position",
    x: 0, y: 0,
    z: parseFloat(e.target.value)
  });
});

// Buttons
document.getElementById('btn-stand').addEventListener('click', () => {
  sendCommand({ cmd: "stand" });
});

document.getElementById('btn-stop').addEventListener('click', () => {
  sendCommand({ cmd: "stop" });
});

// Start
connect();
