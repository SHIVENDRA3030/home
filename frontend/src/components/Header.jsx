import { motion } from 'framer-motion'

export default function Header({ config }) {
  return (
    <header className="header">
      <div className="header-inner">
        <motion.div
          className="header-top"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="logo-icon">🏠</div>
          <div className="logo-text">
            <h1>Home<span className="accent">Value</span> AI</h1>
            <p className="subtitle">ML-powered property price prediction across 7 Indian cities</p>
          </div>
        </motion.div>

        <motion.div
          className="stats-row"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
        >
          <div className="stat">
            <span className="stat-value">7</span>
            <span className="stat-label">Cities</span>
          </div>
          <div className="stat">
            <span className="stat-value">140+</span>
            <span className="stat-label">Localities</span>
          </div>
          <div className="stat">
            <span className="stat-value">16</span>
            <span className="stat-label">Amenities</span>
          </div>
          <div className="stat">
            <span className="stat-value">3</span>
            <span className="stat-label">Property Types</span>
          </div>
          <div className="stat">
            <span className="stat-value">14K+</span>
            <span className="stat-label">Training Data</span>
          </div>
        </motion.div>
      </div>
    </header>
  )
}
