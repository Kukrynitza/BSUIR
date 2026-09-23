from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent
FONT = Path(r"C:\Windows\Fonts\times.ttf")
FONT_B = Path(r"C:\Windows\Fonts\timesbd.ttf")

pdfmetrics.registerFont(TTFont("TimesR", str(FONT)))
if FONT_B.exists():
    pdfmetrics.registerFont(TTFont("TimesB", str(FONT_B)))
    title_font = "TimesB"
else:
    title_font = "TimesR"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleR",
            fontName=title_font,
            fontSize=16,
            leading=20,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyR",
            fontName="TimesR",
            fontSize=12,
            leading=16,
            spaceAfter=8,
            firstLineIndent=12,
        )
    )
    return styles


DOCS = [
    (
        "ru_priem.pdf",
        "Приём пациента в терапевтическое отделение",
        [
            "Пациент поступил в городскую больницу с жалобами на высокую температуру, кашель и боль в грудной клетке. При осмотре врач отметил ослабленное дыхание в нижних отделах правого лёгкого и назначил рентгенографию.",
            "Лабораторные анализы крови показали лейкоцитоз и повышение C-реактивного белка. Диагноз: внебольничная пневмония. Назначены антибиотики, муколитики и контроль температуры каждые четыре часа.",
            "Медсестра разместила пациента в отдельной палате, провела ингаляцию с физиологическим раствором и оформила медицинскую карту в электронном виде. Планируется повторный осмотр на следующие сутки.",
        ],
    ),
    (
        "de_aufnahme.pdf",
        "Aufnahme eines Patienten in die internistische Abteilung",
        [
            "Der Patient wurde in das städtische Krankenhaus aufgenommen mit Fieber, Husten und Schmerzen in der Brust. Bei der Untersuchung stellte der Arzt ein abgeschwächtes Atemgeräusch im rechten Unterlappen fest und verordnete eine Röntgenaufnahme.",
            "Die Blutanalysen zeigten eine Leukozytose und ein erhöhtes C-reaktives Protein. Diagnose: ambulant erworbene Pneumonie. Es wurden Antibiotika, Mukolytika und eine Temperaturkontrolle alle vier Stunden angeordnet.",
            "Die Krankenschwester brachte den Patienten in einem Einzelzimmer unter, führte eine Inhalation mit physiologischer Lösung durch und aktualisierte die elektronische Krankenakte. Eine Kontrolluntersuchung ist für den nächsten Tag geplant.",
        ],
    ),
    (
        "ru_operaciya.pdf",
        "Подготовка к лапароскопической операции",
        [
            "Хирургическое отделение готовит пациента к лапароскопической операции по поводу острого аппендицита. Проведены консультация анестезиолога, анализ свёртываемости крови и ультразвуковое исследование брюшной полости.",
            "Перед вмешательством назначена антибиотикопрофилактика. Операционная оснащена эндоскопической стойкой и системой мониторинга жизненных показателей. После операции пациент будет наблюдаться в палате пробуждения.",
            "Родственникам разъяснён план лечения и возможные осложнения. Выписка ожидается на третий день при отсутствии признаков инфекции и нормальной температуре тела.",
        ],
    ),
    (
        "de_operation.pdf",
        "Vorbereitung auf eine laparoskopische Operation",
        [
            "Die chirurgische Abteilung bereitet den Patienten auf eine laparoskopische Operation bei akuter Appendizitis vor. Es erfolgten die Beratung durch den Anästhesisten, Gerinnungsanalysen und eine Ultraschalluntersuchung des Bauchraums.",
            "Vor dem Eingriff wurde eine Antibiotikaprophylaxe verordnet. Der Operationssaal ist mit einer endoskopischen Einheit und einem Überwachungssystem ausgestattet. Nach der Operation bleibt der Patient im Aufwachraum.",
            "Den Angehörigen wurden der Behandlungsplan und mögliche Komplikationen erläutert. Die Entlassung ist für den dritten Tag geplant, sofern keine Infektionszeichen und kein Fieber vorliegen.",
        ],
    ),
]


def write_pdf(name: str, title: str, paragraphs: list[str]) -> None:
    styles = build_styles()
    path = ROOT / name
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    story = [Paragraph(title, styles["TitleR"]), Spacer(1, 6)]
    for text in paragraphs:
        story.append(Paragraph(text, styles["BodyR"]))
    doc.build(story)
    print(path, path.stat().st_size)


if __name__ == "__main__":
    for item in DOCS:
        write_pdf(*item)
