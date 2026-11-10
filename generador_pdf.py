from datetime import datetime

from fpdf import FPDF


def generar_reporte_pdf(email_usuario: str, num_archivos: int, stats: dict) -> bytes:
    """Genera un reporte PDF con estilo corporativo y devuelve los bytes para descargarlo."""
    pdf = FPDF()
    pdf.add_page()
    
    # --- Encabezado corporativo (Azul #3b82f6) ---
    pdf.set_fill_color(59, 130, 246)
    pdf.rect(0, 0, 210, 25, 'F')
    
    pdf.set_font("Helvetica", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(8)
    pdf.cell(0, 10, "RowRescue - Reporte de Limpieza", ln=True, align='C')
    
    pdf.ln(15)
    
    # --- Información del proceso ---
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 6, f"Usuario: {email_usuario}", ln=True)
    pdf.set_font("Helvetica", '', 11)
    
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 6, f"Fecha de emision: {fecha_actual}", ln=True)
    pdf.cell(0, 6, f"Archivos procesados en lote: {num_archivos}", ln=True)
    
    pdf.ln(10)
    
    # --- Título de la tabla ---
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Resumen de Impacto", ln=True)
    pdf.ln(2)
    
    # --- Encabezados de la tabla ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(110, 10, "Metrica", border=1, fill=True)
    pdf.cell(50, 10, "Cantidad", border=1, fill=True, ln=True, align='C')
    
    # --- Filas de la tabla ---
    pdf.set_font("Helvetica", '', 11)
    
    total_eliminadas = stats['duplicados'] + stats['vacias'] + stats['basura']
    total_final = stats['originales'] - total_eliminadas
    
    datos = [
        ("Filas Originales Analizadas", str(stats['originales'])),
        ("Duplicados Eliminados", f"- {stats['duplicados']}"),
        ("Filas Vacias Eliminadas", f"- {stats['vacias']}"),
        ("Datos Filtrados (Palabra clave)", f"- {stats['basura']}"),
        ("TOTAL DE FILAS CONSERVADAS", str(total_final))
    ]
    
    for i, (metrica, valor) in enumerate(datos):
        # La última fila (el total limpio) la pintamos de verde clarito para que destaque
        if i == len(datos) - 1:
            pdf.set_font("Helvetica", 'B', 11)
            pdf.set_fill_color(220, 253, 230) 
            pdf.cell(110, 10, metrica, border=1, fill=True)
            pdf.cell(50, 10, valor, border=1, fill=True, ln=True, align='C')
        else:
            pdf.cell(110, 10, metrica, border=1)
            pdf.cell(50, 10, valor, border=1, ln=True, align='C')
            
    pdf.ln(20)
    
    # --- Pie de página ---
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Documento generado automaticamente por RowRescue (DesiLabs)", align='C')
    
    # Exportar a bytes
    return bytes(pdf.output())