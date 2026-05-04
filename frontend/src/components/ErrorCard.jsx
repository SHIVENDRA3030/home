import { motion } from 'framer-motion'

export default function ErrorCard({ message, onDismiss }) {
  return (
    <motion.div
      className="error-card"
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -12, scale: 0.98 }}
    >
      <span className="error-icon">⚠️</span>
      <p>{message}</p>
      <button className="dismiss" onClick={onDismiss} aria-label="Dismiss">×</button>
    </motion.div>
  )
}
