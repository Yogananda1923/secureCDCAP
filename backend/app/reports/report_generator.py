import os
import json
from datetime import datetime
from typing import Dict, Any
from app.config import settings

class ReportGenerator:
    """
    Generates academic and enterprise security compliance audit reports
    in JSON, HTML, and PDF formats.
    """

    @classmethod
    def generate_json_report(cls, data: Dict[str, Any]) -> str:
        report_data = {
            "title": "SecureCompilerAI Security & Compiler Analysis Report",
            "generated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "file_name": data.get("file_name", "source_code"),
                "language": data.get("language", "python"),
                "total_lines": data.get("total_lines", 0),
                "total_tokens": data.get("total_tokens", 0),
                "security_score": data.get("security_score", 100.0),
                "ast_nodes": data.get("ast_nodes_count", 0)
            },
            "vulnerabilities": data.get("vulnerabilities", []),
            "transformations": data.get("transformations", []),
            "verification": data.get("verification", {}),
            "disclaimer": data.get("limitations_disclaimer", "")
        }
        return json.dumps(report_data, indent=2)

    @classmethod
    def generate_html_report(cls, data: Dict[str, Any]) -> str:
        file_name = data.get("file_name", "source_code")
        language = data.get("language", "python")
        score = data.get("security_score", 100.0)
        lines = data.get("total_lines", 0)
        tokens = data.get("total_tokens", 0)
        ast_nodes = data.get("ast_nodes_count", 0)
        vulns = data.get("vulnerabilities", [])
        transformations = data.get("transformations", [])
        verification = data.get("verification", {})

        score_color = "#22c55e" if score >= 80 else ("#f59e0b" if score >= 50 else "#ef4444")

        vuln_rows = ""
        for v in vulns:
            sev = v.get("severity", "Medium")
            s_color = "#ef4444" if sev == "Critical" else ("#f97316" if sev == "High" else "#f59e0b")
            vuln_rows += f"""
            <tr style="border-bottom: 1px solid #1f2937;">
                <td style="padding: 12px; font-weight: bold; color: {s_color};">{sev}</td>
                <td style="padding: 12px;">{v.get('cwe_id', 'CWE')}</td>
                <td style="padding: 12px; font-weight: 500;">{v.get('name', '')}</td>
                <td style="padding: 12px;">Line {v.get('line_number', 1)}</td>
                <td style="padding: 12px; font-family: monospace; font-size: 13px; color: #93c5fd;">{v.get('vulnerable_snippet', '')}</td>
                <td style="padding: 12px; font-size: 13px;">{v.get('root_cause', '')}</td>
            </tr>
            """

        if not vuln_rows:
            vuln_rows = '<tr><td colspan="6" style="padding: 16px; text-align: center; color: #22c55e;">No vulnerabilities detected. Clean security profile.</td></tr>'

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureCompilerAI Audit Report - {file_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0b1020;
            color: #e5e7eb;
            margin: 0;
            padding: 30px;
        }}
        .header {{
            border-bottom: 2px solid #1f2937;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .title {{
            font-size: 26px;
            font-weight: 800;
            color: #6366f1;
            margin: 0;
        }}
        .subtitle {{
            color: #9ca3af;
            font-size: 14px;
            margin-top: 5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #172033;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 20px;
        }}
        .metric-title {{
            font-size: 13px;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .metric-val {{
            font-size: 30px;
            font-weight: 800;
            margin-top: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #172033;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 30px;
        }}
        th {{
            background: #111827;
            padding: 14px 12px;
            text-align: left;
            font-size: 13px;
            color: #9ca3af;
            text-transform: uppercase;
        }}
        .disclaimer {{
            background: #111827;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            font-size: 13px;
            color: #9ca3af;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 class="title">SecureCompilerAI</h1>
            <div class="subtitle">Semantic Compiler & Security Verification Audit Report</div>
        </div>
        <div style="text-align: right; font-size: 13px; color: #9ca3af;">
            <div>Target: <strong>{file_name}</strong> ({language.upper()})</div>
            <div>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
        </div>
    </div>

    <div class="stats-grid">
        <div class="card">
            <div class="metric-title">Security Score</div>
            <div class="metric-val" style="color: {score_color};">{score} / 100</div>
        </div>
        <div class="card">
            <div class="metric-title">Total Vulnerabilities</div>
            <div class="metric-val" style="color: {'#ef4444' if len(vulns) > 0 else '#22c55e'};">{len(vulns)}</div>
        </div>
        <div class="card">
            <div class="metric-title">Source Lines / Tokens</div>
            <div class="metric-val" style="color: #6366f1;">{lines} / {tokens}</div>
        </div>
        <div class="card">
            <div class="metric-title">AST Node Count</div>
            <div class="metric-val" style="color: #a855f7;">{ast_nodes}</div>
        </div>
    </div>

    <h2>Identified Security Vulnerabilities</h2>
    <table>
        <thead>
            <tr>
                <th>Severity</th>
                <th>CWE</th>
                <th>Vulnerability</th>
                <th>Location</th>
                <th>Code Snippet</th>
                <th>Root Cause</th>
            </tr>
        </thead>
        <tbody>
            {vuln_rows}
        </tbody>
    </table>

    <div class="disclaimer">
        <strong>Academic & Compliance Disclaimer:</strong> This report is automatically generated by SecureCompilerAI static AST and semantic verification pipelines. Static analysis heuristics detect known syntactic and data-flow flaw patterns but do not represent mathematical proof of absence of flaws in dynamic production environments.
    </div>
</body>
</html>"""
        return html_content

    @classmethod
    def generate_pdf_report(cls, data: Dict[str, Any], output_path: str):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#6366F1')
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#6B7280')
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1F2937')
        )

        elements = []

        elements.append(Paragraph("SecureCompilerAI Security & Compiler Report", title_style))
        elements.append(Paragraph(f"File: {data.get('file_name', 'source')} | Language: {data.get('language', 'python').upper()} | Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style))
        elements.append(Spacer(1, 15))

        # Metrics Table
        metrics_data = [
            ["Security Score", "Total Vulnerabilities", "Total Lines", "Tokens", "AST Nodes"],
            [
                f"{data.get('security_score', 100.0)} / 100",
                str(len(data.get("vulnerabilities", []))),
                str(data.get("total_lines", 0)),
                str(data.get("total_tokens", 0)),
                str(data.get("ast_nodes_count", 0))
            ]
        ]
        t = Table(metrics_data, colWidths=[100, 110, 80, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F3F4F6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # Vulnerabilities
        elements.append(Paragraph("<b>Security Vulnerabilities Detected:</b>", styles['Heading3']))
        elements.append(Spacer(1, 8))

        vulns = data.get("vulnerabilities", [])
        if vulns:
            table_data = [["Severity", "CWE", "Name", "Line", "Snippet"]]
            for v in vulns:
                table_data.append([
                    v.get("severity", ""),
                    v.get("cwe_id", ""),
                    Paragraph(v.get("name", "")[:40], body_style),
                    str(v.get("line_number", 1)),
                    Paragraph(v.get("vulnerable_snippet", "")[:45], body_style)
                ])
            vt = Table(table_data, colWidths=[65, 60, 155, 40, 190])
            vt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(vt)
        else:
            elements.append(Paragraph("No vulnerabilities detected. Clean security profile.", body_style))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Verified Transformations & Compiler Optimizations:</b>", styles['Heading3']))
        elements.append(Spacer(1, 6))

        fixes = data.get("transformations", [])
        if fixes:
            for fix in fixes:
                elements.append(Paragraph(f"• {fix}", body_style))
        else:
            elements.append(Paragraph("No automated transformations applied.", body_style))

        doc.build(elements)

