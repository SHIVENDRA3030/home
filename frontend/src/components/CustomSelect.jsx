import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function CustomSelect({ 
  id, 
  value, 
  onChange, 
  options, 
  placeholder, 
  disabled, 
  hasError 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSelect = (val) => {
    onChange(val);
    setIsOpen(false);
  };

  const selectedOption = value 
    ? options.find(opt => (typeof opt === 'object' ? opt.value === value : opt === value))
    : null;
    
  const displayValue = selectedOption 
    ? (typeof selectedOption === 'object' ? selectedOption.label : selectedOption)
    : placeholder;

  return (
    <div 
      className={`custom-select-container ${disabled ? 'disabled' : ''} ${hasError ? 'has-error' : ''}`}
      ref={containerRef}
    >
      <div 
        className="custom-select-trigger"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            setIsOpen(!isOpen);
          }
        }}
      >
        <span className={`selected-text ${!value ? 'placeholder' : ''}`}>
          {displayValue}
        </span>
        <motion.span 
          className="dropdown-icon"
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">
            <path fill="currentColor" d="M6 8L1 3h10z" />
          </svg>
        </motion.span>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="custom-select-dropdown"
            initial={{ opacity: 0, y: -10, scaleY: 0.95 }}
            animate={{ opacity: 1, y: 0, scaleY: 1 }}
            exit={{ opacity: 0, y: -10, scaleY: 0.95 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            style={{ originY: 0 }}
          >
            <ul className="custom-select-list" role="listbox">
              {/* Optional unselect option */}
              <li 
                className={`custom-select-option ${!value ? 'selected' : ''}`}
                onClick={() => handleSelect('')}
                role="option"
                aria-selected={!value}
              >
                {placeholder}
              </li>
              
              {options.map((opt, index) => {
                const optVal = typeof opt === 'object' ? opt.value : opt;
                const optLabel = typeof opt === 'object' ? opt.label : opt;
                const isSelected = value === optVal;
                
                return (
                  <li 
                    key={`${optVal}-${index}`}
                    className={`custom-select-option ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleSelect(optVal)}
                    role="option"
                    aria-selected={isSelected}
                  >
                    {optLabel}
                  </li>
                );
              })}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
