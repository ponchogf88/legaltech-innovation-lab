#!/usr/bin/env python3
"""
AUDITOR LEGAL WEB: PRIVACIDAD Y TÉRMINOS & CONDICIONES
Desarrollado para: Gutiérrez Consulting / AI Law × Entre eclipse y condiciones
Motor: Antigravity Legal Tech (Python Standard Library - Zero External Dependencies)

Audita sitios web contra la Ley Federal de Protección de Datos Personales
en Posesión de los Particulares (LFPDPPP) y la Ley Federal de Protección al Consumidor (PROFECO).
"""

import sys
import os
import json
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from datetime import datetime

# Headers para simular navegador moderno
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8'
}

KEYWORDS_AVISO = [
    'aviso de privacidad', 'politica de privacidad', 'política de privacidad',
    'aviso legal', 'privacidad', 'privacy policy', 'privacy-policy', 'aviso-de-privacidad'
]

KEYWORDS_TERMINOS = [
    'terminos y condiciones', 'términos y condiciones', 'terminos de uso',
    'términos de uso', 'terminos del servicio', 'términos del servicio',
    'condiciones de uso', 'terms of service', 'terms-and-conditions', 'terms'
]

class LinkExtractor(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = [] # list of (href, text)
        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            if 'href' in attrs_dict:
                self.current_href = attrs_dict['href']
                self.current_text = []

    def handle_data(self, data):
        if self.current_href:
            self.current_text.append(data.strip())

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_href:
            text = ' '.join(self.current_text).strip()
            # Normalize URL
            full_url = urllib.parse.urljoin(self.base_url, self.current_href)
            self.links.append((full_url, text))
            self.current_href = None
            self.current_text = []

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.ignore_tags = {'script', 'style', 'head', 'noscript', 'svg'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_endtag(self, tag):
        self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self):
        return ' '.join(self.text_parts)

def fetch_url(url, timeout=12):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            encoding = response.headers.get_content_charset() or 'utf-8'
            html = response.read().decode(encoding, errors='replace')
            return True, html, response.geturl()
    except Exception as e:
        return False, str(e), url

def auditar_texto_privacidad(texto):
    texto_lower = texto.lower()
    hallazgos = []
    puntos_fuertes = []
    score_riesgo = 0 # 0 a 100

    # 1. BANDERAS ROJAS DE LEY EXTRANJERA (Machote copiado de Europa o EE.UU.)
    patrones_extranjeros = [
        (r'\brgpd\b', 'Cita el RGPD (Reglamento General de Protección de Datos de la Unión Europea)'),
        (r'\blopd\b|\blopdgdd\b', 'Cita la LOPD (Ley Orgánica de Protección de Datos de España)'),
        (r'agencia española de protección de datos|aepd', 'Menciona a la AEPD (Autoridad Española de Protección de Datos)'),
        (r'comisión europea|unión europea', 'Hace referencia a autoridades o directivas de la Unión Europea'),
        (r'\bccpa\b|california consumer privacy act', 'Cita legislación del estado de California (CCPA)'),
    ]
    for patron, desc in patrones_extranjeros:
        if re.search(patron, texto_lower):
            hallazgos.append({
                'tipo': 'CRÍTICO',
                'regla': 'Legislación Extranjera (Machote Copiado)',
                'detalle': desc,
                'fundamento': 'Invalidez procesal ante el INAI en México. Demuestra omisión de asesoría jurídica local.',
                'impacto_puntos': 35
            })
            score_riesgo += 35
            break

    # 2. PLACEHOLDERS SIN LLENAR
    patrones_placeholders = [
        (r'\[nombre de la empresa\]|\[insertar nombre\]|\[razón social\]', 'Texto de plantilla sin llenar: [Nombre de la empresa]'),
        (r'\[correo electrónico\]|\[insertar email\]|\[email@ejemplo\.com\]', 'Correo de contacto sin configurar'),
        (r'\[dirección\]|\[insertar domicilio\]|\[calle y número\]', 'Domicilio con texto de plantilla'),
        (r'lorem ipsum dolor sit amet', 'Texto de prueba Lorem Ipsum en aviso público'),
    ]
    for patron, desc in patrones_placeholders:
        if re.search(patron, texto_lower):
            hallazgos.append({
                'tipo': 'CRÍTICO',
                'regla': 'Texto de Plantilla Sin Rellenar',
                'detalle': desc,
                'fundamento': 'Infracción grave por falta de datos de identificación del Responsable.',
                'impacto_puntos': 30
            })
            score_riesgo += 30
            break

    # 3. IDENTIFICACIÓN DEL RESPONSABLE
    tiene_razon_social = bool(re.search(r's\.a\. de c\.v\.|s\. de r\.l\.|s\.a\.p\.i\.|sociedad anónima|persona física|responsable del tratamiento', texto_lower))
    tiene_rfc = bool(re.search(r'\brfc\b|[a-zñ&]{3,4}\d{6}[a-z0-9]{3}', texto_lower))
    if not (tiene_razon_social or tiene_rfc):
        hallazgos.append({
            'tipo': 'ALTO',
            'regla': 'Falta Identidad del Responsable',
            'detalle': 'No se especifica con claridad la persona física o moral responsable del tratamiento ni RFC.',
            'fundamento': 'Violación al Art. 16 Fracc. I de la LFPDPPP.',
            'impacto_puntos': 20
        })
        score_riesgo += 20
    else:
        puntos_fuertes.append('Identifica la denominación del responsable legal.')

    # 4. DOMICILIO FÍSICO
    tiene_domicilio = bool(re.search(r'domicilio|calle|colonia|c\.p\.|código postal|monterrey|nuevo león|san pedro|ciudad de méxico|méxico', texto_lower))
    if not tiene_domicilio:
        hallazgos.append({
            'tipo': 'ALTO',
            'regla': 'Falta Domicilio Legal del Responsable',
            'detalle': 'No contiene domicilio físico para oír y recibir notificaciones legales o inspecciones.',
            'fundamento': 'Violación al Art. 16 Fracc. I de la LFPDPPP.',
            'impacto_puntos': 20
        })
        score_riesgo += 20
    else:
        puntos_fuertes.append('Contempla domicilio o demarcación territorial.')

    # 5. DERECHOS ARCO
    tiene_arco = bool(re.search(r'derechos arco|acceso, rectificación|cancelación y oposición|rectificacion, cancelacion', texto_lower))
    tiene_procedimiento_dias = bool(re.search(r'20 días|veinte días|plazo de 20|plazo legal', texto_lower))
    if not tiene_arco:
        hallazgos.append({
            'tipo': 'CRÍTICO',
            'regla': 'Omisión Total de Derechos ARCO',
            'detalle': 'No menciona el derecho del titular a Acceder, Rectificar, Cancelar u Oponerse al uso de sus datos.',
            'fundamento': 'Violación directa a los Arts. 16 Fracc. IV, 28 y 29 de la LFPDPPP. Sanción directa por el INAI.',
            'impacto_puntos': 35
        })
        score_riesgo += 35
    elif not tiene_procedimiento_dias:
        hallazgos.append({
            'tipo': 'MEDIO',
            'regla': 'Procedimiento ARCO Incompleto',
            'detalle': 'Menciona los derechos ARCO pero no precisa el plazo legal de 20 días para respuesta.',
            'fundamento': 'Art. 32 LFPDPPP.',
            'impacto_puntos': 15
        })
        score_riesgo += 15
    else:
        puntos_fuertes.append('Estipula procedimiento y plazos de atención para Derechos ARCO.')

    # 6. FINALIDADES PRIMARIAS Y SECUNDARIAS
    tiene_secundarias = bool(re.search(r'finalidades secundarias|fines mercadotécnicos|publicidad|prospección comercial|finalidades no necesarias', texto_lower))
    if not tiene_secundarias:
        hallazgos.append({
            'tipo': 'MEDIO',
            'regla': 'Falta Desglose de Finalidades Secundarias',
            'detalle': 'No distingue entre datos necesarios para el servicio y datos usados para marketing/publicidad, ni ofrece mecanismo de negativa.',
            'fundamento': 'Art. 14 y 41 del Reglamento de la LFPDPPP.',
            'impacto_puntos': 15
        })
        score_riesgo += 15
    else:
        puntos_fuertes.append('Distingue finalidades primarias de fines mercadotécnicos.')

    # 7. TRANSFERENCIAS A TERCEROS
    tiene_transferencias = bool(re.search(r'transferencia de datos|transferir sus datos|terceros receptores|nacionales o internacionales', texto_lower))
    if not tiene_transferencias:
        hallazgos.append({
            'tipo': 'MEDIO',
            'regla': 'Cláusula de Transferencias Indefinida',
            'detalle': 'No aclara si los datos son compartidos con plataformas en la nube, pasarelas de pago o proveedores.',
            'fundamento': 'Art. 36 y 37 de la LFPDPPP.',
            'impacto_puntos': 10
        })
        score_riesgo += 10
    else:
        puntos_fuertes.append('Regula la transferencia de datos a terceros.')

    # 8. COOKIES Y RASTREADORES
    tiene_cookies = bool(re.search(r'cookies|web beacons|rastreadores|dirección ip', texto_lower))
    if not tiene_cookies:
        hallazgos.append({
            'tipo': 'BAJO',
            'regla': 'Sin Mención de Cookies / Tecnologías de Rastreo',
            'detalle': 'El sitio web no advierte el uso de cookies analíticas o de publicidad.',
            'fundamento': 'Lineamientos del INAI sobre tecnologías de rastreo web.',
            'impacto_puntos': 10
        })
        score_riesgo += 10
    else:
        puntos_fuertes.append('Declara el uso de cookies y herramientas de analítica web.')

    score_riesgo = min(100, score_riesgo)

    if score_riesgo >= 50:
        nivel = 'ALTO'
        color = 'ROJO'
        multa_estimada = '$540,000 – $3,200,000 MXN'
    elif score_riesgo >= 25:
        nivel = 'MEDIO'
        color = 'AMARILLO'
        multa_estimada = '$108,000 – $540,000 MXN'
    else:
        nivel = 'BAJO'
        color = 'VERDE'
        multa_estimada = 'Riesgo leve / Preventivo'

    return {
        'score_riesgo': score_riesgo,
        'nivel_riesgo': nivel,
        'color_semaforo': color,
        'multa_estimada_inai': multa_estimada,
        'hallazgos': hallazgos,
        'puntos_fuertes': puntos_fuertes
    }

def auditar_sitio_completo(url_objetivo):
    resultado = {
        'url_analizada': url_objetivo,
        'fecha_auditoria': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sitio_accesible': False,
        'tiene_link_aviso': False,
        'url_aviso': None,
        'tiene_link_terminos': False,
        'url_terminos': None,
        'analisis_privacidad': None,
        'resumen_ejecutivo': ''
    }

    print(f"\n[ANTIGRAVITY] Conectando con: {url_objetivo} ...")
    success, html_or_err, final_url = fetch_url(url_objetivo)
    if not success:
        resultado['error'] = f"No se pudo acceder a la página: {html_or_err}"
        return resultado

    resultado['sitio_accesible'] = True
    resultado['url_final'] = final_url

    # Extraer enlaces
    parser = LinkExtractor(final_url)
    try:
        parser.feed(html_or_err)
    except Exception:
        pass

    # Buscar links de aviso y términos
    for full_url, text in parser.links:
        t_low = text.lower()
        u_low = full_url.lower()

        if not resultado['tiene_link_aviso']:
            if any(k in t_low or k in u_low for k in KEYWORDS_AVISO):
                resultado['tiene_link_aviso'] = True
                resultado['url_aviso'] = full_url

        if not resultado['tiene_link_terminos']:
            if any(k in t_low or k in u_low for k in KEYWORDS_TERMINOS):
                resultado['tiene_link_terminos'] = True
                resultado['url_terminos'] = full_url

    # Si no tiene enlace a aviso
    if not resultado['tiene_link_aviso']:
        resultado['analisis_privacidad'] = {
            'score_riesgo': 100,
            'nivel_riesgo': 'CRÍTICO',
            'color_semaforo': 'ROJO',
            'multa_estimada_inai': '$1,085,000 – $4,300,000 MXN',
            'hallazgos': [{
                'tipo': 'CRÍTICO',
                'regla': 'Inexistencia Absoluta de Aviso de Privacidad',
                'detalle': 'El sitio web recolecta datos o tiene tráfico sin contar con enlace público a un Aviso de Privacidad.',
                'fundamento': 'Violación directa a los Arts. 15, 16 y 17 de la LFPDPPP.',
                'impacto_puntos': 100
            }],
            'puntos_fuertes': []
        }
        resultado['resumen_ejecutivo'] = "SITIO TOTALMENTE EXPUESTO: Carece de Aviso de Privacidad visible en el sitio."
        return resultado

    # Si tiene enlace, descargar y analizar
    print(f"[ANTIGRAVITY] Analizando texto de Aviso de Privacidad: {resultado['url_aviso']}")
    ok_aviso, html_aviso, url_aviso_final = fetch_url(resultado['url_aviso'])
    if not ok_aviso:
        resultado['analisis_privacidad'] = {
            'score_riesgo': 90,
            'nivel_riesgo': 'CRÍTICO',
            'color_semaforo': 'ROJO',
            'multa_estimada_inai': '$540,000 – $2,100,000 MXN',
            'hallazgos': [{
                'tipo': 'CRÍTICO',
                'regla': 'Enlace Roto a Política de Privacidad (Error 404 / Inaccesible)',
                'detalle': f'El botón de Aviso de Privacidad dirige a un enlace roto o con error: {html_aviso}',
                'fundamento': 'La ley exige disponibilidad permanente y accesible del documento.',
                'impacto_puntos': 90
            }],
            'puntos_fuertes': []
        }
        resultado['resumen_ejecutivo'] = "ENLACE ROTO: El sitio tiene el botón pero no muestra el aviso."
        return resultado

    # Extraer texto limpio
    text_parser = TextExtractor()
    try:
        text_parser.feed(html_aviso)
        texto_limpio = text_parser.get_text()
    except Exception:
        texto_limpio = html_aviso

    resultado['analisis_privacidad'] = auditar_texto_privacidad(texto_limpio)
    resultado['resumen_ejecutivo'] = f"Riesgo: {resultado['analisis_privacidad']['nivel_riesgo']} ({resultado['analisis_privacidad']['score_riesgo']}/100) - {len(resultado['analisis_privacidad']['hallazgos'])} inconsistencias legales detectadas."

    return resultado

def generar_reporte_html(r, output_path=None):
    p = r.get('analisis_privacidad') or {}
    domain = urllib.parse.urlparse(r['url_analizada']).netloc or 'sitio'
    if not output_path:
        output_path = f"04_MARKETING/auditorias/{domain}_auditoria.html"

    color_hex = '#EF4444' if p.get('color_semaforo') == 'ROJO' else ('#F59E0B' if p.get('color_semaforo') == 'AMARILLO' else '#10B981')
    badge_bg = '#FEE2E2' if p.get('color_semaforo') == 'ROJO' else ('#FEF3C7' if p.get('color_semaforo') == 'AMARILLO' else '#D1FAE5')

    hallazgos_html = ""
    for h in p.get('hallazgos', []):
        pill_color = '#DC2626' if h['tipo'] == 'CRÍTICO' else ('#D97706' if h['tipo'] == 'ALTO' else '#4B5563')
        hallazgos_html += f"""
        <div style="margin-bottom: 16px; padding: 14px 18px; background: #F8FAFC; border-left: 4px solid {pill_color}; border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <strong style="color: #0F172A; font-size: 15px;">{h['regla']}</strong>
                <span style="background: {pill_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{h['tipo']}</span>
            </div>
            <p style="margin: 0 0 6px 0; color: #334155; font-size: 13.5px; line-height: 1.5;">{h['detalle']}</p>
            <small style="color: #64748B; font-size: 12px; font-style: italic;">Fundamento legal: {h['fundamento']}</small>
        </div>
        """

    puntos_fuertes_html = "".join([f"<li style='margin-bottom: 4px; color: #166534;'>✓ {pf}</li>" for pf in p.get('puntos_fuertes', [])])
    if not puntos_fuertes_html:
        puntos_fuertes_html = "<li style='color: #64748B;'>No se identificaron elementos de cumplimiento robustos en el texto analizado.</li>"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dictamen Legal Digital — {domain}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #F1F5F9; color: #0F172A; margin: 0; padding: 30px; }}
        .page {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 25px; }}
        .brand-title {{ font-size: 18px; font-weight: 800; color: #0F172A; letter-spacing: 0.5px; }}
        .brand-sub {{ font-size: 13px; color: #64748B; font-weight: 500; }}
        .partner {{ text-align: right; font-size: 13px; color: #0284C7; font-weight: 700; }}
        .score-box {{ display: flex; gap: 20px; background: {badge_bg}; border: 1px solid {color_hex}; border-radius: 8px; padding: 18px 24px; margin-bottom: 25px; align-items: center; }}
        .score-num {{ font-size: 42px; font-weight: 900; color: {color_hex}; line-height: 1; }}
        .score-meta {{ flex: 1; }}
        .score-title {{ font-size: 17px; font-weight: 800; color: {color_hex}; margin: 0 0 4px 0; }}
        .score-desc {{ font-size: 13px; color: #334155; margin: 0; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 14px 18px; margin-bottom: 25px; font-size: 13px; }}
        .meta-item strong {{ color: #475569; }}
        .section-title {{ font-size: 16px; font-weight: 800; text-transform: uppercase; color: #1E293B; letter-spacing: 0.5px; margin: 25px 0 14px 0; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px; }}
        .cta-box {{ margin-top: 35px; background: #0F172A; color: white; padding: 22px; border-radius: 8px; text-align: center; }}
        .cta-btn {{ display: inline-block; margin-top: 10px; background: #38BDF8; color: #0F172A; font-weight: bold; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-size: 14px; }}
        @media print {{ body {{ background: white; padding: 0; }} .page {{ box-shadow: none; padding: 20px; }} .cta-box {{ background: #F8FAFC; color: black; border: 1px solid #CBD5E1; }} .cta-btn {{ border: 1px solid black; }} }}
    </style>
</head>
<body>
    <div class="page">
        <div class="header">
            <div>
                <div class="brand-title">GUTIÉRREZ CONSULTING · AI LAW</div>
                <div class="brand-sub">Litigio Corporativo, Ciberseguridad &amp; Compliance Digital</div>
            </div>
            <div class="partner">
                <span>EN ALIANZA CON</span><br>
                <span style="font-size: 15px; color: #8B5CF6;">Entre eclipse y condiciones</span>
            </div>
        </div>

        <h2 style="font-size: 20px; font-weight: 800; margin: 0 0 6px 0; color: #0F172A;">DICTAMEN TÉCNICO DE CUMPLIMIENTO DIGITAL</h2>
        <p style="color: #64748B; font-size: 13px; margin: 0 0 20px 0;">Auditoría automatizada de Aviso de Privacidad y Términos conforme a la LFPDPPP y PROFECO.</p>

        <div class="score-box">
            <div class="score-num">{p.get('score_riesgo', 0)}%</div>
            <div class="score-meta">
                <div class="score-title">NIVEL DE RIESGO: {p.get('nivel_riesgo', 'DESCONOCIDO')}</div>
                <div class="score-desc">Contingencia económica estimada ante inspección del INAI: <strong>{p.get('multa_estimada_inai', 'N/A')}</strong>.</div>
            </div>
        </div>

        <div class="meta-grid">
            <div class="meta-item"><strong>Dominio evaluado:</strong> {r['url_analizada']}</div>
            <div class="meta-item"><strong>Fecha de auditoría:</strong> {r['fecha_auditoria']}</div>
            <div class="meta-item"><strong>Aviso de Privacidad:</strong> {'Detectado y analizado' if r['tiene_link_aviso'] else '<span style="color:red;font-weight:bold;">No detectado</span>'}</div>
            <div class="meta-item"><strong>Términos y Condiciones:</strong> {'Detectado' if r['tiene_link_terminos'] else 'No detectado en inicio'}</div>
        </div>

        <div class="section-title">Hallazgos e Inconsistencias Normativas ({len(p.get('hallazgos', []))})</div>
        {hallazgos_html}

        <div class="section-title">Puntos de Cumplimiento Favorable</div>
        <ul style="margin: 0; padding-left: 20px; font-size: 13.5px;">
            {puntos_fuertes_html}
        </ul>

        <div class="cta-box">
            <h3 style="margin: 0 0 6px 0; font-size: 17px;">Programa de Regularización Exprés (48 Horas)</h3>
            <p style="margin: 0 0 10px 0; font-size: 13px; opacity: 0.9;">Blindamos su sitio web con Aviso de Privacidad y Términos a la medida, adaptados 100% a la ley mexicana y su modelo de negocio.</p>
            <div style="font-size: 12px; opacity: 0.8; margin-bottom: 8px;">Contacto directo: WhatsApp +52 81 4005 0088 · jesus.alfonso@gutierrezconsultores.net</div>
        </div>

        <div style="margin-top: 25px; padding-top: 15px; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-between; font-size: 11px; color: #94A3B8;">
            <div>Dictamen emitido por Lic. Jesús Alfonso Gutiérrez Flores (Céd. Prof. 11557818)</div>
            <div>Validación técnica: Motor Antigravity v2.6</div>
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[ANTIGRAVITY] Reporte visual HTML guardado con éxito en: {output_path}")
    return output_path

def imprimir_reporte_consola(r):
    p = r.get('analisis_privacidad')
    print("\n" + "="*70)
    print("  DICTAMEN DE AUDITORÍA LEGAL WEB — ANTIGRAVITY")
    print("  Gutiérrez Consulting × Entre eclipse y condiciones")
    print("="*70)
    print(f"URL Auditada:       {r['url_analizada']}")
    print(f"Fecha:              {r['fecha_auditoria']}")
    print(f"Aviso Encontrado:   {'SÍ' if r['tiene_link_aviso'] else 'NO'}")
    if r['tiene_link_aviso']:
        print(f"URL del Aviso:      {r['url_aviso']}")
    print(f"Términos y Cond.:   {'SÍ' if r['tiene_link_terminos'] else 'NO'}")
    if p:
        print(f"\n[SEMÁFORO DE RIESGO]:  {p['color_semaforo']} - NIVEL {p['nivel_riesgo']} (Score: {p['score_riesgo']}/100)")
        print(f"[SANCIÓN ESTIMADA]:    {p['multa_estimada_inai']}")
        print("\nHALLAZGOS CRÍTICOS Y OBSERVACIONES:")
        for i, h in enumerate(p['hallazgos'], 1):
            print(f"  {i}. [{h['tipo']}] {h['regla']}")
            print(f"     Detalle:    {h['detalle']}")
            print(f"     Normativa:  {h['fundamento']}")
        if p['puntos_fuertes']:
            print("\nPUNTOS FAVORABLES DETECTADOS:")
            for pf in p['puntos_fuertes']:
                print(f"  ✓ {pf}")
    print("="*70 + "\n")

if __name__ == '__main__':
    url_target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    res = auditar_sitio_completo(url_target)
    imprimir_reporte_consola(res)
    generar_reporte_html(res)
