from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os

# Create a presentation object
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# Define color scheme
PRIMARY_BLUE = RGBColor(37, 99, 235)
DARK_BLUE = RGBColor(30, 64, 175)
DARK_BG = RGBColor(15, 23, 42)
WHITE = RGBColor(255, 255, 255)
LIGHT_GRAY = RGBColor(226, 232, 240)

# ========== SLIDE 1: SmartFile Converter (file.py) ==========
slide1 = prs.slides.add_slide(prs.slide_layouts[6])

# Background
background = slide1.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = DARK_BG

# Title
title_box = slide1.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
title_frame = title_box.text_frame
title_frame.text = "SmartFile Converter"
title_p = title_frame.paragraphs[0]
title_p.font.size = Pt(48)
title_p.font.bold = True
title_p.font.color.rgb = PRIMARY_BLUE
title_p.alignment = PP_ALIGN.CENTER

# Subtitle
subtitle_box = slide1.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(9), Inches(0.4))
subtitle_frame = subtitle_box.text_frame
subtitle_frame.text = "Web-based tool for managing and converting mainframe files"
subtitle_p = subtitle_frame.paragraphs[0]
subtitle_p.font.size = Pt(18)
subtitle_p.font.color.rgb = LIGHT_GRAY
subtitle_p.alignment = PP_ALIGN.CENTER

# What Box
what_box = slide1.shapes.add_shape(
    1,  # Rectangle
    Inches(0.5), Inches(1.6), Inches(9), Inches(1.2))
what_box.fill.solid()
what_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
what_box.line.color.rgb = PRIMARY_BLUE
what_box.line.width = Pt(2)

what_text = what_box.text_frame
what_text.word_wrap = True
what_text.margin_top = Inches(0.15)
what_text.margin_left = Inches(0.2)

p1 = what_text.paragraphs[0]
p1.text = "What is SmartFile Converter?"
p1.font.size = Pt(22)
p1.font.bold = True
p1.font.color.rgb = PRIMARY_BLUE
p1.space_after = Pt(8)

desc = what_text.add_paragraph()
desc.text = "A simple web application that helps users convert, rename, and modify mainframe data files. Users can access it through their web browser - no complex software installation needed."
desc.font.size = Pt(15)
desc.font.color.rgb = WHITE

# Features Box
features_box = slide1.shapes.add_shape(1, Inches(0.5), Inches(3.0), Inches(9), Inches(3.7))
features_box.fill.solid()
features_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
features_box.line.color.rgb = DARK_BLUE
features_box.line.width = Pt(2)

features_text = features_box.text_frame
features_text.word_wrap = True
features_text.margin_top = Inches(0.15)
features_text.margin_left = Inches(0.25)
features_text.margin_right = Inches(0.25)

f1 = features_text.paragraphs[0]
f1.text = "Key Features & Buttons"
f1.font.size = Pt(24)
f1.font.bold = True
f1.font.color.rgb = PRIMARY_BLUE
f1.space_after = Pt(10)

features = [
    ("📝 Rename .FF File", "Changes the name of mainframe format files quickly"),
    ("✏️ Modify .FF File", "Updates or edits the content inside files"),
    ("⚙️ Run Dowitcher", "Converts files using the Dowitcher conversion tool"),
    ("👁️ Display Output", "Shows the results of file operations on screen"),
    ("🔧 Run Roys Tool", "Processes EBCDIC files using REXX conversion"),
    ("🔢 Display with Hex", "Shows file content in hexadecimal format"),
    ("📄 Convert Records", "Converts specific records from mainframe format"),
    ("⌨️ Input with Hex", "Allows entering data in hexadecimal format"),
    ("📂 Update Paths", "Configures file locations and directories")
]

for feature, description in features:
    p = features_text.add_paragraph()
    p.text = f"{feature}"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(100, 181, 246)
    p.space_after = Pt(2)
    
    d = features_text.add_paragraph()
    d.text = f"   {description}"
    d.font.size = Pt(12)
    d.font.color.rgb = LIGHT_GRAY
    d.space_after = Pt(6)

# Footer
footer_box = slide1.shapes.add_textbox(Inches(0.5), Inches(7.1), Inches(9), Inches(0.3))
footer_frame = footer_box.text_frame
footer_frame.text = "Powered by Astadia TEAM"
footer_p = footer_frame.paragraphs[0]
footer_p.font.size = Pt(12)
footer_p.font.color.rgb = LIGHT_GRAY
footer_p.alignment = PP_ALIGN.CENTER

# ========== SLIDE 2: ConvertFlow Studio (scripts_ui.py) ==========
slide2 = prs.slides.add_slide(prs.slide_layouts[6])

