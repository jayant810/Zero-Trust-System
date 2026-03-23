import { useState, useMemo } from 'react'
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

  const fingerprint = useMemo(() => {
    const components = [
      navigator.language,
      screen.colorDepth,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset(),
      navigator.hardwareConcurrency || 'unknown',
      (navigator as any).deviceMemory || 'unknown'
    ];
    return btoa(components.join('|'));
  }, []);

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
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-Device-Fingerprint': fingerprint
        }
      })
      
      const { access_token, refresh_token } = response.data
      setToken(access_token)
      localStorage.setItem('zt_token', access_token)
      localStorage.setItem('zt_refresh_token', refresh_token)
      
      setApiResult(null)
      addLog('POST', '/auth/login', 200, 'Login Successful', 'success')
    } catch (error: any) {
      const status = error.response?.status || 500
      const detail = error.response?.data?.detail || 'Login Failed'
      addLog('POST', '/auth/login', status, detail, 'error')
    }
  }

  const handleLogout = async () => {
    try {
      if (token) {
        await axios.post(`${BASE_URL}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })
      }
    } catch (e) {}
    
    setToken(null)
    localStorage.removeItem('zt_token')
    localStorage.removeItem('zt_refresh_token')
    setApiResult(null)
    addLog('INFO', 'Logout', 0, 'Session cleared.', 'warning')
  }

  const callApi = async (endpoint: string, customHeaders = {}) => {
    if (!token) return
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Device-Fingerprint': fingerprint,
          ...customHeaders
        }
      })
      setApiResult(response.data)
      addLog('GET', endpoint, 200, `Access Granted (Score: ${response.data.risk_score})`, 'success')
    } catch (error: any) {
      const status = error.response?.status || 500
      const detail = error.response?.data?.detail || 'Access Denied'
      addLog('GET', endpoint, status, detail, 'error')
      setApiResult({ error: detail, status })
    }
  }

  return (
    <div className="container">
      <header>
        <h1>🛡️ Zero Trust Security Lab</h1>
        <p className="subtitle">Risk Engine & Policy Enforcement</p>
      </header>

      <div className="grid">
        <section className="card">
          <h2>🔑 1. Authentication</h2>
          {!token ? (
            <form onSubmit={handleLogin}>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
              <button type="submit">Login</button>
            </form>
          ) : (
            <div className="auth-status">
              <p>✅ Logged in as <strong>{email}</strong></p>
              <button onClick={handleLogout} className="btn-secondary">Logout</button>
            </div>
          )}
        </section>

        <section className="card">
          <h2>🧬 2. Context Info</h2>
          <div className="context-item">
             <label>Device Fingerprint Hash</label>
             <code className="context-box">{fingerprint.substring(0, 30)}...</code>
          </div>
          <div className="context-item" style={{marginTop: '1rem'}}>
             <label>Dynamic Risk Status</label>
             <span className="badge" style={{background: '#2563eb', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px'}}>ACTIVE</span>
          </div>
        </section>

        <section className="card">
          <h2>🔍 3. Policy Enforcement</h2>
          <div className="btn-group">
            <button onClick={() => callApi('/api/dashboard')}>Dashboard (Score &lt; 60)</button>
            <button onClick={() => callApi('/api/admin')} className="btn-admin">Admin Portal (Score &lt; 20)</button>
          </div>
        </section>

        <section className="card">
          <h2>🔥 4. Risk Engine Attacks</h2>
          <div className="btn-group">
            <button onClick={() => callApi('/api/dashboard', { 'X-Device-Fingerprint': 'TAMPERED-ID' })} className="btn-danger">Simulate Device Change</button>
            <button onClick={() => callApi('/api/admin', { 'X-Device-Fingerprint': 'TAMPERED-ID' })} className="btn-danger">Simulate Admin Breach</button>
          </div>
        </section>
      </div>

      <section className="log-section card">
        <h2>📜 Security Event Logs</h2>
        <div className="log-container">
          {logs.length === 0 ? (
            <div className="empty-log">No logs captured yet. Perform actions to see events.</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className={`log-entry ${log.type}`}>
                <span className="timestamp">[{log.timestamp}]</span>
                <span className="method">{log.method}</span>
                <span className="endpoint">{log.endpoint}</span>
                <span className="status">({log.status})</span>
                <span className="message">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </section>

      {apiResult && (
        <section className="card" style={{marginTop: '2rem'}}>
          <h2>📊 API Response</h2>
          <div className={`result-box ${apiResult.error ? 'error' : 'success'}`}>
             <pre>{JSON.stringify(apiResult, null, 2)}</pre>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
