import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import PropertyForm from './components/PropertyForm'
import ResultCard from './components/ResultCard'
import ErrorCard from './components/ErrorCard'
import ModelInfo from './components/ModelInfo'
import ShaderBackground from './components/ShaderBackground'
import './App.css'

const API_BASE = '/api'

export default function App() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/config`)
      .then(r => r.json())
      .then(setConfig)
      .catch(() => setError('Failed to load configuration'))

    fetch(`${API_BASE}/model-info`)
      .then(r => r.json())
      .then(setModelInfo)
      .catch(() => {})
  }, [])

  const handlePredict = useCallback(async (payload) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Prediction failed')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleReset = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])

  return (
    <div className="app">
      {/* WebGL Animated Background */}
      <ShaderBackground />

      <Header config={config} />

      <main className="main">
        <div className="container">
          <PropertyForm
            config={config}
            onPredict={handlePredict}
            onReset={handleReset}
            loading={loading}
          />

          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.3 }}
              >
                <ErrorCard message={error} onDismiss={() => setError(null)} />
              </motion.div>
            )}

            {result && (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 24, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -24, scale: 0.98 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              >
                <ResultCard result={result} />
              </motion.div>
            )}
          </AnimatePresence>

          {modelInfo && !result && !error && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <ModelInfo info={modelInfo} />
            </motion.div>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>HomeValue AI v2 — ML-powered property estimation for Indian real estate</p>
        </div>
      </footer>
    </div>
  )
}
