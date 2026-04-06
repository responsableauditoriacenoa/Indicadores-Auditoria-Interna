"use client";

import { useTheme } from "./ThemeProvider";
import { Moon, Sun, LayoutDashboard } from "lucide-react";

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav style={{ 
      padding: '1rem 2rem', 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      borderBottom: '1px solid var(--surface-border)',
      background: 'var(--surface-color)',
      backdropFilter: 'var(--blur-glass)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ 
          background: 'var(--accent-gradient)', 
          padding: '0.5rem', 
          borderRadius: '12px',
          color: 'white',
          display: 'flex'
        }}>
          <LayoutDashboard size={24} />
        </div>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          Auditoría<span style={{ color: 'var(--accent-primary)' }}>Tracker</span>
        </h1>
      </div>

      <button 
        onClick={toggleTheme} 
        className="btn-icon"
        aria-label="Toggle Theme"
      >
        {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
      </button>
    </nav>
  );
}
