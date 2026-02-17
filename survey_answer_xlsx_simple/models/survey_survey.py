# -*- coding: utf-8 -*-
import base64
import io

from odoo import _, api, fields, models
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    def action_view_user_inputs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("survey.action_survey_user_input")
        action['domain'] = [('survey_id', '=', self.id), ('state', '=', 'done')]
        # Pass active_survey_id to trigger dynamic columns in fields_view_get
        action['context'] = {
            'default_survey_id': self.id,
            'active_survey_id': self.id,
            'search_default_completed': 1
        }
        return action

    def action_export_answers_xlsx(self):
        if not xlsxwriter:
            raise UserError(_("The xlsxwriter library is not installed. Please install it to use this feature."))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Answers')

        bold = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})

        # Get all questions (excluding pages and notes)
        questions = self.question_and_page_ids.filtered(lambda q: not q.is_page and q.question_type != 'note')

        # Headers
        headers = ['ID', 'Tarih', 'Durum']
        for q in questions:
            headers.append(q.title)

        for col, title in enumerate(headers):
            sheet.write(0, col, title, bold)

        # Get completed answers
        domain = [('survey_id', '=', self.id), ('state', '=', 'done')]
        user_input_ids = self._context.get('user_input_ids')
        if user_input_ids:
            domain.append(('id', 'in', user_input_ids))

        user_inputs = self.env['survey.user_input'].search(domain)

        row = 1
        for ui in user_inputs:
            sheet.write(row, 0, ui.id)
            sheet.write(row, 1, str(ui.create_date))
            sheet.write(row, 2, ui.state)

            # Map answers to columns
            lines = ui.user_input_line_ids
            line_map = {line.question_id.id: line for line in lines}

            col = 3
            for q in questions:
                line = line_map.get(q.id)
                val = ""
                if line:
                    if q.question_type in ['char_box', 'text_box']:
                        val = line.value_char_box or line.value_text_box or ""
                    elif q.question_type == 'numerical_box':
                        val = line.value_numerical_box
                    elif q.question_type in ['date', 'datetime']:
                        val = str(line.value_date or line.value_datetime or "")
                    elif q.question_type in ['simple_choice', 'multiple_choice']:
                        choices = lines.filtered(lambda l: l.question_id == q).mapped('suggested_answer_id.value')
                        val = ", ".join(choices)

                sheet.write(row, col, val)
                col += 1
            row += 1

        workbook.close()
        output.seek(0)

        file_name = f"{self.title}_Answers.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': base64.b64encode(output.read()),
            'res_model': 'survey.survey',
            'res_id': self.id,
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
