from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Create PDF object
pdf = FPDF()
pdf.add_page()

# Register the font (place NotoSansTelugu-Regular.ttf in the same folder)
pdf.add_font(family="NotoTelugu", fname="NotoSansTelugu-Regular.ttf")

# Set default font
pdf.set_font("NotoTelugu", size=14)

# ────────────────────────────────────────────────
# Title Page
# ────────────────────────────────────────────────
pdf.set_font("NotoTelugu", size=24)
pdf.cell(
    text="శ్రీ మహాభారతం – సంక్షిప్త వివరణాత్మక సారాంశం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C",
    w=190
)
pdf.ln(10)

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="వ్యాస మహర్షి రచిత ఇతిహాసం • ధర్మ యుద్ధ గాథ",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C",
    w=190
)
pdf.ln(20)

pdf.set_font("NotoTelugu", size=12)
pdf.multi_cell(
    w=190,
    h=8,
    text="మహాభారతం ధర్మం, అధర్మం, కర్తవ్యం, భక్తి, రాజనీతి, యుద్ధ తత్వాలను బోధించే మహా గ్రంథం.\n"
         "కురు వంశంలో పాండవ-కౌరవుల మధ్య జరిగిన మహా యుద్ధం చుట్టూ ఈ కథ నడుస్తుంది.\n"
         "భగవద్గీత ఈ ఇతిహాసంలోని అత్యంత ముఖ్య భాగం."
)
pdf.add_page()

