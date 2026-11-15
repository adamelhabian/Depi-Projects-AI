import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

/**
 * Smooth, accessible page transition for workspace hash routes.
 * Preserves exact layout while providing a calm, polished feel.
 */
export function PageTransition({ children, routeKey }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      key={routeKey}
      initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: -6 }}
      transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
      className="page-transition-wrapper"
    >
      {children}
    </motion.div>
  );
}

/**
 * Animated counter that counts up to the target number with spring easing.
 * Always formats with Western Arabic digits (0-9).
 */
export function AnimatedCounter({ value, duration = 0.8, prefix = '', suffix = '' }) {
  const shouldReduceMotion = useReducedMotion();
  const numValue = typeof value === 'number' ? value : NaN;
  const isNumeric = Number.isFinite(numValue);
  const [displayValue, setDisplayValue] = useState(() => (shouldReduceMotion || !isNumeric ? value : 0));

  useEffect(() => {
    if (shouldReduceMotion || !isNumeric) {
      setDisplayValue(value);
      return;
    }

    let start = 0;
    const end = numValue;
    const startTime = performance.now();
    const durationMs = duration * 1000;

    let frameId;
    const tick = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / durationMs, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + (end - start) * eased);
      setDisplayValue(current);

      if (progress < 1) {
        frameId = requestAnimationFrame(tick);
      } else {
        setDisplayValue(end);
      }
    };

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [value, isNumeric, numValue, duration, shouldReduceMotion]);

  if (!isNumeric) {
    return <span>{value}</span>;
  }

  return (
    <span>
      {prefix}
      {displayValue}
      {suffix}
    </span>
  );
}

/**
 * Interactive card wrapper that adds refined hover lift and tap feedback
 * without altering any existing layout or borders.
 */
export function InteractiveItem({ children, className = '', as = 'div', ...props }) {
  const shouldReduceMotion = useReducedMotion();
  const Component = motion[as] || motion.div;

  if (shouldReduceMotion) {
    const Tag = as;
    return <Tag className={className} {...props}>{children}</Tag>;
  }

  return (
    <Component
      className={className}
      whileHover={{ y: -2, transition: { duration: 0.16, ease: 'easeOut' } }}
      whileTap={{ scale: 0.99, transition: { duration: 0.08 } }}
      {...props}
    >
      {children}
    </Component>
  );
}

/**
 * Segmented control with smooth sliding active pill indicator (layoutId).
 * Matches the existing .segmented design system styling.
 */
export function AnimatedSegmented({ items, selected, onChange, ariaLabel, layoutId = 'segmented-indicator' }) {
  return (
    <div className="segmented animated-segmented" aria-label={ariaLabel}>
      {items.map(([key, label]) => {
        const isSelected = selected === key;
        return (
          <button
            type="button"
            key={key}
            aria-pressed={isSelected}
            className={isSelected ? 'selected' : ''}
            onClick={() => onChange(key)}
            style={{ position: 'relative' }}
          >
            {isSelected && (
              <motion.span
                layoutId={layoutId}
                className="segmented-pill-bg"
                transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                style={{
                  position: 'absolute',
                  inset: 0,
                  borderRadius: 'inherit',
                  background: 'var(--md-sys-color-secondary-container)',
                  zIndex: 0,
                }}
              />
            )}
            <span style={{ position: 'relative', zIndex: 1 }}>{label}</span>
          </button>
        );
      })}
    </div>
  );
}
