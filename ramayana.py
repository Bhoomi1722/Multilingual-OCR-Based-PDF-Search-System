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
# Page 1 - Title & Introduction
# ────────────────────────────────────────────────
pdf.cell(
    text="శ్రీ రామాయణం - సంక్షిప్త సారాంశం (తెలుగు)",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C",
    w=190
)
pdf.ln(12)

pdf.multi_cell(
    w=190,
    h=10,
    text="రామాయణం వాల్మీకి మహర్షి రచించిన ఆదికావ్యం. "
         "ఇది ఏడు కాండలుగా విభజించబడింది. "
         "రాముడు ధర్మస్వరూపుడు, సీత పవిత్రత్వం, హనుమంతుడు భక్తి ప్రతీకలు."
)

pdf.ln(10)

# Heading style: larger size instead of bold
pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="1. బాలకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="అయోధ్యలో దశరథ మహారాజుకు నాలుగు కుమారులు జన్మిస్తారు: "
         "రాముడు (కౌసల్య), భరతుడు (కైకేయి), లక్ష్మణుడు & శత్రుఘ్నుడు (సుమిత్ర). "
         "విశ్వామిత్రుడు రామలక్ష్మణులను తీసుకొని యజ్ఞ రక్షణ చేస్తారు. "
         "రాముడు శివధనుస్సును తెంచి సీతను వివాహం చేసుకుంటాడు. "
         "పరశురాముడితో సంఘర్షణ తర్వాత రాముడి మహిమ తెలుస్తుంది."
)

pdf.ln(12)

# ────────────────────────────────────────────────
# Page 2 - Ayodhya & Aranya Kanda
# ────────────────────────────────────────────────
pdf.add_page()

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="2. అయోధ్యాకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="దశరథుడు రాముణ్ణి యువరాజుగా పట్టాభిషేకం చేయాలనుకుంటాడు. "
         "కైకేయి రెండు వరాలు అడుగుతుంది: భరతుడికి రాజ్యం, "
         "రాముడికి 14 సంవత్సరాల వనవాసం. "
         "రాముడు సీత, లక్ష్మణులతో అడవికి బయలుదేరతాడు. "
         "దశరథుడు దుఃఖంతో మరణిస్తాడు. "
         "భరతుడు రాముణ్ణి తిరిగి తీసుకురావాలని ప్రయత్నిస్తాడు కానీ విఫలమవుతాడు."
)

pdf.ln(8)

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="3. అరణ్యకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="వనవాసంలో శూర్పణఖ రాముణ్ణి కోరుతుంది. లక్ష్మణుడు ఆమె ముక్కు తెగిస్తాడు. "
         "రావణుడు మాయామృగం (బంగారు జింక) పంపి సీతను అపహరిస్తాడు. "
         "జటాయువు రావణునితో పోరాడి మరణిస్తాడు. "
         "రామలక్ష్మణులు సీతను వెతుకుతూ ముందుకు సాగుతారు."
)

# ────────────────────────────────────────────────
# Page 3 - Kishkindha, Sundara, Yuddha
# ────────────────────────────────────────────────
pdf.add_page()

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="4. కిష్కింధాకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="రాముడు సుగ్రీవుని స్నేహితుడవుతాడు. వాలిని సంహరిస్తాడు. "
         "సుగ్రీవుడు వానర సైన్యంతో సీతను వెతకడానికి సహాయం చేస్తాడు. "
         "వానరులు దిశలా వెతుకుతారు."
)

pdf.ln(8)

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="5. సుందరకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="హనుమంతుడు సముద్రం దాటి లంకకు వెళ్తాడు. "
         "సీతను అశోకవనంలో చూసి రాముని సందేశం, ఉంగరం ఇస్తాడు. "
         "లంకను దహనం చేసి తిరిగి వస్తాడు. "
         "వానర సైన్యానికి ఆనందం కలుగుతుంది."
)

pdf.ln(8)

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="6. యుద్ధకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="రాముడు వానర సైన్యంతో సేతువు కట్టి లంక మీద దాడి చేస్తాడు. "
         "కుంభకర్ణుడు, ఇంద్రజిత్తు, రావణుడు మృతి చెందుతారు. "
         "సీత విముక్తి అవుతుంది. అగ్ని పరీక్ష తర్వాత అయోధ్యకు తిరిగి వస్తారు. "
         "రాముడు పట్టాభిషేకం అవుతాడు. రామరాజ్యం స్థాపన."
)

# ────────────────────────────────────────────────
# Page 4 - Uttara Kanda & Closing
# ────────────────────────────────────────────────
pdf.add_page()

pdf.set_font("NotoTelugu", size=16)
pdf.cell(
    text="7. ఉత్తరకాండం",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoTelugu", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="రామరాజ్య వివరణ, లవ-కుశుల జననం, సీతా పరిత్యాగం, "
         "రాముని అంతిమ గమనం (సరయూ నదిలో జలసమాధి). "
         "(ఈ కాండం తరువాత జోడించబడినదని కొందరి అభిప్రాయం.)"
)

pdf.ln(15)

pdf.multi_cell(
    w=190,
    h=10,
    text="రామాయణం ధర్మం, భక్తి, కర్తవ్యం, సత్యం బోధిస్తుంది.\n"
         "'రామో విగ్రహవాన్ ధర్మః' – రాముడే ధర్మ స్వరూపుడు."
)

pdf.ln(12)

pdf.set_font("NotoTelugu", size=18)
pdf.cell(
    text="జయ శ్రీరామ్ !",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C"
)

# Save the PDF
pdf.output("ramayanam_summary_telugu_fixed.pdf")
print("Created: ramayanam_summary_telugu_fixed.pdf")