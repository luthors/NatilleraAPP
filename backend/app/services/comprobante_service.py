"""
ComprobanteService — PDF receipt generation with embedded QR code.

Generates a professional PDF receipt for confirmed payments (ISSUE-25).
The PDF is saved to UPLOAD_DIR/comprobantes/ and the URL is stored on
the Pago record.

QR code encodes a verification URL:
  {APP_BASE_URL}/api/v1/verificar/{pago.recibo_referencia}

Dependencies:
  - reportlab (PDF generation)
  - qrcode[pil] (QR code image)
  - Pillow (image handling for QR in PDF)

References:
- ISSUE-25: PDF comprobante
- HU-05-02: receipt generation after payment confirmation
- RNF-09: receipts must be idempotent (same pago_id → same file)
"""
import io
import os
import logging
import secrets
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not installed — PDF generation disabled")

try:
    import qrcode
    from PIL import Image as PILImage
    QRCODE_AVAILABLE = True
except ImportError:  # pragma: no cover
    QRCODE_AVAILABLE = False
    logger.warning("qrcode/Pillow not installed — QR generation disabled")


class ComprobanteService:
    """
    Generates PDF payment receipts with embedded QR verification codes.

    Usage:
        svc = ComprobanteService(upload_dir, app_base_url, frontend_base_url)
        referencia, url = svc.generar(pago, socio, natillera, periodo)
    """

    def __init__(
        self,
        upload_dir: str,
        app_base_url: str,
        frontend_base_url: str,
    ) -> None:
        self.upload_dir = Path(upload_dir)
        self.app_base_url = app_base_url.rstrip("/")
        self.frontend_base_url = frontend_base_url.rstrip("/")
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        (self.upload_dir / "comprobantes").mkdir(parents=True, exist_ok=True)

    # ── Public ────────────────────────────────────────────────────────────────

    def generar(
        self,
        pago,
        socio,
        natillera,
        periodo,
    ) -> tuple[str, str]:
        """
        Generate a PDF receipt for a confirmed payment.

        Returns:
            (referencia, relative_url)  — both are safe to store on the Pago model.

        The method is idempotent: if pago.recibo_referencia is already set,
        the same values are returned without regenerating the file.
        """
        if pago.recibo_referencia:
            return pago.recibo_referencia, pago.recibo_url or ""

        referencia = self._nueva_referencia()
        filename = f"{referencia}.pdf"
        filepath = self.upload_dir / "comprobantes" / filename
        relative_url = f"/uploads/comprobantes/{filename}"
        verificacion_url = f"{self.app_base_url}/api/v1/verificar/{referencia}"

        if REPORTLAB_AVAILABLE:
            pdf_bytes = self._build_pdf(
                pago=pago,
                socio=socio,
                natillera=natillera,
                periodo=periodo,
                referencia=referencia,
                verificacion_url=verificacion_url,
            )
            filepath.write_bytes(pdf_bytes)
        else:
            # Fallback: plain-text receipt when reportlab is not installed
            text = self._build_text_receipt(
                pago=pago, socio=socio, natillera=natillera,
                periodo=periodo, referencia=referencia,
            )
            filepath.with_suffix(".txt").write_text(text, encoding="utf-8")
            relative_url = relative_url.replace(".pdf", ".txt")

        logger.info("[comprobante] Generated referencia=%s path=%s", referencia, filepath)
        return referencia, relative_url

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _nueva_referencia() -> str:
        """Generate a unique receipt reference (e.g. REC-A3F9C2B1)."""
        return f"REC-{secrets.token_hex(4).upper()}"

    def _build_qr_image(self, url: str, size_cm: float = 3.5):
        """Return a ReportLab Image object of the QR code."""
        if not QRCODE_AVAILABLE:
            return None
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        size = size_cm * cm
        return RLImage(buf, width=size, height=size)

    def _build_pdf(
        self,
        pago,
        socio,
        natillera,
        periodo,
        referencia: str,
        verificacion_url: str,
    ) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "titulo",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#4f46e5"),
            alignment=TA_CENTER,
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "subtitulo",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        label_style = ParagraphStyle(
            "label",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
        )
        value_style = ParagraphStyle(
            "value",
            parent=styles["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
        )
        ref_style = ParagraphStyle(
            "ref",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )

        story = []

        # Header
        story.append(Paragraph("🏦 Natillera App", title_style))
        story.append(Paragraph("Comprobante de Pago", subtitle_style))
        story.append(Spacer(1, 0.3 * cm))

        # Divider table
        story.append(Table(
            [[""]],
            colWidths=[17 * cm],
            style=TableStyle([
                ("LINEABOVE", (0, 0), (-1, 0), 1.5, colors.HexColor("#4f46e5")),
            ]),
        ))
        story.append(Spacer(1, 0.5 * cm))

        # Data table
        nombre_socio = getattr(getattr(socio, "usuario", None), "nombre", str(socio.usuario_id))
        data = [
            [Paragraph("REFERENCIA", label_style), Paragraph(referencia, value_style)],
            [Paragraph("FECHA", label_style),
             Paragraph(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"), value_style)],
            [Paragraph("NATILLERA", label_style), Paragraph(natillera.nombre, value_style)],
            [Paragraph("PERÍODO", label_style), Paragraph(periodo.nombre, value_style)],
            [Paragraph("SOCIO", label_style), Paragraph(nombre_socio, value_style)],
            [Paragraph("MONTO", label_style),
             Paragraph(f"$ {pago.monto:,.2f}", ParagraphStyle(
                 "monto", parent=value_style, fontSize=14,
                 textColor=colors.HexColor("#16a34a")
             ))],
            [Paragraph("MÉTODO", label_style), Paragraph(pago.metodo.value, value_style)],
            [Paragraph("ESTADO", label_style),
             Paragraph(
                 pago.estado.value,
                 ParagraphStyle("estado", parent=value_style,
                                textColor=colors.HexColor("#16a34a"))
             )],
        ]
        if pago.referencia:
            data.append([
                Paragraph("REF. TRANSFERENCIA", label_style),
                Paragraph(pago.referencia, value_style),
            ])

        tbl = Table(data, colWidths=[5 * cm, 12 * cm])
        tbl.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.8 * cm))

        # QR code section
        qr_img = self._build_qr_image(verificacion_url)
        if qr_img:
            qr_label = Paragraph(
                "Escanea el código QR para verificar la autenticidad de este comprobante",
                ref_style,
            )
            qr_tbl = Table(
                [[qr_img], [qr_label]],
                colWidths=[17 * cm],
            )
            qr_tbl.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(qr_tbl)
            story.append(Spacer(1, 0.3 * cm))

        # Footer
        story.append(Paragraph(
            f"URL de verificación: {verificacion_url}",
            ParagraphStyle("url", parent=styles["Normal"], fontSize=8,
                           textColor=colors.grey, alignment=TA_CENTER),
        ))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            "Este documento es un comprobante oficial generado por Natillera App. "
            "Guárdalo para tus registros.",
            ParagraphStyle("footer", parent=styles["Normal"], fontSize=8,
                           textColor=colors.grey, alignment=TA_CENTER),
        ))

        doc.build(story)
        return buf.getvalue()

    def _build_text_receipt(
        self, pago, socio, natillera, periodo, referencia: str
    ) -> str:
        """Plain-text fallback receipt when reportlab is unavailable."""
        nombre_socio = getattr(getattr(socio, "usuario", None), "nombre", str(socio.usuario_id))
        lines = [
            "=" * 50,
            "  NATILLERA APP — COMPROBANTE DE PAGO",
            "=" * 50,
            f"  Referencia : {referencia}",
            f"  Fecha      : {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}",
            f"  Natillera  : {natillera.nombre}",
            f"  Período    : {periodo.nombre}",
            f"  Socio      : {nombre_socio}",
            f"  Monto      : $ {pago.monto:,.2f}",
            f"  Método     : {pago.metodo.value}",
            f"  Estado     : {pago.estado.value}",
            "=" * 50,
        ]
        return "\n".join(lines)
