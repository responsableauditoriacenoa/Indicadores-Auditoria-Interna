export interface AuditItem {
  id: string;
  codigoAuditoria: string;
  mesPlanificado: string;
  empresa: string;
  sucursal: string;
  eventoAuditoria: string;
  sector: string;
  provincia: string;
  auditor: string;
  fechaInicio: string;
  fechaFin: string;
  fechaVencimiento: string;
  estado: string;
  conclusion: string;
  puntaje: number | null;
  horasPlanificadas: number;
  cantidadHoras: number;
}