# Background
background2 = slide2.background
fill2 = background2.fill
fill2.solid()
fill2.fore_color.rgb = DARK_BG

# Title
title_box2 = slide2.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
title_frame2 = title_box2.text_frame
title_frame2.text = "ConvertFlow Studio"
title_p2 = title_frame2.paragraphs[0]
title_p2.font.size = Pt(48)
title_p2.font.bold = True
title_p2.font.color.rgb = PRIMARY_BLUE
title_p2.alignment = PP_ALIGN.CENTER

# Subtitle
subtitle_box2 = slide2.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(9), Inches(0.4))
subtitle_frame2 = subtitle_box2.text_frame
subtitle_frame2.text = "Complete workflow management system for data migration projects"
subtitle_p2 = subtitle_frame2.paragraphs[0]
subtitle_p2.font.size = Pt(18)
subtitle_p2.font.color.rgb = LIGHT_GRAY
subtitle_p2.alignment = PP_ALIGN.CENTER

# What Box
what_box2 = slide2.shapes.add_shape(1, Inches(0.5), Inches(1.6), Inches(9), Inches(1.2))
what_box2.fill.solid()
what_box2.fill.fore_color.rgb = RGBColor(30, 41, 59)
what_box2.line.color.rgb = PRIMARY_BLUE
what_box2.line.width = Pt(2)

what_text2 = what_box2.text_frame
what_text2.word_wrap = True
what_text2.margin_top = Inches(0.15)
what_text2.margin_left = Inches(0.2)

p1_2 = what_text2.paragraphs[0]
p1_2.text = "What is ConvertFlow Studio?"
p1_2.font.size = Pt(22)
p1_2.font.bold = True
p1_2.font.color.rgb = PRIMARY_BLUE
p1_2.space_after = Pt(8)

desc2 = what_text2.add_paragraph()
desc2.text = "A comprehensive web platform that manages entire data migration workflows. It automates file copying, conversion, and cloud upload processes - reducing manual work from hours to minutes."
desc2.font.size = Pt(15)
desc2.font.color.rgb = WHITE

# Features Box
features_box2 = slide2.shapes.add_shape(1, Inches(0.5), Inches(3.0), Inches(9), Inches(3.7))
features_box2.fill.solid()
features_box2.fill.fore_color.rgb = RGBColor(30, 41, 59)
features_box2.line.color.rgb = DARK_BLUE
features_box2.line.width = Pt(2)

features_text2 = features_box2.text_frame
features_text2.word_wrap = True
features_text2.margin_top = Inches(0.15)
features_text2.margin_left = Inches(0.25)
features_text2.margin_right = Inches(0.25)

f1_2 = features_text2.paragraphs[0]
f1_2.text = "Workflow Modules & Functions"
f1_2.font.size = Pt(24)
f1_2.font.bold = True
f1_2.font.color.rgb = PRIMARY_BLUE
f1_2.space_after = Pt(10)

workflows = [
    ("📁 Copy Bulk Files", "Copies multiple files from source to destination in one operation"),
    ("🔄 Run DataTurn", "Executes data transformation and format conversion processes"),
    ("📋 Create EXPFD", "Generates export file definitions for data migration"),
    ("🔁 Bulk Conversion", "Converts large batches of files automatically"),
    ("📂 Create Folder Structure", "Sets up required directory structure for projects"),
    ("📁 Open Project Folders", "Quickly accesses project directories in file explorer"),
    ("☁️ Copy to AWS S3", "Uploads converted files to Amazon cloud storage"),
    ("🗺️ FF File Mapping", "Maps and validates file format definitions"),
    ("⚙️ Scripts Configuration", "Manages settings and file paths for all operations")
]

for workflow, description in workflows:
    p = features_text2.add_paragraph()
    p.text = f"{workflow}"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(100, 181, 246)
    p.space_after = Pt(2)
    
    d = features_text2.add_paragraph()
    d.text = f"   {description}"
    d.font.size = Pt(12)
    d.font.color.rgb = LIGHT_GRAY
    d.space_after = Pt(6)

# Footer
footer_box2 = slide2.shapes.add_textbox(Inches(0.5), Inches(7.1), Inches(9), Inches(0.3))
footer_frame2 = footer_box2.text_frame
footer_frame2.text = "Powered by Astadia TEAM"
footer_p2 = footer_frame2.paragraphs[0]
footer_p2.font.size = Pt(12)
footer_p2.font.color.rgb = LIGHT_GRAY
footer_p2.alignment = PP_ALIGN.CENTER

