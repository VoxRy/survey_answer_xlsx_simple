# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, fields, models


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    # Adding barcode_sn field if it's not already provided by other modules
    barcode_sn = fields.Char(string='Barkod / Seri No')

    # Generic fields for dynamic columns (up to 40 questions)
    p01 = fields.Char(compute='_compute_dynamic_fields')
    p02 = fields.Char(compute='_compute_dynamic_fields')
    p03 = fields.Char(compute='_compute_dynamic_fields')
    p04 = fields.Char(compute='_compute_dynamic_fields')
    p05 = fields.Char(compute='_compute_dynamic_fields')
    p06 = fields.Char(compute='_compute_dynamic_fields')
    p07 = fields.Char(compute='_compute_dynamic_fields')
    p08 = fields.Char(compute='_compute_dynamic_fields')
    p09 = fields.Char(compute='_compute_dynamic_fields')
    p10 = fields.Char(compute='_compute_dynamic_fields')
    p11 = fields.Char(compute='_compute_dynamic_fields')
    p12 = fields.Char(compute='_compute_dynamic_fields')
    p13 = fields.Char(compute='_compute_dynamic_fields')
    p14 = fields.Char(compute='_compute_dynamic_fields')
    p15 = fields.Char(compute='_compute_dynamic_fields')
    p16 = fields.Char(compute='_compute_dynamic_fields')
    p17 = fields.Char(compute='_compute_dynamic_fields')
    p18 = fields.Char(compute='_compute_dynamic_fields')
    p19 = fields.Char(compute='_compute_dynamic_fields')
    p20 = fields.Char(compute='_compute_dynamic_fields')
    p21 = fields.Char(compute='_compute_dynamic_fields')
    p22 = fields.Char(compute='_compute_dynamic_fields')
    p23 = fields.Char(compute='_compute_dynamic_fields')
    p24 = fields.Char(compute='_compute_dynamic_fields')
    p25 = fields.Char(compute='_compute_dynamic_fields')
    p26 = fields.Char(compute='_compute_dynamic_fields')
    p27 = fields.Char(compute='_compute_dynamic_fields')
    p28 = fields.Char(compute='_compute_dynamic_fields')
    p29 = fields.Char(compute='_compute_dynamic_fields')
    p30 = fields.Char(compute='_compute_dynamic_fields')
    p31 = fields.Char(compute='_compute_dynamic_fields')
    p32 = fields.Char(compute='_compute_dynamic_fields')
    p33 = fields.Char(compute='_compute_dynamic_fields')
    p34 = fields.Char(compute='_compute_dynamic_fields')
    p35 = fields.Char(compute='_compute_dynamic_fields')
    p36 = fields.Char(compute='_compute_dynamic_fields')
    p37 = fields.Char(compute='_compute_dynamic_fields')
    p38 = fields.Char(compute='_compute_dynamic_fields')
    p39 = fields.Char(compute='_compute_dynamic_fields')
    p40 = fields.Char(compute='_compute_dynamic_fields')

    def _compute_dynamic_fields(self):
        for rec in self:
            # Pre-clear
            for i in range(1, 41):
                rec[f'p{i:02d}'] = False

            if not rec.survey_id:
                continue

            questions = rec.survey_id.question_and_page_ids.filtered(lambda q: not q.is_page and q.question_type != 'note')
            line_map = {line.question_id.id: line for line in rec.user_input_line_ids}

            for i, q in enumerate(questions[:40], 1):
                line = line_map.get(q.id)
                val = ""
                if line:
                    if q.question_type in ['char_box', 'text_box']:
                        val = line.value_char_box or line.value_text_box or ""
                    elif q.question_type == 'numerical_box':
                        val = str(line.value_numerical_box) if line.value_numerical_box is not False else ""
                    elif q.question_type in ['date', 'datetime']:
                        val = str(line.value_date or line.value_datetime or "")
                    elif q.question_type in ['simple_choice', 'multiple_choice']:
                        choices = rec.user_input_line_ids.filtered(lambda l: l.question_id == q).mapped('suggested_answer_id.value')
                        val = ", ".join(choices)

                rec[f'p{i:02d}'] = val

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SurveyUserInput, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        ctx = self._context
        active_survey_id = ctx.get('active_survey_id') or ctx.get('default_survey_id') or ctx.get('survey_id')

        # Odoo 15 Specific: Check params if context is partial
        if not active_survey_id and 'params' in ctx:
            active_survey_id = ctx['params'].get('active_survey_id') or ctx['params'].get('survey_id')

        if view_type == 'tree' and active_survey_id:
            try:
                survey = self.env['survey.survey'].sudo().browse(int(active_survey_id))
                if survey.exists():
                    doc = etree.XML(res['arch'])
                    questions = survey.question_and_page_ids.filtered(lambda q: not q.is_page and q.question_type != 'note')

                    target_node = doc.xpath("//field[@name='partner_id']")
                    if not target_node:
                        target_node = doc.xpath("//field[last()]")

                    if target_node:
                        target_node = target_node[0]
                        for i, q in enumerate(questions[:40], 1):
                            fname = f'p{i:02d}'
                            display_title = q.title or f'Soru {i}'
                            if len(display_title) > 40:
                                display_title = display_title[:37] + '...'

                            new_field = etree.Element('field', {
                                'name': fname,
                                'string': display_title,
                                'optional': 'show' if i <= 15 else 'hide'
                            })
                            target_node.addnext(new_field)
                            target_node = new_field
                    res['arch'] = etree.tostring(doc)
            except Exception:
                pass
        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(SurveyUserInput, self).fields_get(allfields=allfields, attributes=attributes)

        ctx = self._context
        active_survey_id = ctx.get('active_survey_id') or ctx.get('default_survey_id') or ctx.get('survey_id')

        if not active_survey_id and 'params' in ctx:
             active_survey_id = ctx['params'].get('active_survey_id') or ctx['params'].get('survey_id')

        if not active_survey_id:
            ids = ctx.get('active_ids', [])
            if ids and isinstance(ids, list) and isinstance(ids[0], int):
                sample_rec = self.env['survey.user_input'].sudo().browse(ids[0]).exists()
                if sample_rec:
                    active_survey_id = sample_rec.survey_id.id

        if active_survey_id:
            try:
                survey = self.env['survey.survey'].sudo().browse(int(active_survey_id))
                if survey.exists():
                    questions = survey.question_and_page_ids.filtered(lambda q: not q.is_page and q.question_type != 'note')
                    for i, q in enumerate(questions[:40], 1):
                        fname = f'p{i:02d}'
                        if fname in res:
                            res[fname]['string'] = q.title or f'Soru {i}'
            except Exception:
                pass
        return res

    def action_export_selected_answers(self):
        """ Used by Server Action to export selected records with correct headers. """
        self.ensure_one()
        survey = self.survey_id
        return survey.with_context(user_input_ids=self.env.context.get('active_ids')).action_export_answers_xlsx()
