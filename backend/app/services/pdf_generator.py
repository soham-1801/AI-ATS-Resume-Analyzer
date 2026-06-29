import io
import re
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, CondPageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Define curated colors for premium styling
PRIMARY_COLOR = colors.HexColor("#111827")  # Deep Charcoal
SECONDARY_COLOR = colors.HexColor("#6b7280")  # Soft Gray
ACCENT_GREEN = colors.HexColor("#059669")  # Clean Green
ACCENT_RED = colors.HexColor("#dc2626")  # Clean Red
CARD_BG = colors.HexColor("#ffffff")  # White Background
TEXT_COLOR = colors.HexColor("#374151")  # Medium Gray

class PDFGenerator:
    @staticmethod
    def generate_report(
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        upload_date: datetime,
        keyword_score: float,
        semantic_score: float,
        final_score: float,
        matched_skills: list[str],
        missing_skills: list[str],
        suggestions: str,
        category_breakdown: list = None,
        intelligence_layer: dict = None,
        improvement_roadmap: list = None,
        keywords_impact_analysis: str = "",
        skill_validation_explanation: str = "",
        estimated_future_score: str = ""
    ) -> io.BytesIO:
        """
        Generates a premium designed ATS resume assessment report in PDF format.
        Outputs to a memory stream (io.BytesIO).
        """
        buffer = io.BytesIO()
        
        # Page geometry
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )
        
        story = []
        
        # Typography / Styles Setup
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=PRIMARY_COLOR,
            spaceAfter=6
        )
        
        ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=20
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=PRIMARY_COLOR,
            spaceBefore=0,
            spaceAfter=0,
            keepWithNext=True
        )

        sub_header_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=PRIMARY_COLOR,
            spaceBefore=0,
            spaceAfter=4,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=TEXT_COLOR,
            leading=14
        )
        
        bold_body_style = ParagraphStyle(
            'BoldBody',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        ParagraphStyle(
            'BreakdownHeader',
            parent=bold_body_style,
            fontSize=12,
            textColor=PRIMARY_COLOR
        )

        card_title_style = ParagraphStyle(
            'CardTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            alignment=1  # Centered
        )

        card_value_style = ParagraphStyle(
            'CardValue',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            alignment=1  # Centered
        )

        feature_title_style = ParagraphStyle(
            'FeatureTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=PRIMARY_COLOR,
            spaceAfter=6,
            leading=14
        )

        feature_body_style = ParagraphStyle(
            'FeatureBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=TEXT_COLOR,
            leading=14
        )

        feature_bullet_style = ParagraphStyle(
            'FeatureBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=TEXT_COLOR,
            leading=14,
            leftIndent=10,
            firstLineIndent=-6,
            spaceBefore=2
        )

        feature_highlight_style = ParagraphStyle(
            'FeatureHighlight',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=ACCENT_GREEN,
            spaceBefore=6,
            leading=14
        )

        # Helper to determine score color
        def get_score_color(score: float):
            if score >= 80:
                return ACCENT_GREEN
            elif score >= 60:
                return colors.HexColor("#d97706") # Amber / Orange
            return ACCENT_RED

        # Helper to draw progress bars representing: Current Score, Target Score (80%), and Improvement Gap
        def draw_progress_bar(score: float, width_in_inches: float = 2.0, height: float = 6):
            if score < 80:
                w_current = max(0.01, (score / 100.0) * width_in_inches)
                w_gap = max(0.01, ((80.0 - score) / 100.0) * width_in_inches)
                w_remaining = max(0.01, (20.0 / 100.0) * width_in_inches)
                
                current_color = ACCENT_GREEN if score >= 80 else (colors.HexColor("#d97706") if score >= 60 else ACCENT_RED)
                gap_color = colors.HexColor("#fed7aa") # Lighter Orange for the improvement gap
                
                bar_table = Table([["", "", ""]], colWidths=[w_current, w_gap, w_remaining], rowHeights=[height])
                bar_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (0,0), current_color),
                    ('BACKGROUND', (1,0), (1,0), gap_color),
                    ('BACKGROUND', (2,0), (2,0), colors.HexColor("#e2e8f0")),
                    ('PADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
            else:
                w_current = max(0.01, (score / 100.0) * width_in_inches)
                w_remaining = max(0.01, ((100.0 - score) / 100.0) * width_in_inches)
                
                current_color = ACCENT_GREEN
                
                bar_table = Table([["", ""]], colWidths=[w_current, w_remaining], rowHeights=[height])
                bar_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (0,0), current_color),
                    ('BACKGROUND', (1,0), (1,0), colors.HexColor("#e2e8f0")),
                    ('PADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
            return bar_table

        # Define four status levels with corresponding colors and styles
        def get_card_style(score: float):
            if score >= 90:
                # EXCELLENT
                bg_color = colors.HexColor("#ecfdf5") # Light Green
                border_color = colors.HexColor("#a7f3d0")
                pill_bg = colors.HexColor("#d1fae5")
                pill_border = colors.HexColor("#059669")
                text_color = colors.HexColor("#047857")
                status_text = "Excellent"
            elif score >= 75:
                # GOOD
                bg_color = colors.HexColor("#eff6ff") # Light Blue
                border_color = colors.HexColor("#bfdbfe")
                pill_bg = colors.HexColor("#dbeafe")
                pill_border = colors.HexColor("#2563eb")
                text_color = colors.HexColor("#1d4ed8")
                status_text = "Good"
            elif score >= 50:
                # AVERAGE
                bg_color = colors.HexColor("#fffbeb") # Light Amber
                border_color = colors.HexColor("#fde68a")
                pill_bg = colors.HexColor("#fef3c7")
                pill_border = colors.HexColor("#d97706")
                text_color = colors.HexColor("#b45309")
                status_text = "Average"
            else:
                # CRITICAL
                bg_color = colors.HexColor("#fff1f2") # Light Rose
                border_color = colors.HexColor("#fecdd3")
                pill_bg = colors.HexColor("#ffe4e6")
                pill_border = colors.HexColor("#e11d48")
                text_color = colors.HexColor("#be123c")
                status_text = "Critical"

            t_style = ParagraphStyle('CardTitleStyle', parent=card_title_style, textColor=text_color)
            v_style = ParagraphStyle('CardValueStyle', parent=card_value_style, textColor=text_color)
            return bg_color, t_style, v_style, border_color, pill_bg, pill_border, text_color, status_text

        def make_dashboard_card(title: str, score: float):
            bg_color, t_style, v_style, border_color, pill_bg, pill_border, text_color, status_text = get_card_style(score)
            
            badge_style = ParagraphStyle(
                'BadgeStyle', 
                parent=styles['Normal'], 
                fontName='Helvetica-Bold', 
                fontSize=9, 
                leading=11,
                alignment=1,
                textColor=text_color
            )
            
            badge_p = Paragraph(f"<b>{status_text.upper()}</b>", badge_style)
            badge_table = Table([[badge_p]], colWidths=[1.3 * inch], rowHeights=[20])
            badge_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), pill_bg),
                ('BOX', (0,0), (-1,-1), 1, pill_border),
                ('PADDING', (0,0), (-1,-1), 2),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            badge_table.hAlign = 'CENTER'

            card_content = [
                Paragraph(title.upper(), t_style),
                Spacer(1, 6),
                Paragraph(f"<b>{int(score)}%</b>", v_style),
                Spacer(1, 8),
                badge_table
            ]
            # Wrap content in a Table to apply styling, background, and border
            card_table = Table([[card_content]], colWidths=[2.3 * inch], rowHeights=[1.5 * inch])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), bg_color),
                ('BOX', (0,0), (-1,-1), 1.5, border_color),
                ('PADDING', (0,0), (-1,-1), 12),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            return card_table

        # Helper to create section header with visual separator and increased spacing
        def make_section_header(title: str):
            header_para = Paragraph(title, section_style)
            line = Table([[""]], colWidths=[7.5 * inch], rowHeights=[1.5])
            line.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#d1d5db")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            return KeepTogether([
                Spacer(1, 18),
                header_para,
                Spacer(1, 4),
                line,
                Spacer(1, 8)
            ])

        # Helper to create side-by-side list cards (Strengths / Weaknesses or Section Detection)
        def make_list_card(title: str, bullets: str, title_color, bg_color, border_color):
            title_style = ParagraphStyle(
                'ListCardTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=12,
                textColor=title_color,
                spaceAfter=6
            )
            content = [
                Paragraph(title, title_style),
                Spacer(1, 4),
                Paragraph(bullets, body_style)
            ]
            card_table = Table([[content]], colWidths=[3.6 * inch])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), bg_color),
                ('BOX', (0,0), (-1,-1), 1, border_color),
                ('PADDING', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            return card_table

        # Helper to build small badges
        def make_badge(label: str, value: str, tier: str):
            if tier == 'success':
                bg = colors.HexColor("#ecfdf5")
                text_color = colors.HexColor("#047857")
                border = colors.HexColor("#a7f3d0")
            elif tier == 'warning':
                bg = colors.HexColor("#e0e7ff")
                text_color = colors.HexColor("#4338ca")
                border = colors.HexColor("#c7d2fe")
            else: # danger
                bg = colors.HexColor("#fff1f2")
                text_color = colors.HexColor("#be123c")
                border = colors.HexColor("#fecdd3")
                
            lbl_style = ParagraphStyle('BadgeLbl', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#64748b"), alignment=1)
            val_style = ParagraphStyle('BadgeVal', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=text_color, alignment=1)
            
            content = [
                Paragraph(label.upper(), lbl_style),
                Spacer(1, 2),
                Paragraph(value, val_style)
            ]
            t = Table([[content]], colWidths=[1.15 * inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), bg),
                ('BOX', (0,0), (-1,-1), 1, border),
                ('PADDING', (0,0), (-1,-1), 4),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            return t

        # --- Header Section ---
        header_data = [
            [
                Paragraph("AI RESUME ATS ALIGNMENT REPORT", title_style),
                Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('RightText', parent=styles['Normal'], alignment=2, textColor=colors.HexColor("#64748b")))
            ]
        ]
        header_table = Table(header_data, colWidths=[5.0 * inch, 2.5 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))
        
        # Horizontal line divider
        divider = Table([[""]], colWidths=[7.5 * inch], rowHeights=[2])
        divider.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), SECONDARY_COLOR),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider)
        story.append(Spacer(1, 15))

        # Extract scores from breakdown
        formatting_score = 0.0
        content_quality_score = 0.0
        skill_validation_score = 0.0
        ats_compatibility_score = 0.0
        for cat in (category_breakdown or []):
            name_low = cat.get("name", "").lower()
            if "formatting" in name_low:
                formatting_score = cat.get("score", 0.0)
            elif "keyword" in name_low:
                keyword_score = cat.get("score", 0.0)
            elif "content" in name_low:
                content_quality_score = cat.get("score", 0.0)
            elif "validation" in name_low:
                skill_validation_score = cat.get("score", 0.0)
            elif "compatibility" in name_low:
                ats_compatibility_score = cat.get("score", 0.0)

        # --- Section 1: Cover-Style Summary Section at the Top ---
        details_style = ParagraphStyle('Details', parent=body_style, leading=16)
        if upload_date:
            upload_date_ist = upload_date + timedelta(hours=5, minutes=30)
            date_str = upload_date_ist.strftime('%Y-%m-%d %I:%M %p IST')
        else:
            date_str = 'Unknown'
            
        left_content = [
            Paragraph(f"<font size='14'><b>{candidate_name}</b></font>", ParagraphStyle('CandName', parent=bold_body_style, fontSize=14, textColor=PRIMARY_COLOR)),
            Spacer(1, 6),
            Paragraph(f"<b>Email:</b> {candidate_email}", details_style),
            Paragraph(f"<b>Target Role:</b> {job_title if job_title else 'Software Engineer'}", details_style),
            Paragraph(f"<b>Date:</b> {date_str}", details_style),
        ]
        
        score_style = ParagraphStyle('ScoreVal', fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=PRIMARY_COLOR, alignment=1)
        score_lbl_style = ParagraphStyle('ScoreLbl', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#64748b"), alignment=1)
        
        grade_val = intelligence_layer.get("grade", "N/A") if intelligence_layer else "N/A"
        readiness_val = intelligence_layer.get("readiness_indicator", "N/A") if intelligence_layer else "N/A"
        hiring_val = intelligence_layer.get("hiring_probability", "N/A") if intelligence_layer else "N/A"
        
        # Determine tiers
        if grade_val in ['A+', 'A', 'B+']:
            grade_tier = 'success'
        elif grade_val in ['B', 'C']:
            grade_tier = 'warning'
        else:
            grade_tier = 'danger'
            
        if "interview ready" in readiness_val.lower():
            readiness_tier = 'success'
        elif "partially" in readiness_val.lower():
            readiness_tier = 'warning'
        else:
            readiness_tier = 'danger'
            
        if "high" in hiring_val.lower():
            hiring_tier = 'success'
        elif "medium" in hiring_val.lower():
            hiring_tier = 'warning'
        else:
            hiring_tier = 'danger'
            
        badge_grade = make_badge("Grade", grade_val, grade_tier)
        badge_readiness = make_badge("Readiness", readiness_val, readiness_tier)
        badge_hiring = make_badge("Hiring Prob", hiring_val, hiring_tier)
        
        badges_table = Table([[badge_grade, "", badge_readiness, "", badge_hiring]], colWidths=[1.15 * inch, 0.05 * inch, 1.15 * inch, 0.05 * inch, 1.15 * inch])
        badges_table.setStyle(TableStyle([
            ('PADDING', (0,0), (-1,-1), 0),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        right_content = [
            Paragraph("OVERALL ATS MATCH SCORE", score_lbl_style),
            Spacer(1, 4),
            Paragraph(f"<b>{int(final_score)}%</b>", score_style),
            Spacer(1, 6),
            badges_table
        ]
        
        cover_table = Table([[left_content, right_content]], colWidths=[3.8 * inch, 3.7 * inch])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
            ('PADDING', (0,0), (-1,-1), 15),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(cover_table)
        story.append(Spacer(1, 8))

        # --- Section 2: ATS Intelligence Dashboard (6 Score Cards) ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("ATS INTELLIGENCE DASHBOARD"))

        dashboard_data = [
            [
                make_dashboard_card("Overall ATS Score", final_score), "",
                make_dashboard_card("Formatting Score", formatting_score), "",
                make_dashboard_card("Keywords & Skills", keyword_score)
            ],
            ["", "", "", "", ""],  # vertical spacer row
            [
                make_dashboard_card("Content Quality", content_quality_score), "",
                make_dashboard_card("Skill Validation", skill_validation_score), "",
                make_dashboard_card("ATS Compatibility", ats_compatibility_score)
            ]
        ]
        
        dashboard_table = Table(dashboard_data, colWidths=[2.3 * inch, 0.3 * inch, 2.3 * inch, 0.3 * inch, 2.3 * inch], rowHeights=[None, 0.1 * inch, None])
        dashboard_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(dashboard_table)
        story.append(Spacer(1, 8))

        # --- Section 2.1: Why This Score? ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("WHY THIS SCORE?"))
        for cat in (category_breakdown or []):
            name_cat = cat.get("name", "")
            score_cat = cat.get("score", 0.0)
            cat.get("potential_gain", 0.0)
            issues_cat = cat.get("issues", [])
            recs_cat = cat.get("recommendations", [])
            
            # Header text
            header_left_style = ParagraphStyle('CatHeaderLeft', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=PRIMARY_COLOR)
            header_right_style = ParagraphStyle('CatHeaderRight', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#475569"), alignment=2)
            
            hdr_left = Paragraph(f"<b>{name_cat.upper()}</b>", header_left_style)
            imp_needed = cat.get("improvement_needed", max(0.0, 80.0 - score_cat))
            if imp_needed > 0:
                imp_color = ACCENT_RED.hexval()
                imp_text = f"+{int(round(imp_needed))}%"
            else:
                imp_color = ACCENT_GREEN.hexval()
                imp_text = "0% (Met)"

            hdr_right = Paragraph(
                f"Score: <b>{int(score_cat)}%</b>  |  Target: <b>80%</b>  |  Improvement Needed: <font color='{imp_color}'><b>{imp_text}</b></font>", 
                header_right_style
            )
            
            hdr_table = Table([[hdr_left, hdr_right]], colWidths=[3.5 * inch, 3.6 * inch])
            hdr_table.setStyle(TableStyle([
                ('PADDING', (0,0), (-1,-1), 0),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            
            # Progress bar for the specific category
            cat_progress_bar = draw_progress_bar(score_cat, width_in_inches=7.1 * inch, height=6)
            
            # Problems and Recommendations Columns
            problems_html = ""
            if issues_cat:
                for issue in issues_cat:
                    problems_html += f"<font color='{ACCENT_RED.hexval()}'>-</font> {issue}<br/>"
            else:
                problems_html = f"<font color='{ACCENT_GREEN.hexval()}'>+ </font> No problems detected.<br/>"
                
            recs_html = ""
            if recs_cat:
                for rec in recs_cat:
                    recs_html += f"<font color='{SECONDARY_COLOR.hexval()}'>+ </font> {rec}<br/>"
            else:
                recs_html = "No recommendations needed.<br/>"
                
            col_title_style = ParagraphStyle('ColTitle', parent=bold_body_style, fontSize=9, textColor=colors.HexColor("#475569"))
            
            cols_data = [
                [Paragraph("<b>IDENTIFIED PROBLEMS:</b>", col_title_style), Paragraph("<b>RECOMMENDED FIXES:</b>", col_title_style)],
                [Paragraph(problems_html, body_style), Paragraph(recs_html, body_style)]
            ]
            cols_table = Table(cols_data, colWidths=[3.5 * inch, 3.6 * inch])
            cols_table.setStyle(TableStyle([
                ('PADDING', (0,0), (-1,-1), 0),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,0), 4),
            ]))
            
            # Wrap all in card
            card_elements = [
                hdr_table,
                Spacer(1, 6),
                cat_progress_bar,
                Spacer(1, 10),
                cols_table
            ]
            
            cat_card = Table([[card_elements]], colWidths=[7.5 * inch])
            cat_card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('PADDING', (0,0), (-1,-1), 12),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            story.append(cat_card)
            story.append(Spacer(1, 8))
            
        story.append(Spacer(1, 4))

        # --- Section 2.2: Keywords Analysis (Matched vs Missing Table) ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("KEYWORDS ANALYSIS"))
        matched_str = ", ".join(matched_skills) if matched_skills else "None"
        
        skills_impact_list = intelligence_layer.get("missing_skills_impact", []) if intelligence_layer else []
        total_skills_gain = intelligence_layer.get("total_skills_impact_gain", 0.0) if intelligence_layer else 0.0
        
        def make_matched_skills_card(matched_str: str):
            content = [
                Paragraph("<b>MATCHED KEYWORDS</b>", sub_header_style),
                Spacer(1, 6),
                Paragraph(matched_str, body_style)
            ]
            card = Table([[content]], colWidths=[3.6 * inch])
            card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
                ('PADDING', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            return card

        def make_missing_skills_card(skills_impact_list: list, total_skills_gain: float):
            content = [
                Paragraph("<b>MISSING KEYWORDS & IMPACT</b>", sub_header_style),
                Spacer(1, 6),
            ]
            
            # Structured table of missing skills, estimated gain, and total gain
            tbl_header_style = ParagraphStyle('TblHdr', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#475569"))
            tbl_data = [
                [Paragraph("<b>Skill Name</b>", tbl_header_style), Paragraph("<b>Estimated Gain</b>", tbl_header_style)]
            ]
            
            if skills_impact_list:
                for item in skills_impact_list:
                    skill_name = item.get("skill", "")
                    skill_impact = item.get("impact", 0.0)
                    tbl_data.append([
                        Paragraph(skill_name, body_style),
                        Paragraph(f"+{skill_impact}%", ParagraphStyle('GainStyle', parent=bold_body_style, textColor=ACCENT_GREEN))
                    ])
            else:
                tbl_data.append([Paragraph("None detected", body_style), Paragraph("0%", body_style)])
                
            skills_impact_table = Table(tbl_data, colWidths=[2.0 * inch, 1.2 * inch])
            skills_impact_table.setStyle(TableStyle([
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ]))
            
            content.append(skills_impact_table)
            content.append(Spacer(1, 8))
            content.append(Paragraph(f"<b>Total Recovery Gain:</b> <font color='{ACCENT_GREEN.hexval()}'><b>+{total_skills_gain}%</b></font>", bold_body_style))
            
            card = Table([[content]], colWidths=[3.6 * inch])
            card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
                ('PADDING', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            return card

        kw_table = Table([[make_matched_skills_card(matched_str), "", make_missing_skills_card(skills_impact_list, total_skills_gain)]], colWidths=[3.6 * inch, 0.3 * inch, 3.6 * inch])
        kw_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(kw_table)
        story.append(Spacer(1, 8))

        # --- Section 2.3: ATS Recovery Calculator (Callout Highlight Style) ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("ATS RECOVERY CALCULATOR"))
        if intelligence_layer:
            current = intelligence_layer.get("current_score", 0.0)
            proj = intelligence_layer.get("projected_score", 0.0)
            recov = intelligence_layer.get("recoverable_score", 0.0)
            
            # Intro text explaining the calculator
            intro_p_style = ParagraphStyle('CalcIntro', parent=body_style, fontSize=10, leading=14, textColor=TEXT_COLOR)
            intro_p = Paragraph(
                "The ATS Recovery Calculator simulates potential improvements to your candidate match score by resolving issues across formatting, critical keywords, and content validation.",
                intro_p_style
            )
            
            # Helper to build metric cards
            def make_metric_card(title: str, val: str, bg: colors.Color, border: colors.Color, text_color: colors.Color, is_large: bool = False):
                lbl_style = ParagraphStyle('MetricLbl', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor("#64748b"), alignment=1)
                val_style = ParagraphStyle('MetricVal', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=text_color, alignment=1)
                
                content = [
                    Paragraph(title.upper(), lbl_style),
                    Spacer(1, 4),
                    Paragraph(f"<b>{val}</b>", val_style)
                ]
                t = Table([[content]], colWidths=[2.2 * inch], rowHeights=[0.9 * inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), bg),
                    ('BOX', (0,0), (-1,-1), 1.5 if is_large else 1.0, border),
                    ('PADDING', (0,0), (-1,-1), 8),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                return t

            card_current = make_metric_card("Current ATS Score", f"{int(current)}%", colors.HexColor("#f1f5f9"), colors.HexColor("#cbd5e1"), colors.HexColor("#475569"))
            card_recoverable = make_metric_card("Recoverable Score", f"+{int(recov)}%", colors.HexColor("#eff6ff"), colors.HexColor("#bfdbfe"), colors.HexColor("#1d4ed8"))
            card_projected = make_metric_card("Projected Future ATS Score", f"{int(proj)}%", colors.HexColor("#ecfdf5"), colors.HexColor("#a7f3d0"), colors.HexColor("#047857"), is_large=True)

            metrics_table = Table([[card_current, "", card_recoverable, "", card_projected]], colWidths=[2.2 * inch, 0.25 * inch, 2.2 * inch, 0.25 * inch, 2.2 * inch])
            metrics_table.setStyle(TableStyle([
                ('PADDING', (0,0), (-1,-1), 0),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))

            # Bottom detailed factors table
            calc_header = ParagraphStyle('CalcHeader', parent=bold_body_style, fontSize=9, textColor=PRIMARY_COLOR)
            calc_data = [
                [
                    Paragraph("<b>Recovery Area</b>", calc_header),
                    Paragraph("<b>Current Score</b>", calc_header),
                    Paragraph("<b>Potential Recovery</b>", calc_header),
                    Paragraph("<b>Status Impact</b>", calc_header)
                ],
                [
                    Paragraph("Resume Formatting & Structure", body_style),
                    Paragraph(f"{int(formatting_score)}%", body_style),
                    Paragraph(f"+{int(intelligence_layer.get('formatting_recovery', 0))}%", ParagraphStyle('RecGreen', parent=bold_body_style, textColor=ACCENT_GREEN)),
                    Paragraph("Improves layout parsing and syntax extraction", body_style)
                ],
                [
                    Paragraph("Keywords & Critical Skills", body_style),
                    Paragraph(f"{int(keyword_score)}%", body_style),
                    Paragraph(f"+{int(intelligence_layer.get('keywords_recovery', 0))}%", ParagraphStyle('RecGreen', parent=bold_body_style, textColor=ACCENT_GREEN)),
                    Paragraph("Closes the skill gap for semantic indexing", body_style)
                ],
                [
                    Paragraph("Content Quality & Action Verbs", body_style),
                    Paragraph(f"{int(content_quality_score)}%", body_style),
                    Paragraph(f"+{int(intelligence_layer.get('content_recovery', 0))}%", ParagraphStyle('RecGreen', parent=bold_body_style, textColor=ACCENT_GREEN)),
                    Paragraph("Enhances narrative strength and impact", body_style)
                ],
                [
                    Paragraph("Skill Validation & Context", body_style),
                    Paragraph(f"{int(skill_validation_score)}%", body_style),
                    Paragraph(f"+{int(intelligence_layer.get('validation_recovery', 0))}%", ParagraphStyle('RecGreen', parent=bold_body_style, textColor=ACCENT_GREEN)),
                    Paragraph("Proves expertise through situational context", body_style)
                ]
            ]
            
            calc_table = Table(calc_data, colWidths=[2.2 * inch, 1.0 * inch, 1.3 * inch, 2.6 * inch])
            calc_table.setStyle(TableStyle([
                ('PADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ]))

            # Pack all into the Large Highlighted Callout Card
            calc_card_content = [
                intro_p,
                Spacer(1, 12),
                metrics_table,
                Spacer(1, 15),
                calc_table
            ]

            large_calc_card = Table([[calc_card_content]], colWidths=[7.5 * inch])
            large_calc_card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#3b82f6")), # Blue border
                ('PADDING', (0,0), (-1,-1), 12),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            
            story.append(large_calc_card)
        else:
            story.append(Paragraph("Recovery calculator data unavailable.", body_style))
        story.append(Spacer(1, 8))

        # --- Section 2.4: Strengths & Weaknesses (2-column layout) ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("STRENGTHS & WEAKNESSES"))
        if intelligence_layer:
            strengths_list = intelligence_layer.get("strengths", [])
            weaknesses_list = intelligence_layer.get("weaknesses", [])
            
            str_bullets = "".join(f"<font color='{ACCENT_GREEN.hexval()}'>+ </font>{item}<br/>" for item in strengths_list) if strengths_list else "None detected<br/>"
            weak_bullets = "".join(f"<font color='{ACCENT_RED.hexval()}'>- </font>{item}<br/>" for item in weaknesses_list) if weaknesses_list else "None detected<br/>"
            
            str_card = make_list_card("STRENGTHS", str_bullets, colors.HexColor("#047857"), colors.HexColor("#ecfdf5"), colors.HexColor("#a7f3d0"))
            weak_card = make_list_card("WEAKNESSES", weak_bullets, colors.HexColor("#be123c"), colors.HexColor("#fff1f2"), colors.HexColor("#fecdd3"))

            str_weak_table = Table([[str_card, "", weak_card]], colWidths=[3.6 * inch, 0.3 * inch, 3.6 * inch])
            str_weak_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(str_weak_table)
        else:
            story.append(Paragraph("Strengths and weaknesses data unavailable.", body_style))
        story.append(Spacer(1, 8))

        # --- Section 2.5: Recruiter Readiness ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("RECRUITER READINESS"))
        if intelligence_layer:
            readiness = intelligence_layer.get("readiness_indicator", "Not Interview Ready")
            hiring = intelligence_layer.get("hiring_probability", "Low")
            current = intelligence_layer.get("current_score", 0.0)
            proj = intelligence_layer.get("projected_score", 0.0)
            
            current_prob_val = int(current * 0.9)
            proj_prob_val = int(proj * 0.9)
            
            projected_readiness = "Interview Ready" if proj >= 80 else "Partially Interview Ready" if proj >= 60 else "Not Interview Ready"
            
            readiness_data = [
                [
                    Paragraph("<b>Current Readiness:</b>", bold_body_style),
                    Paragraph(readiness, body_style),
                    Paragraph("<b>Projected Readiness:</b>", bold_body_style),
                    Paragraph(projected_readiness, body_style)
                ],
                [
                    Paragraph("<b>Current Hiring Probability:</b>", bold_body_style),
                    Paragraph(f"{current_prob_val}% ({hiring} Probability)", body_style),
                    Paragraph("<b>Projected Hiring Probability:</b>", bold_body_style),
                    Paragraph(f"{proj_prob_val}% (High Probability)", body_style)
                ]
            ]
            readiness_table = Table(readiness_data, colWidths=[2.0 * inch, 1.75 * inch, 2.0 * inch, 1.75 * inch])
            readiness_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('PADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
            ]))
            story.append(readiness_table)
        else:
            story.append(Paragraph("Recruiter readiness details unavailable.", body_style))
        story.append(Spacer(1, 8))

        # --- Section 2.5.1: Resume Section Detection ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("RESUME SECTION DETECTION"))
        if intelligence_layer:
            found_list = intelligence_layer.get("found_sections", [])
            missing_list = intelligence_layer.get("missing_sections", [])
            
            found_bullets = "".join(f"<font color='{ACCENT_GREEN.hexval()}'>+ </font>{item}<br/>" for item in found_list) if found_list else "None detected<br/>"
            missing_bullets = "".join(f"<font color='{ACCENT_RED.hexval()}'>- </font>{item}<br/>" for item in missing_list) if missing_list else "All standard sections present!<br/>"
            
            found_sec_card = make_list_card("FOUND SECTIONS", found_bullets, colors.HexColor("#047857"), colors.HexColor("#ecfdf5"), colors.HexColor("#a7f3d0"))
            missing_sec_card = make_list_card("MISSING SECTIONS", missing_bullets, colors.HexColor("#be123c"), colors.HexColor("#fff1f2"), colors.HexColor("#fecdd3"))
            
            sec_table = Table([[found_sec_card, "", missing_sec_card]], colWidths=[3.6 * inch, 0.3 * inch, 3.6 * inch])
            sec_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(sec_table)
        else:
            story.append(Paragraph("Section detection details unavailable.", body_style))
        story.append(Spacer(1, 8))

        # --- Section 2.5.2: ATS Keyword Coverage ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("ATS KEYWORD COVERAGE"))
        if intelligence_layer:
            coverage_pct = intelligence_layer.get("keyword_coverage_percentage", 0.0)
            req_kws = intelligence_layer.get("required_keywords", [])
            fnd_kws = intelligence_layer.get("found_keywords", [])
            msg_kws = intelligence_layer.get("missing_keywords", [])
            
            req_kws_str = ", ".join(req_kws) if req_kws else "None"
            fnd_kws_str = ", ".join(fnd_kws) if fnd_kws else "None"
            msg_kws_str = ", ".join(msg_kws) if msg_kws else "None"
            
            cov_progress_bar = draw_progress_bar(coverage_pct, width_in_inches=4.8 * inch, height=6)
            cov_header_cell = [
                Paragraph(f"<font color='{SECONDARY_COLOR.hexval()}'><b>{coverage_pct}%</b></font> ({len(fnd_kws)} of {len(req_kws)} keywords)", body_style),
                Spacer(1, 4),
                cov_progress_bar
            ]
            
            cov_data = [
                [
                    Paragraph("<b>Keyword Coverage:</b>", bold_body_style),
                    cov_header_cell
                ],
                [
                    Paragraph("<b>Required Keywords:</b>", bold_body_style),
                    Paragraph(req_kws_str, body_style)
                ],
                [
                    Paragraph("<b>Found Keywords:</b>", bold_body_style),
                    Paragraph(fnd_kws_str, body_style)
                ],
                [
                    Paragraph("<b>Missing Keywords:</b>", bold_body_style),
                    Paragraph(msg_kws_str, body_style)
                ]
            ]
            cov_table = Table(cov_data, colWidths=[2.2 * inch, 5.3 * inch])
            cov_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('PADDING', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
            ]))
            story.append(cov_table)
        else:
            story.append(Paragraph("Keyword coverage details unavailable.", body_style))
        story.append(Spacer(1, 8))

        # --- Section 2.6: Priority Fix Rankings ---
        if intelligence_layer:
            story.append(Spacer(1, 5))
            story.append(Paragraph("PRIORITY FIX RANKINGS", sub_header_style))
            story.append(Spacer(1, 5))
            fixes_list = intelligence_layer.get("priority_fixes", [])
            fixes_elements = []
            
            if fixes_list:
                for idx, fix in enumerate(fixes_list):
                    title_fix = fix.get("title", "")
                    impact_fix = fix.get("impact", "")
                    desc_fix = fix.get("description", "")
                    pts_fix = fix.get("points_recovery", 0.0)
                    
                    color_impact = ACCENT_RED.hexval() if impact_fix == "High" else (SECONDARY_COLOR.hexval() if impact_fix == "Medium" else "gray")
                    
                    fix_para = f"<b>{idx+1}. {title_fix}</b> (<font color='{color_impact}'><b>{impact_fix} Impact</b></font>)<br/>{desc_fix} (Recovers +{pts_fix}% of total score)"
                    fixes_elements.append(Paragraph(fix_para, body_style))
                    fixes_elements.append(Spacer(1, 3))
            else:
                fixes_elements.append(Paragraph("No urgent fixes required.", body_style))
                
            fixes_box = Table([[fixes_elements]], colWidths=[7.5 * inch])
            fixes_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('PADDING', (0,0), (-1,-1), 10),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
            ]))
            story.append(fixes_box)
            story.append(Spacer(1, 8))

        # --- Section 2.6.5: ATS Improvement Summary ("How to Reach 80% ATS Score") ---
        if intelligence_layer and intelligence_layer.get("improvement_summary"):
            summary_recs = intelligence_layer.get("improvement_summary", [])
            summary_elements = [
                Paragraph("<b>HOW TO REACH 80% ATS SCORE</b>", sub_header_style),
                Spacer(1, 6)
            ]
            for item in summary_recs:
                summary_elements.append(Paragraph(f"<font color='{ACCENT_GREEN.hexval()}'>✓</font> {item}", body_style))
                summary_elements.append(Spacer(1, 3))
            
            summary_elements.append(Spacer(1, 6))
            summary_elements.append(Paragraph(f"<b>Estimated Score After Improvements:</b> <font color='{ACCENT_GREEN.hexval()}'><b>{estimated_future_score}</b></font>", bold_body_style))
            
            summary_box = Table([[summary_elements]], colWidths=[7.5 * inch])
            summary_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('PADDING', (0,0), (-1,-1), 10),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
            ]))
            story.append(summary_box)
            story.append(Spacer(1, 8))

        # --- Section 2.7: Search Indexing & Semantic Roadmap ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("ATS SEARCH INDEXING & SEMANTIC ROADMAP"))
        if intelligence_layer:
            kw_impact = intelligence_layer.get("keyword_impact_score", 0.0)
            impact_elements = [
                Paragraph(f"<b>Keyword Impact Score:</b> {kw_impact}%", bold_body_style),
                Paragraph(f"<b>Missing Keywords Analysis:</b> {keywords_impact_analysis}", body_style),
                Spacer(1, 4),
                Paragraph(f"<b>Skill Validation Principle:</b> {skill_validation_explanation}", body_style),
                Spacer(1, 4),
                Paragraph(f"<b>Projected Estimated Score:</b> {estimated_future_score} after recommended adjustments.", bold_body_style)
            ]
            impact_box = Table([[impact_elements]], colWidths=[7.5 * inch])
            impact_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
                ('PADDING', (0,0), (-1,-1), 10),
                ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
            ]))
            story.append(impact_box)
            story.append(Spacer(1, 8))

        # --- Section 3: Skill Map & Keyword Matches ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("SKILL MAP & KEYWORD MATCHES"))
        matched_text = ", ".join(matched_skills) if matched_skills else "None"
        missing_text = ", ".join(missing_skills) if missing_skills else "None"
        
        green_hdr = ParagraphStyle('GreenHdr', parent=sub_header_style, textColor=ACCENT_GREEN)
        red_hdr = ParagraphStyle('RedHdr', parent=sub_header_style, textColor=ACCENT_RED)
        blue_hdr = ParagraphStyle('BlueHdr', parent=sub_header_style, textColor=SECONDARY_COLOR)
        gray_hdr = ParagraphStyle('GrayHdr', parent=sub_header_style, textColor=colors.HexColor("#64748b"))

        skills_data = [
            [Paragraph("Matched Skills", green_hdr), Paragraph(matched_text, body_style)],
            [Paragraph("Missing / Targeted Skills", red_hdr), Paragraph(missing_text, body_style)],
            [Paragraph("Recommended Skills To Add", blue_hdr), Paragraph(missing_text, body_style)],
            [Paragraph("Skills Unrelated / Not Recommended", gray_hdr), Paragraph("Skills not present in Job Description, or unrelated to target role", body_style)]
        ]
        skills_table = Table(skills_data, colWidths=[2.2 * inch, 5.3 * inch])
        skills_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
            ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        story.append(skills_table)
        story.append(Spacer(1, 8))

        # --- Section 4: AI Optimization Recommendations ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("AI OPTIMIZATION RECOMMENDATIONS"))
        suggestion_elements = []
        if suggestions:
            paragraphs = suggestions.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # Safely replace pairs of ** with <b>...</b>
                formatted_para = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', para)
                
                if formatted_para.startswith("* ") or formatted_para.startswith("- "):
                    formatted_para = f"&bull; {formatted_para[2:]}"
                    p_style = ParagraphStyle('BulletText', parent=body_style, leftIndent=15)
                elif formatted_para.startswith("### "):
                    formatted_para = formatted_para[4:]
                    p_style = ParagraphStyle('SubHeaderRecs', parent=sub_header_style, textColor=SECONDARY_COLOR, spaceBefore=8, spaceAfter=4)
                else:
                    p_style = body_style
                    
                suggestion_elements.append(Paragraph(formatted_para, p_style))
                suggestion_elements.append(Spacer(1, 4))
        else:
            suggestion_elements.append(Paragraph("No suggestions generated.", body_style))

        for elem in suggestion_elements:
            story.append(elem)
        story.append(Spacer(1, 8))

        # --- Section 5: Key Features (At absolute bottom) ---
        story.append(CondPageBreak(2.0 * inch))
        story.append(make_section_header("KEY FEATURES"))
        feature_1_content = [
            Paragraph("Comprehensive Scoring", feature_title_style),
            Paragraph("Get detailed scores across 5 key dimensions:", feature_body_style),
            Paragraph("&bull; Formatting", feature_bullet_style),
            Paragraph("&bull; Keywords & Skills", feature_bullet_style),
            Paragraph("&bull; Content Quality", feature_bullet_style),
            Paragraph("&bull; Skill Validation", feature_bullet_style),
            Paragraph("&bull; ATS Compatibility", feature_bullet_style),
        ]

        feature_2_content = [
            Paragraph("Skill Validation", feature_title_style),
            Paragraph("Verify that your claimed skills are demonstrated in your projects and experience using AI-powered semantic analysis.", feature_body_style),
            Paragraph("No more empty claims!", feature_highlight_style)
        ]

        features_data = [
            [feature_1_content, "", feature_2_content]
        ]
        features_table = Table(features_data, colWidths=[3.6 * inch, 0.3 * inch, 3.6 * inch])
        features_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), CARD_BG),
            ('BOX', (0,0), (0,0), 0.75, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (0,0), 10),

            ('BACKGROUND', (2,0), (2,0), CARD_BG),
            ('BOX', (2,0), (2,0), 0.75, colors.HexColor("#cbd5e1")),
            ('PADDING', (2,0), (2,0), 10),

            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(features_table)

        # Build document
        doc.build(story)
        buffer.seek(0)
        return buffer
