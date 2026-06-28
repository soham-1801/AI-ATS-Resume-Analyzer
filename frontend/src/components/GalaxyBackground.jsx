import { useMemo } from 'react';
import './GalaxyBackground.css';

// Generate random coordinates for stars
const generateStars = (count) => {
  let value = `${Math.random() * 2000}px ${Math.random() * 2000}px #FFF`;
  for (let i = 1; i < count; i++) {
    value += `, ${Math.random() * 2000}px ${Math.random() * 2000}px #FFF`;
  }
  return value;
};

const GalaxyBackground = () => {
  const starsSmall = useMemo(() => generateStars(700), []);
  const starsMedium = useMemo(() => generateStars(200), []);
  const starsLarge = useMemo(() => generateStars(50), []);

  return (
    <div className="galaxy-wrapper absolute inset-0 z-0 overflow-hidden bg-[#030514]">
      {/* Dynamic Nebula Layer */}
      <div className="absolute inset-0 opacity-50 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/40 via-[#030514] to-[#030514]" />
      <div className="nebula-layer nebula-1" />
      <div className="nebula-layer nebula-2" />
      
      {/* 3D Rotating Stars */}
      <div className="stars-container">
        <div className="stars-layer stars-small" style={{ boxShadow: starsSmall }} />
        <div className="stars-layer stars-medium" style={{ boxShadow: starsMedium }} />
        <div className="stars-layer stars-large" style={{ boxShadow: starsLarge }} />
      </div>
    </div>
  );
};

export default GalaxyBackground;
