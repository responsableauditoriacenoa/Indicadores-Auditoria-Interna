"use client";

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { AuditItem } from '@/lib/types';
import KPICard from './KPICard';
import { FileSearch, CheckCircle, Clock, BarChart3, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(result => {
        if(result.success) {
          setData(result.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="btn-icon" style={{ animation: 'spin 1s linear infinite', margin: '0 auto', borderTopColor: 'var(--accent-primary)' }}></div>
          <p className="text-muted" style={{ marginTop: '1rem' }}>Sincronizando con Google Sheets...</p>
        </div>
        <style jsx>{`
          @keyframes spin { 100% { transform: rotate(360deg); } }
        `}</style>
      </div>
    );
  }

  // --- KPI LOGIC ---
  const totalAudits = data.length;
  const completed = data.filter(d => d.estado?.toLowerCase().includes('culminado')).length;
  const inProgress = data.filter(d => d.estado?.toLowerCase().includes('en proceso')).length;
  
  const completionRate = totalAudits > 0 ? Math.round((completed / totalAudits) * 100) : 0;

  let totalScore = 0;
  let scoredItems = 0;
  data.forEach(d => {
    if (d.puntaje !== null && !isNaN(d.puntaje)) {
      totalScore += d.puntaje;
      scoredItems++;
    }
  });
  const avgScore = scoredItems > 0 ? ((totalScore / scoredItems) * 100).toFixed(1) : '0.0';

  let totalHsPlan = 0;
  let totalHsReal = 0;
  data.forEach(d => {
    totalHsPlan += d.horasPlanificadas || 0;
    totalHsReal += d.cantidadHoras || 0;
  });

  // Data for Pie Chart (Status)
  const statusCounts = data.reduce((acc, curr) => {
    const s = curr.estado || 'Desconocido';
    acc[s] = (acc[s] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.keys(statusCounts).map(k => ({ name: k, value: statusCounts[k] }));
  const COLORS = ['#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6', '#64748b'];

  // Data for Bar Chart (Conclusion)
  const conclusionCounts = data.reduce((acc, curr) => {
    let c = curr.conclusion || 'Sin Conclusión';
    if(c.trim() === '') c = 'Sin Conclusión';
    acc[c] = (acc[c] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const barData = Object.keys(conclusionCounts).map(k => ({ name: k, count: conclusionCounts[k] }))
    .sort((a,b) => b.count - a.count);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', paddingBottom: '2rem' }}>
      
      {/* Header */}
      <div>
        <h2 className="heading-primary">Resumen Ejecutivo</h2>
        <p className="text-muted">Desempeño general basado en la Solapa de Seguimiento de Auditoría.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4">
        <KPICard 
          title="Total Auditorías" 
          value={totalAudits} 
          icon={<FileSearch />} 
        />
        <KPICard 
          title="Tasa de Finalización" 
          value={`${completionRate}%`} 
          icon={<CheckCircle />} 
          trend={{ value: `${completed} listas`, isPositive: true }}
        />
        <KPICard 
          title="Desempeño Promedio" 
          value={`${avgScore}%`} 
          icon={<BarChart3 />} 
          trend={{ value: 'Calificación General', isPositive: parseFloat(avgScore) >= 80 }}
        />
        <KPICard 
          title="Horas Plan. vs Reales" 
          value={`${Math.round(totalHsPlan)} / ${Math.round(totalHsReal)}`} 
          icon={<Clock />} 
          trend={{ value: totalHsReal > totalHsPlan ? 'Exceso' : 'Ahorro', isPositive: totalHsReal <= totalHsPlan }}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2">
        <div className="glass-panel" style={{ padding: '1.5rem', height: '400px' }}>
          <h3 className="heading-secondary">Estado de las Tareas</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="45%"
                innerRadius={80}
                outerRadius={110}
                paddingAngle={5}
                dataKey="value"
                // label={({name, percent}) => `${name} (${(percent * 100).toFixed(0)}%)`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ borderRadius: '12px', background: 'var(--surface-color)', borderColor: 'var(--surface-border)', color: 'var(--text-primary)' }}
                itemStyle={{ color: 'var(--text-primary)' }}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', height: '400px' }}>
          <h3 className="heading-secondary">Distribución de Conclusiones</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={barData}
              margin={{ top: 20, right: 30, left: 0, bottom: 50 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-border)" vertical={false} />
              <XAxis dataKey="name" stroke="var(--text-secondary)" angle={-45} textAnchor="end" height={60} />
              <YAxis stroke="var(--text-secondary)" />
              <Tooltip 
                cursor={{fill: 'var(--surface-border)'}} 
                contentStyle={{ borderRadius: '12px', background: 'var(--surface-color)', borderColor: 'var(--surface-border)', color: 'var(--text-primary)' }}
              />
              <Bar dataKey="count" fill="var(--accent-primary)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Data Table Preview */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
          <h3 className="heading-secondary" style={{ margin: 0 }}>Registro de Auditorías (Últimas 10)</h3>
          <span className="badge badge-info">Sincronizado vía Google Sheets</span>
        </div>
        
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Empresa</th>
                <th>Evento Auditoría</th>
                <th>Auditor</th>
                <th>Estado</th>
                <th>Puntaje</th>
              </tr>
            </thead>
            <tbody>
              {data.slice().reverse().slice(0, 10).map((row, i) => {
                let badgeClass = 'badge-info';
                if(row.estado === 'Culminado') badgeClass = 'badge-success';
                else if(row.estado === 'Suspendido') badgeClass = 'badge-danger';
                else if(row.estado === 'En proceso') badgeClass = 'badge-warning';

                return (
                  <tr key={i}>
                    <td className="font-semibold">{row.codigoAuditoria}</td>
                    <td>{row.empresa} - {row.sucursal}</td>
                    <td style={{ whiteSpace: 'normal', minWidth: '200px' }}>{row.eventoAuditoria}</td>
                    <td>{row.auditor}</td>
                    <td><span className={`badge ${badgeClass}`}>{row.estado}</span></td>
                    <td className="font-semibold text-sm">
                      {row.puntaje !== null ? `${(row.puntaje * 100).toFixed(2)}%` : '--'}
                    </td>
                  </tr>
              )})}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
