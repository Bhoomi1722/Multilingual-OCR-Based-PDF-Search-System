import pdfkit

# 🔹 Update path if different
path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

paragraph = """
یہ ایک مکمل پیراگراف ہے جو اردو زبان میں لکھا گیا ہے۔
اس پیراگراف کا مقصد پی ڈی ایف رینڈرنگ، فونٹ ایمبیڈنگ،
اور رائٹ ٹو لیفٹ ٹیکسٹ فلو کی جانچ کرنا ہے۔
اردو ایک خوبصورت زبان ہے جو دائیں سے بائیں لکھی جاتی ہے۔
اس میں حروف کی جوڑ توڑ اور لیگچر رینڈرنگ نہایت اہم ہوتی ہے۔
یہ متن OCR اور ڈاکومنٹ پراسیسنگ سسٹمز کی ٹیسٹنگ کے لیے استعمال کیا جا سکتا ہے۔
"""

# Repeat paragraphs to fill pages
content_block = "<p>" + paragraph + "</p>" * 8

html_content = f"""
<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="UTF-8">
<style>
body {{
    font-family: "Noto Nastaliq Urdu", serif;
    direction: rtl;
    text-align: right;
    font-size: 22px;
    line-height: 2.2;
    margin: 40px;
}}
h1 {{
    text-align: center;
}}
.page-break {{
    page-break-after: always;
}}
p {{
    margin-bottom: 20px;
}}
</style>
</head>
<body>

<h1>اردو ٹیسٹ دستاویز - صفحہ 1</h1>
{content_block}

<div class="page-break"></div>

<h1>اردو ٹیسٹ دستاویز - صفحہ 2</h1>
{content_block}

<div class="page-break"></div>

<h1>اردو ٹیسٹ دستاویز - صفحہ 3</h1>
{content_block}

<div class="page-break"></div>

<h1>اردو ٹیسٹ دستاویز - صفحہ 4</h1>
{content_block}

<div class="page-break"></div>

<h1>اردو ٹیسٹ دستاویز - صفحہ 5</h1>
{content_block}

</body>
</html>
"""

pdfkit.from_string(html_content, "urdu_test_document_5pages.pdf", configuration=config)

print("✅ 5 Page Urdu PDF Generated Successfully!")