import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

JSON_CONFIG = "canales_manuales.json"
XML_SALIDA = "epg_manual.xml"
TIMEZONE = ZoneInfo("Europe/Madrid")

def formatear_fecha_xmltv(dt):
    # Formato: 20260909060000 +0200
    return dt.strftime("%Y%m%d%H%M%S %z")

def main():
    if not os.path.exists(JSON_CONFIG):
        print(f"❌ Error: No se encontró '{JSON_CONFIG}'")
        return

    with open(JSON_CONFIG, "r", encoding="utf-8") as f:
        canales = json.load(f)

    ahora = datetime.now(TIMEZONE)
    # Si la hora actual es antes de las 06:00 am, el bloque de "hoy" arrancó ayer a las 06:00
    base_date = ahora.date()
    if ahora.hour < 6:
        base_date -= timedelta(days=1)

    root = ET.Element("tv", generator_info_name="EPG Manual Generator")

    # 1. Crear nodos <channel>
    for ch in canales:
        ch_elem = ET.SubElement(root, "channel", id=ch["id"])
        dn_elem = ET.SubElement(ch_elem, "display-name")
        dn_elem.text = ch.get("name", ch["id"])

    # 2. Crear bloques de 06:00 a 06:00 para Hoy (0), Mañana (1) y Pasado (2)
    for ch in canales:
        for offset_dias in range(3):
            dia_inicio = base_date + timedelta(days=offset_dias)
            dia_fin = dia_inicio + timedelta(days=1)

            dt_inicio = datetime(dia_inicio.year, dia_inicio.month, dia_inicio.day, 6, 0, 0, tzinfo=TIMEZONE)
            dt_fin = datetime(dia_fin.year, dia_fin.month, dia_fin.day, 6, 0, 0, tzinfo=TIMEZONE)

            prog = ET.SubElement(
                root,
                "programme",
                start=formatear_fecha_xmltv(dt_inicio),
                stop=formatear_fecha_xmltv(dt_fin),
                channel=ch["id"]
            )

            title = ET.SubElement(prog, "title")
            title.text = ch.get("title", "Emisión general")

            desc = ET.SubElement(prog, "desc")
            desc.text = ch.get("desc", "Sin descripción disponible.")

    ET.indent(root, space="  ", level=0)
    tree = ET.ElementTree(root)
    tree.write(XML_SALIDA, encoding="utf-8", xml_declaration=True)
    print(f"✔ '{XML_SALIDA}' generado con éxito para {len(canales)} canales (3 días cada uno).")

if __name__ == "__main__":
    main()
