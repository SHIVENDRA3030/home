import { useMemo } from 'react'
import { motion } from 'framer-motion'

function formatINR(num) {
  const n = Math.round(num).toString()
  if (n.length <= 3) return '₹' + n
  let result = n.substring(n.length - 3)
  let rem = n.substring(0, n.length - 3)
  while (rem.length > 0) {
    const chunk = rem.substring(Math.max(0, rem.length - 2))
    result = chunk + ',' + result
    rem = rem.substring(0, Math.max(0, rem.length - 2))
  }
  return '₹' + result
}

function formatINRShort(num) {
  if (num >= 10000000) return '₹' + (num / 10000000).toFixed(2) + ' Cr'
  if (num >= 100000) return '₹' + (num / 100000).toFixed(2) + ' L'
  return formatINR(num)
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
}

export default function ResultCard({ result }) {
  const {
    predicted_price, price_range_low, price_range_high,
    price_per_sqft, luxury_label, luxury_emoji,
    emi_monthly, city, locality, property_type, area, bedrooms, bathrooms,
  } = result

  const luxuryClass = luxury_label.replace(/\s+/g, '-')

  return (
    <motion.div className="card result-card" variants={container} initial="hidden" animate="show">
      {/* Header */}
      <motion.div className="result-header" variants={item}>
        <div className="result-location">
          📍 {locality}, {city}
        </div>
        <div className={`luxury-badge ${luxuryClass}`}>
          {luxury_emoji} {luxury_label}
        </div>
      </motion.div>

      {/* Hero price */}
      <motion.div className="price-hero" variants={item}>
        <span className="price-label">Estimated Market Value</span>
        <span className="price-value">{formatINR(predicted_price)}</span>
        <span className="price-per-sqft">{formatINR(price_per_sqft)} / sqft</span>
      </motion.div>

      {/* Tiles */}
      <motion.div className="result-grid" variants={item}>
        <div className="result-tile">
          <span className="tile-label">Price Range (80% CI)</span>
          <span className="tile-value">
            {formatINRShort(price_range_low)} – {formatINRShort(price_range_high)}
          </span>
        </div>
        <div className="result-tile">
          <span className="tile-label">Est. Monthly EMI</span>
          <span className="tile-value">{formatINR(emi_monthly)} / mo</span>
        </div>
      </motion.div>

      {/* Property details chips */}
      <motion.div className="result-details" variants={item}>
        <div className="detail-chip">
          <span className="emoji">🏗️</span>
          <span>{property_type}</span>
        </div>
        <div className="detail-chip">
          <span className="emoji">📐</span>
          <span>{area.toLocaleString()} sqft</span>
        </div>
        <div className="detail-chip">
          <span className="emoji">🛏️</span>
          <span>{bedrooms} BHK / {bathrooms} Bath</span>
        </div>
      </motion.div>

      {/* Footer */}
      <motion.div className="result-footer" variants={item}>
        <small>
          Estimate based on ML model trained on 10,000+ property records across 8 Indian cities
          &nbsp;·&nbsp; 80% prediction interval via quantile regression &nbsp;·&nbsp; 8.5% / 20yr EMI
        </small>
      </motion.div>
    </motion.div>
  )
}
