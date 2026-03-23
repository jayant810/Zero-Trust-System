import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const BASE_URL = 'http://127.0.0.1:8000'

interface LogEntry {
  timestamp: string;
  method: string;
  endpoint: string;
  status: number;
  message: string;
  type: 'success' | 'error' | 'warning';
}

function App() {
  const [email, setEmail] = useState('user@zero.trust')
  const [password, setPassword] = useState('user123')
  const [token, setToken] = useState<string | null>(localStorage.getItem('zt_token'))
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [apiResult, setApiResult] = useState<any>(null)
  const [userAgent, setUserAgent] = useState(navigator.userAgent)

  const addLog = (method: string, endpoint: string, status: number, message: string, type: 'success' | 'error' | 'warning') => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      method,
      endpoint,
      status,
      message,
      type
    }
    setLogs(prev => [newLog, ...prev].slice(0, 10))
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const params = new URLSearchParams()
      params.append('username', email)
      params.append('password', password)

      const response = await axios.post(`${BASE_URL}/auth/login`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      const newToken = response.data.access_token
      setToken(newToken)
      localStorage.setItem('zt_token', newToken)
      setApiResult(null) // Clear old errors
      addLog('POST', '/auth/login', 200, 'Login Successful', 'success')
    } catch (error: any) {
      const status = error.response?.status || 500
      const detail = error.response?.data?.detail || 'Login Failed'
      addLog('POST', '/auth/login', status, detail, 'error')
    }
  }

  const handleLogout = () => {
    setToken(null)
    localStorage.removeItem('zt_token')
    setApiResult(null)
    addLog('INFO', 'Logout', 0, 'Session cleared. Please login again.', 'warning')
  }

  const callApi = async (endpoint: string, customHeaders = {}) => {
    if (!token) return
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          ...customHeaders
        }
      })
      setApiResult(response.data)
      addLog('GET', endpoint, 200, 'Access Granted', 'success')
    } catch (error: any) {
      const status = error.response?.status || 500
      const detail = error.response?.data?.detail || 'Access Denied'
      
      // If token is invalid (401), we help the user by suggesting a logout
      if (status === 401) {
        addLog('SECURITY', 'JWT', 401, 'Token is invalid or tampered. Session compromised.', 'error')
      }

      setApiResult({ error: detail, status })
      addLog('GET', endpoint, status, detail, 'error')
    }
  }

  // ATTACK SIMULATIONS
  const simulateDeviceChange = () => {
    addLog('ATTACK', '/api/dashboard', 0, 'Simulating Token Theft (Wrong Device)', 'warning')
    callApi('/api/dashboard', { 'User-Agent': 'Hacker-Browser-9000' })
  }

  const tamperToken = () => {
    if (!token) return
    addLog('ATTACK', 'Local Storage', 0, 'Tampering with JWT Payload', 'warning')
    
    try {
      // Very crude tampering - just to show it breaks signature
      const parts = token.split('.')
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]))
        payload.role = 'admin' // Attempt escalation
        const fakePayload = btoa(JSON.stringify(payload))
        const tamperedToken = `${parts[0]}.${fakePayload}.${parts[2]}`
        
        setToken(tamperedToken)
        localStorage.setItem('zt_token', tamperedToken)
        addLog('INFO', 'JWT', 0, 'Token payload modified (Admin escalation attempt)', 'warning')
      }
    } catch (e) {
      addLog('ERROR', 'JWT', 0, 'Failed to tamper token', 'error')
    }
  }

  return (
    <div className="container">
      <header>
        <h1>🛡️ Zero Trust Security Lab</h1>
        <p className="subtitle">Continuous Verification & RBAC Testing Ground</p>
      </header>

      <div className="grid">
        {/* SECTION 1: AUTHENTICATION */}
        <section className="card">
          <h2>🔑 1. Authentication</h2>
          {!token ? (
            <form onSubmit={handleLogin}>
              <input 
                type="email" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                placeholder="Email"
              />
              <input 
                type="password" 
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                placeholder="Password"
              />
              <button type="submit">Login</button>
              <div className="hint">Try: admin@zero.trust / admin123</div>
            </form>
          ) : (
            <div className="auth-status">
              <p>✅ Logged in as <strong>{email}</strong></p>
              <button onClick={handleLogout} className="btn-secondary">Logout</button>
            </div>
          )}
        </section>

        {/* SECTION 2: CONTEXT INFO */}
        <section className="card">
          <h2>🌐 2. Client Context</h2>
          <div className="context-box">
            <div className="context-item">
              <label>Detected Device (User-Agent):</label>
              <code>{userAgent.substring(0, 50)}...</code>
            </div>
            <div className="context-item">
              <label>API Endpoint:</label>
              <code>{BASE_URL}</code>
            </div>
          </div>
        </section>

        {/* SECTION 3: PROTECTED RESOURCES */}
        <section className="card">
          <h2>🔓 3. Resource Access</h2>
          <div className="btn-group">
            <button disabled={!token} onClick={() => callApi('/api/dashboard')}>Dashboard (All)</button>
            <button disabled={!token} onClick={() => callApi('/api/data')}>Secure Data (All)</button>
            <button disabled={!token} onClick={() => callApi('/api/admin')} className="btn-admin">Admin Portal (Admin Only)</button>
          </div>
          {apiResult && (
            <pre className={`result-box ${apiResult.error ? 'error' : 'success'}`}>
              {JSON.stringify(apiResult, null, 2)}
            </pre>
          )}
        </section>

        {/* SECTION 4: ATTACK SIMULATIONS */}
        <section className="card highlight">
          <h2>🔥 4. Attack Simulations</h2>
          <div className="btn-group">
            <button disabled={!token} onClick={simulateDeviceChange} className="btn-danger">
              Simulate Token Theft (Context Mismatch)
            </button>
            <button disabled={!token} onClick={tamperToken} className="btn-danger">
              Tamper Token (Signature Violation)
            </button>
          </div>
          <p className="hint">These actions intentionally break security rules to test the backend response.</p>
        </section>
      </div>

      {/* SECURITY AUDIT LOG */}
      <section className="card log-section">
        <h2>📜 Security Audit Log (Frontend)</h2>
        <div className="log-container">
          {logs.length === 0 && <p className="empty-log">No activity yet...</p>}
          {logs.map((log, i) => (
            <div key={i} className={`log-entry ${log.type}`}>
              <span className="time">[{log.timestamp}]</span>
              <span className="method">{log.method}</span>
              <span className="endpoint">{log.endpoint}</span>
              <span className="status">Status: {log.status}</span>
              <span className="message">{log.message}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
