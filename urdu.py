from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Create PDF object
pdf = FPDF()
pdf.add_page()

# Register the Urdu font (place NotoNastaliqUrdu-Regular.ttf in the same folder)
pdf.add_font(family="NotoNastaliq", fname="NotoNastaliqUrdu-Regular.ttf")

# Set default font (Nastaliq style looks beautiful for Urdu)
pdf.set_font("NotoNastaliq", size=14)

# ────────────────────────────────────────────────
# Page 1 - Title & Introduction
# ────────────────────────────────────────────────
pdf.cell(
    text="رامائن کا مختصر خلاصہ (اردو میں)",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C",
    w=190
)
pdf.ln(12)

pdf.multi_cell(
    w=190,
    h=10,
    text="رامائن والمیکی مہرشی کی تصنیف کردہ قدیم ہندوستانی مہاکاوی ہے۔ "
         "یہ سات کاندوں (حصوں) پر مشتمل ہے۔ رام دھرم کی علامت، سیتا پاکیزگی کی، "
         "اور ہنومان بھکتی اور طاقت کی نمائندگی کرتے ہیں۔ یہ کہانی دھرم، کرم، "
         "بھکتی اور خاندانی اقدار کی تعلیم دیتی ہے۔"
)

pdf.ln(10)

# Heading: larger size
pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="1. بال کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="ایودھیا میں دشرتھ مہاراج کے چار بیٹے پیدا ہوتے ہیں: رام (کوشلیا سے)، "
         "بھرت (کیکئی سے)، لکشمن اور شترگھن (سمیترا سے)۔ رام وشنو کے اوتار ہیں۔ "
         "وشوامتر رام اور لکشمن کو یگ کی حفاظت کے لیے لے جاتے ہیں۔ "
         "رام شیو دھنुष توڑ کر سیتا سے شادی کرتے ہیں۔"
)

pdf.ln(12)

# ────────────────────────────────────────────────
# Page 2 - Ayodhya & Aranya Kanda
# ────────────────────────────────────────────────
pdf.add_page()

pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="2. ایودھیا کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="دشرتھ رام کو یووراج بنانا چاہتے ہیں۔ کیکئی دو وعدے مانگتی ہے: "
         "بھرت کو راج اور رام کو چودہ سال کا ون واس۔ رام سیتا اور لکشمن کے ساتھ جنگل چلے جاتے ہیں۔ "
         "دشرتھ دکھ سے مر جاتے ہیں۔ بھرت رام کو واپس لانے کی کوشش کرتے ہیں مگر ناکام رہتے ہیں۔"
)

pdf.ln(8)

pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="3. ارنیا کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="ون واس کے دوران شورپنکھا رام سے محبت کا اظہار کرتی ہے۔ لکشمن اس کا ناک کاٹ دیتے ہیں۔ "
         "راون مایا مرگیج (سونے کی ہرن) بھیج کر سیتا کا ہرن کر لیتا ہے۔ "
         "جٹایو (پرندہ راج) راون سے لڑتا ہے اور مر جاتا ہے۔ رام اور لکشمن سیتا کی تلاش میں نکلتے ہیں۔"
)

# ────────────────────────────────────────────────
# Page 3 - Kishkindha, Sundara, Yuddha
# ────────────────────────────────────────────────
pdf.add_page()

pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="4. کشکندھا کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="رام سگریو (وانر راج) سے دوستی کرتے ہیں۔ والی کو مارتے ہیں۔ "
         "سگریو وانر فوج کے ساتھ سیتا کی تلاش میں مدد کرتا ہے۔ وانر مختلف سمتوں میں جاتے ہیں۔"
)

pdf.ln(8)

pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="5. سندر کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="ہنومان سمندر پار کر کے لنکا پہنچتے ہیں۔ "
         "سیتا کو اشوک ون میں دیکھتے ہیں، رام کا پیغام اور انگوٹھی دیتے ہیں۔ "
         "لنکا کو آگ لگا کر واپس آتے ہیں۔ وانر فوج خوش ہوتی ہے۔"
)

pdf.ln(8)

pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="6. یدھ کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="رام وانر فوج کے ساتھ سیتو (پل) بنوا کر لنکا پر حملہ کرتے ہیں۔ "
         "کمبھ کرن، اندرجیت اور راون مارے جاتے ہیں۔ سیتا آزاد ہوتی ہیں۔ "
         "اگنی پریکشا کے بعد ایودھیا واپس جاتے ہیں۔ رام کا راج تلک ہوتا ہے اور رام راجیہ قائم ہوتا ہے۔"
)

# ────────────────────────────────────────────────
# Page 4 - Uttara Kanda & Closing
# ────────────────────────────────────────────────
pdf.add_page()

pdf.set_font("NotoNastaliq", size=16)
pdf.cell(
    text="7. اتر کاند",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT
)
pdf.set_font("NotoNastaliq", size=14)

pdf.multi_cell(
    w=190,
    h=10,
    text="رام راجیہ کی تفصیل، لو اور کش کے جنم، سیتا کا تیاغ، "
         "رام کا آخری سفر (سریو ندی میں جل سمادھی)۔ "
         "(یہ کاند بعد میں شامل کیا گیا مانا جاتا ہے۔)"
)

pdf.ln(15)

pdf.multi_cell(
    w=190,
    h=10,
    text="رامائن دھرم، بھکتی، کرتویہ اور سچائی کی تعلیم دیتی ہے۔\n"
         "رام ہی دھرم کی زندہ شکل ہیں۔"
)

pdf.ln(12)

pdf.set_font("NotoNastaliq", size=18)
pdf.cell(
    text="جے شری رام!",
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
    align="C"
)

# Save the PDF
pdf.output("ramayanam_summary_urdu.pdf")
print("Created: ramayanam_summary_urdu.pdf")