# ────────────────────────────────────────────────
# Function to add section title and content
# ────────────────────────────────────────────────
def add_parva_title(parva_num, title):
    pdf.set_font("NotoTelugu", size=18)
    pdf.cell(
        text=f"{parva_num}. {title}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )
    pdf.ln(8)
    pdf.set_font("NotoTelugu", size=14)

def add_content(text):
    pdf.multi_cell(w=190, h=9, text=text)
    pdf.ln(6)

# 1. ఆది పర్వం
add_parva_title(1, "ఆది పర్వం")
add_content(
    "కురు వంశ చరిత్ర, భీష్ముని ప్రతిజ్ఞ, శంతను-గంగ వివాహం, చిత్రాంగద-విచిత్రవీర్యుల జననం.\n"
    "పాండు-ధృతరాష్ట్ర-విదురుల జననం. ద్రౌపది స్వయంవరం, పాండవుల వివాహం.\n"
    "ఇంద్రప్రస్థ నగర నిర్మాణం, మాయా సభ."
)

# 2. సభా పర్వం
add_parva_title(2, "సభా పర్వం")
add_content(
    "రాజసూయ యాగం, శిశుపాల వధ.\n"
    "ద్యూత క్రీడలో పాండవుల ఓటమి, ద్రౌపది చీర హరణం, వనవాస శిక్ష (12+1 సంవత్సరాలు)."
)

# 3. అరణ్య (వన) పర్వం
add_parva_title(3, "అరణ్య పర్వం")
add_content(
    "వనవాస కాలంలో పాండవుల జీవితం, అర్జునుని దివ్యాస్త్రాల సేకరణ (ఇంద్రకీలాద్రి).\n"
    "ద్రౌపది-జయద్రథ సంఘటన, యక్ష ప్రశ్నలు (ధర్మ బోధలు)."
)

# 4. విరాట పర్వం
add_parva_title(4, "విరాట పర్వం")
add_content(
    "అజ్ఞాత వాసం – పాండవులు విరాట రాజు ఆస్థానంలో దాక్కోవడం.\n"
    "కీచక వధ (భీముడు), గోహరణ యుద్ధం, అర్జునుడు బృహన్నళ రూపంలో వీరత్వం చాటడం."
)

# 5. ఉద్యోగ పర్వం
add_parva_title(5, "ఉద్యోగ పర్వం")
add_content(
    "యుద్ధ సన్నాహాలు, శాంతి దూతలు (కృష్ణుడు), దుర్యోధనుని తిరస్కారం.\n"
    "కృష్ణ-కర్ణ సంవాదం, ఉపప్లవ్యంలో పాండవ సైన్య సమావేశం."
)

# 6. భీష్మ పర్వం
add_parva_title(6, "భీష్మ పర్వం")
add_content(
    "కురుక్షేత్ర యుద్ధం ప్రారంభం.\n"
    "భీష్ముడు సేనాధిపతి. **భగవద్గీత** (అర్జునుని సందేహ నివారణ, కర్మ యోగం, భక్తి యోగం బోధ).\n"
    "భీష్ముని పతనం (శరశయ్యపై ఏకాదశి వరకు)."
)

# 7. ద్రోణ పర్వం
add_parva_title(7, "ద్రోణ పర్వం")
add_content(
    "ద్రోణాచార్యుడు సేనాధిపతి.\n"
    "అభిమన్యు చక్రవ్యూహంలో వీరమరణం.\n"
    "ద్రోణుని మరణం (అశ్వత్థామ గురించి అబద్ధం చెప్పి)."
)

# 8. కర్ణ పర్వం
add_parva_title(8, "కర్ణ పర్వం")
add_content(
    "కర్ణుడు సేనాధిపతి.\n"
    "కర్ణ-అర్జున యుద్ధం, కర్ణుని మరణం (చక్రం కిందికి పోవడం, శపం ప్రభావం)."
)

# 9. శల్య పర్వం
add_parva_title(9, "శల్య పర్వం")
add_content(
    "శల్యుడు సేనాధిపతి.\n"
    "దుర్యోధనుడు గదాయుద్ధంలో భీమునిచే మరణిస్తాడు.\n"
    "యుద్ధం ముగింపు."
)

# 10–15. (సంక్షిప్తంగా)
pdf.add_page()
add_parva_title(10, "సౌప్తిక పర్వం")
add_content("అశ్వత్థామ రాత్రి దాడి, పాండవ పుత్రుల వధ.")

add_parva_title(11, "స్త్రీ పర్వం")
add_content("యుద్ధ తర్వాత శోకం, గాంధారి శాపం.")

add_parva_title(12, "శాంతి పర్వం")
add_content("రాజధర్మం, భీష్ముని బోధలు (ధర్మ రహస్యాలు).")

add_parva_title(13, "అనుశాసన పర్వం")
add_content("భీష్ముని చివరి బోధలు, దాన ధర్మాలు.")

add_parva_title(14, "ఆశ్వమేధిక పర్వం")
add_content("యుధిష్ఠిరుని అశ్వమేధ యాగం, అర్జునుని దిగ్విజయం.")

add_parva_title(15, "ఆశ్రమ వాసిక పర్వం")
add_content("ధృతరాష్ట్రాదుల అరణ్య గమనం, వనవాసం.")

# 16–18
add_parva_title(16, "మౌసల పర్వం")
add_content("యాదవుల మధ్య కలహం, శ్రీకృష్ణుని లీలా సమాప్తి.")

add_parva_title(17, "మహాప్రస్థానిక పర్వం")
add_content("పాండవుల హిమాలయ ప్రయాణం, స్వర్గారోహణం.")

add_parva_title(18, "స్వర్గారోహణ పర్వం")
add_content("యుధిష్ఠిరుని స్వర్గ ప్రవేశం, ధర్మ రాజుతో సంవాదం, అంతిమ బోధలు.")

# ────────────────────────────────────────────────
# Closing
# ────────────────────────────────────────────────
pdf.add_page()
pdf.set_font("NotoTelugu", size=20)
pdf.cell(
    text="ధర్మో రక్షతి రక్షితః\nజయ శ్రీకృష్ణుడు !",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C",
    w=190
)
pdf.ln(20)

pdf.set_font("NotoTelugu", size=12)
pdf.multi_cell(
    w=190,
    h=8,
    text="మహాభారతం కేవలం యుద్ధ కథ కాదు — అది జీవిత దర్శనం, ధర్మ సందేశం.\n"
         "భగవద్గీత ద్వారా శ్రీకృష్ణుడు మానవాళికి అందించిన అమర జ్ఞానం."
)

# Save the PDF
pdf.output("mahabharatam_sankshepta_sarasam_telugu.pdf")
print("Created: mahabharatam_sankshepta_sarasam_telugu.pdf")