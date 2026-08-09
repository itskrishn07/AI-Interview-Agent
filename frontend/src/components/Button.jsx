export default function Button({ children, className = '', variant = 'primary', ...props }) {
  return <button className={`button button-${variant} ${className}`} {...props}>{children}<span className="button-arrow">→</span></button>;
}
