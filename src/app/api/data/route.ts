import { NextResponse } from 'next/server';
import Papa from 'papaparse';
import { AuditItem } from '@/lib/types';

export const revalidate = 60; // Cache the data for 60 seconds

const SHEET_URL = "https://docs.google.com/spreadsheets/d/1rONfVQVzyXIEnhlj2RZvZM4LqSXQ6DyccH6dLyNePc4/export?format=csv&gid=0";

export async function GET() {
  try {
    const response = await fetch(SHEET_URL, {
      next: { revalidate: 60 } // Revalidate every 60 seconds
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch CSV: ${response.status} ${response.statusText}`);
    }

    const csvText = await response.text();

    const result = Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true,
    });

    // Transform and map standard columns to our structured JSON
    const parsedData: AuditItem[] = result.data.map((row: any) => {
      // Normalizing scores
      let puntaje = null;
      if (row['Puntaje']) {
         let p = row['Puntaje'].replace('%', '').trim();
         // If it has comma it's argentine notation, we can replace comma with dot
         p = p.replace(',', '.');
         puntaje = parseFloat(p);
      }

      return {
        id: row['ID Actividad'] || '',
        codigoAuditoria: row['Codigo Auditoría'] || '',
        mesPlanificado: row['Mes Planificado'] || '',
        empresa: row['Empresa'] || '',
        sucursal: row['Sucursal'] || '',
        eventoAuditoria: row['Evento Auditoría'] || '',
        sector: row['Sector'] || '',
        provincia: row['Provincia'] || '',
        auditor: row['Auditor'] || '',
        fechaInicio: row['Fecha Inicio'] || '',
        fechaFin: row['Fecha Fin'] || '',
        fechaVencimiento: row['FechaVencimiento'] || '',
        estado: row['Estado'] || '',
        conclusion: row['Conclusión'] || '',
        puntaje: puntaje,
        horasPlanificadas: parseFloat(row['Horas Planificadas']) || 0,
        cantidadHoras: parseFloat(row['Cantidad Horas']) || 0,
      };
    });

    return NextResponse.json({ success: true, data: parsedData });
  } catch (error: any) {
    console.error("Error fetching sheet data:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
