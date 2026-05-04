import { motion } from 'framer-motion'

export default function ModelInfo({ info }) {
  if (!info || !info.all_models) return null

  const bestModel = info.best_model
  const models = Object.entries(info.all_models)
  const maxR2 = Math.max(...models.map(([, m]) => m.r2))

  return (
    <div className="model-info">
      <div className="card">
        {/* Stats tiles */}
        <div className="info-grid">
          <div className="info-tile accent">
            <span className="value">{info.dataset?.rows?.toLocaleString() || '—'}</span>
            <span className="label">Training Records</span>
          </div>
          <div className="info-tile green">
            <span className="value">{info.metrics?.r2?.toFixed(3) || '—'}</span>
            <span className="label">R² Score</span>
          </div>
          <div className="info-tile coral">
            <span className="value">
              {info.metrics?.mape ? `${info.metrics.mape}%` : '—'}
            </span>
            <span className="label">MAPE</span>
          </div>
          <div className="info-tile purple">
            <span className="value">
              {info.prediction_interval?.coverage_80
                ? `${(info.prediction_interval.coverage_80 * 100).toFixed(0)}%`
                : '—'}
            </span>
            <span className="label">80% CI Coverage</span>
          </div>
        </div>

        {/* Model comparison */}
        <div className="model-comparison">
          <h3>Model Comparison (R² Score)</h3>
          {models.map(([name, metrics]) => {
            const isBest = name === bestModel
            const widthPct = Math.max(5, (metrics.r2 / maxR2) * 100)
            return (
              <div key={name} className="model-row">
                <span className={`name ${isBest ? 'best' : ''}`}>
                  {isBest && '★ '}{name}
                </span>
                <div className="model-bar-container">
                  <motion.div
                    className={`model-bar ${isBest ? 'best' : 'normal'}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${widthPct}%` }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  />
                </div>
                <span className={`r2 ${isBest ? 'best' : ''}`}>
                  {metrics.r2.toFixed(4)}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
