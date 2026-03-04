import pdfkit

config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

html = """
<!DOCTYPE html>
<html dir="rtl" lang="ur">
<head>
<meta charset="UTF-8">
<style>
    body { font-family: serif; direction: rtl; text-align: right; font-size: 20px; }
</style>
</head>
<body>
    <h1>ٹیسٹ اردو متن</h1>
    <p>یہ ایک مکمل پیراگراف ہے جو اردو زبان میں لکھا گیا ہے۔
اس پیراگراف کا مقصد پی ڈی ایف رینڈرنگ، فونٹ ایمبیڈنگ،
اور رائٹ ٹو لیفٹ ٹیکسٹ فلو کی جانچ کرنا ہے۔
اردو ایک خوبصورت زبان ہے جو دائیں سے بائیں لکھی جاتی ہے۔
اس میں حروف کی جوڑ توڑ اور لیگچر رینڈرنگ نہایت اہم ہوتی ہے۔
یہ متن OCR اور ڈاکومنٹ پراسیسنگ سسٹمز کی ٹیسٹنگ کے لیے استعمال کیا جا سکتا ہے۔
رامائن کی کہانی بھی بہت دلچسپ ہے: رام، سیتا، لکشمن، ہنومان اور راون کے کردار۔</p>
</body>
</html>
"""

pdfkit.from_string(html, "urdu_minimal_test.pdf", configuration=config,
                   options={'enable-local-file-access': '', 'encoding': 'UTF-8'})
print("Minimal PDF generated!")