# ========== SLIDE 3: Key Advantages ==========
slide3 = prs.slides.add_slide(prs.slide_layouts[6])

# Background
background3 = slide3.background
fill3 = background3.fill
fill3.solid()
fill3.fore_color.rgb = DARK_BG

# Title
title_box3 = slide3.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
title_frame3 = title_box3.text_frame
title_frame3.text = "Key Advantages & Benefits"
title_p3 = title_frame3.paragraphs[0]
title_p3.font.size = Pt(48)
title_p3.font.bold = True
title_p3.font.color.rgb = PRIMARY_BLUE
title_p3.alignment = PP_ALIGN.CENTER

# Subtitle
subtitle_box3 = slide3.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(9), Inches(0.4))
subtitle_frame3 = subtitle_box3.text_frame
subtitle_frame3.text = "Why the new web-based approach is better than manual scripts"
subtitle_p3 = subtitle_frame3.paragraphs[0]
subtitle_p3.font.size = Pt(18)
subtitle_p3.font.color.rgb = LIGHT_GRAY
subtitle_p3.alignment = PP_ALIGN.CENTER

# Main advantages box
advantages_box = slide3.shapes.add_shape(1, Inches(0.5), Inches(1.6), Inches(9), Inches(5))
advantages_box.fill.solid()
advantages_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
advantages_box.line.color.rgb = PRIMARY_BLUE
advantages_box.line.width = Pt(2)

advantages_text = advantages_box.text_frame
advantages_text.word_wrap = True
advantages_text.margin_top = Inches(0.2)
advantages_text.margin_left = Inches(0.3)
advantages_text.margin_right = Inches(0.3)

# Header
a_header = advantages_text.paragraphs[0]
a_header.text = "🎯 How We Improved the Process"
a_header.font.size = Pt(28)
a_header.font.bold = True
a_header.font.color.rgb = PRIMARY_BLUE
a_header.space_after = Pt(15)

advantages = [
    ("1. ⏱️ 85% Time Savings", 
     "What took 4 hours now takes 10 minutes. All operations accessible from one web interface instead of running 9+ separate scripts."),
    
    ("2. 👥 Anyone Can Use It", 
     "No technical training needed. Simple point-and-click interface replaces complex command-line operations. 10x more people can now perform conversions."),
    
    ("3. ⚙️ Single Configuration", 
     "One path.txt file for all tools. Previously had to manually edit different config files for each script. Web-based editor with validation."),
    
    ("4. ✅ Error Prevention", 
     "Automatic validation catches mistakes before execution. Built-in retry logic handles file system delays. Clear error messages instead of cryptic failures."),
    
    ("5. ☁️ AWS Cloud Integration", 
     "One-click upload to Amazon S3. Previously required manual AWS CLI commands. Saves 90% of time on cloud operations."),
    
    ("6. 💼 Professional & Ready", 
     "Modern interface suitable for client demonstrations. Real-time progress indicators. Consistent branding across all tools.")
]

for title, description in advantages:
    # Title
    p_title = advantages_text.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(18)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(100, 181, 246)
    p_title.space_after = Pt(4)
    p_title.space_before = Pt(12)
    
    # Description
    p_desc = advantages_text.add_paragraph()
    p_desc.text = description
    p_desc.font.size = Pt(13)
    p_desc.font.color.rgb = LIGHT_GRAY
    p_desc.space_after = Pt(8)

# Footer
footer_box3 = slide3.shapes.add_textbox(Inches(0.5), Inches(7.1), Inches(9), Inches(0.3))
footer_frame3 = footer_box3.text_frame
footer_frame3.text = "Powered by Astadia TEAM"
footer_p3 = footer_frame3.paragraphs[0]
footer_p3.font.size = Pt(12)
footer_p3.font.color.rgb = LIGHT_GRAY
footer_p3.alignment = PP_ALIGN.CENTER

# Save the presentation
prs.save('File_Conversion_Tools_With_Advantages.pptx')
print("✅ PowerPoint presentation created successfully!")
print("📄 File: File_Conversion_Tools_With_Advantages.pptx")
print("📊 Slides: 3 slides")
print("   - Slide 1: SmartFile Converter (file.py)")
print("   - Slide 2: ConvertFlow Studio (scripts_ui.py)")
print("   - Slide 3: Key Advantages & Benefits")
print("\n🎯 Highlights:")
print("   ⏱️ 85% Time Savings")
print("   👥 10x More Users Can Use It")
print("   ⚙️ Single Configuration")
print("   ✅ Error Prevention")
print("   ☁️ AWS Cloud Integration")
print("   💼 Professional Interface")
