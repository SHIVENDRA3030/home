import { useState, useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'

const AMENITY_ICONS = {
  parking: '🅿️',
  pool: '🏊',
  garden: '🌿',
  gym: '💪',
  security: '🔒',
  lift: '🛗',
  power_backup: '🔋',
  modular_kitchen: '🍳',
  clubhouse: '🏛️',
  children_play: '🎠',
  jogging_track: '🏃',
  sports_court: '🎾',
  rainwater_harvesting: '🌧️',
  solar_panels: '☀️',
  smart_home: '🤖',
  servant_room: '🛏️',
}

const AMENITY_LABELS = {
  parking: 'Parking',
  pool: 'Pool',
  garden: 'Garden',
  gym: 'Gym',
  security: 'Security',
  lift: 'Lift',
  power_backup: 'Power Backup',
  modular_kitchen: 'Mod. Kitchen',
  clubhouse: 'Clubhouse',
  children_play: 'Kids Play',
  jogging_track: 'Jogging',
  sports_court: 'Sports',
  rainwater_harvesting: 'Rainwater',
  solar_panels: 'Solar',
  smart_home: 'Smart Home',
  servant_room: 'Servant Room',
}

const INITIAL_FORM = {
  city: '',
  locality: '',
  property_type: 'Apartment',
  area: '',
  bedrooms: '3',
  bathrooms: '2',
  furnishing: 'Unfurnished',
  age: '0',
  floor: '0',
}

export default function PropertyForm({ config, onPredict, onReset, loading }) {
  const [form, setForm] = useState(INITIAL_FORM)
  const [amenities, setAmenities] = useState({})
  const [errors, setErrors] = useState({})

  const localities = useMemo(() => {
    if (!config?.cities || !form.city) return []
    return config.cities[form.city] || []
  }, [config, form.city])

  const amenityCount = useMemo(
    () => Object.values(amenities).filter(Boolean).length,
    [amenities]
  )

  const handleChange = useCallback((field, value) => {
    setForm(prev => {
      const next = { ...prev, [field]: value }
      if (field === 'city') next.locality = ''
      return next
    })
    setErrors(prev => ({ ...prev, [field]: undefined }))
  }, [])

  const toggleAmenity = useCallback((amenity) => {
    setAmenities(prev => ({ ...prev, [amenity]: !prev[amenity] }))
  }, [])

  const validate = useCallback(() => {
    const errs = {}
    if (!form.city) errs.city = 'Required'
    if (!form.locality) errs.locality = 'Required'
    if (!form.area || parseInt(form.area) < 100 || parseInt(form.area) > 10000) errs.area = '100–10,000 sqft'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }, [form])

  const handleSubmit = useCallback((e) => {
    e.preventDefault()
    if (!validate()) return

    const payload = {
      city: form.city,
      locality: form.locality,
      property_type: form.property_type,
      area: parseInt(form.area),
      bedrooms: parseInt(form.bedrooms),
      bathrooms: parseInt(form.bathrooms),
      furnishing: form.furnishing,
      age: parseInt(form.age || 0),
      floor: parseInt(form.floor || 0),
    }

    // Add amenities
    config?.amenities?.forEach(a => {
      payload[a] = amenities[a] ? 1 : 0
    })

    onPredict(payload)
  }, [form, amenities, config, validate, onPredict])

  const handleReset = useCallback(() => {
    setForm(INITIAL_FORM)
    setAmenities({})
    setErrors({})
    onReset()
  }, [onReset])

  if (!config) {
    return (
      <div className="card form-section" style={{ textAlign: 'center', padding: '3rem' }}>
        <div className="spinner" />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading configuration...</p>
      </div>
    )
  }

  return (
    <motion.form
      className="card form-section"
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* ── Location & Property ──────────────────────────── */}
      <div className="section-title">
        <span className="icon">📍</span>
        <h2>Location & Property</h2>
      </div>

      <div className="form-row cols-2">
        <div className="form-group">
          <label htmlFor="city">City</label>
          <select
            id="city"
            value={form.city}
            onChange={e => handleChange('city', e.target.value)}
            style={errors.city ? { borderColor: 'var(--rose)' } : {}}
          >
            <option value="">Select City</option>
            {Object.keys(config.cities).map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="locality">Locality</label>
          <select
            id="locality"
            value={form.locality}
            onChange={e => handleChange('locality', e.target.value)}
            disabled={!form.city}
            style={errors.locality ? { borderColor: 'var(--rose)' } : {}}
          >
            <option value="">{form.city ? 'Select Locality' : 'Select city first'}</option>
            {localities.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row cols-2">
        <div className="form-group">
          <label htmlFor="property_type">Property Type</label>
          <select
            id="property_type"
            value={form.property_type}
            onChange={e => handleChange('property_type', e.target.value)}
          >
            {config.property_types.map(pt => (
              <option key={pt} value={pt}>{pt}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="furnishing">Furnishing</label>
          <select
            id="furnishing"
            value={form.furnishing}
            onChange={e => handleChange('furnishing', e.target.value)}
          >
            {config.furnishing_options.map(f => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ── Property Details ─────────────────────────────── */}
      <div className="section-title" style={{ marginTop: '0.5rem' }}>
        <span className="icon">📐</span>
        <h2>Property Details</h2>
      </div>

      <div className="form-row cols-3">
        <div className="form-group">
          <label htmlFor="area">Area (sqft)</label>
          <input
            type="number"
            id="area"
            placeholder="e.g. 1200"
            min="100"
            max="10000"
            value={form.area}
            onChange={e => handleChange('area', e.target.value)}
            style={errors.area ? { borderColor: 'var(--rose)' } : {}}
          />
        </div>
        <div className="form-group">
          <label htmlFor="bedrooms">Bedrooms</label>
          <select
            id="bedrooms"
            value={form.bedrooms}
            onChange={e => handleChange('bedrooms', e.target.value)}
          >
            {[1,2,3,4,5,6].map(n => (
              <option key={n} value={n}>{n} BHK</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="bathrooms">Bathrooms</label>
          <select
            id="bathrooms"
            value={form.bathrooms}
            onChange={e => handleChange('bathrooms', e.target.value)}
          >
            {[1,2,3,4].map(n => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row cols-2">
        <div className="form-group">
          <label htmlFor="age">Property Age (years)</label>
          <input
            type="number"
            id="age"
            min="0"
            max="50"
            value={form.age}
            onChange={e => handleChange('age', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="floor">Floor Number</label>
          <input
            type="number"
            id="floor"
            min="0"
            max="50"
            value={form.floor}
            onChange={e => handleChange('floor', e.target.value)}
          />
        </div>
      </div>

      {/* ── Amenities ────────────────────────────────────── */}
      <div className="section-title" style={{ marginTop: '0.5rem' }}>
        <span className="icon">✨</span>
        <h2>Amenities & Features</h2>
        <span className="badge">{amenityCount} selected</span>
      </div>

      <div className="amenities-grid">
        {config.amenities.map(amenity => (
          <label key={amenity} className="amenity-chip">
            <input
              type="checkbox"
              checked={!!amenities[amenity]}
              onChange={() => toggleAmenity(amenity)}
            />
            <span className="chip-label">
              {AMENITY_ICONS[amenity] || '•'} {AMENITY_LABELS[amenity] || amenity}
            </span>
          </label>
        ))}
      </div>

      {/* ── Buttons ──────────────────────────────────────── */}
      <div className="button-group">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2, margin: 0 }} />
              Predicting...
            </>
          ) : (
            <>
              Predict Price <span className="btn-arrow">→</span>
            </>
          )}
        </button>
        <button type="button" className="btn btn-secondary" onClick={handleReset}>
          Reset
        </button>
      </div>
    </motion.form>
  )
}
