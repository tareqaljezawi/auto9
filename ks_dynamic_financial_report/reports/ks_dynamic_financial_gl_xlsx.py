# -*- coding: utf-8 -*-
import io
from odoo import models, api, _
from odoo.tools.misc import xlsxwriter
import datetime


class KsDynamicFinancialXlsxGL(models.Model):
    _inherit = 'ks.dynamic.financial.base'

    @api.model
    def ks_get_xlsx_general_ledger(self, ks_df_informations):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        currency_id = self.env.user.company_id.currency_id
        move_lines = self.ks_process_general_ledger(ks_df_informations)
        ks_company_id = self.env['res.company'].sudo().browse(ks_df_informations.get('company_id'))

        sheet = workbook.add_worksheet('General Ledger')
        row_pos = 0
        row_pos_2 = 0
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 10)

        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })

        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            'align': 'center',
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'border': True,
            'text_wrap': True,
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'bottom': True,
        })
        line_header.set_num_format(
            '#,##0.' + '0' * ks_company_id.currency_id.decimal_places or 2)
        line_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'top': True,
            'font': 'Arial',
            'bottom': True,
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            # 'top': True,
            # 'bottom': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light.set_num_format(
            '#,##0.' + '0' * ks_company_id.currency_id.decimal_places or 2)
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'top': True,
            # 'bottom': True,
            'font': 'Arial',
            'align': 'center',
            'num_format': 'mm/dd/yyyy'
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'bottom': True,
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_initial.set_num_format(
            '#,##0.' + '0' * ks_company_id.currency_id.decimal_places or 2)
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            # 'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_ending.set_num_format(
            '#,##0.' + '0' * ks_company_id.currency_id.decimal_places or 2)
        # line_header_bold.num_format = currency_id

        row_pos_2 += 0
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])['date_format'].replace('/', '-')
        ks_new_start_date = (datetime.datetime.strptime(
            ks_df_informations['date'].get('ks_start_date'), '%Y-%m-%d').date()).strftime(lang_id)
        ks_new_end_date = (datetime.datetime.strptime(
            ks_df_informations['date'].get('ks_end_date'), '%Y-%m-%d').date()).strftime(lang_id)
        if ks_df_informations:
            # Date from
            sheet.write_string(row_pos_2, 0, _('Date from'), format_header)
            sheet.write_string(row_pos_2 + 1, row_pos_2, ks_new_start_date,
                               content_header_date)

            sheet.write_string(row_pos_2, row_pos_2 + 1, _('Date to'), format_header)

            sheet.write_string(row_pos_2 + 1, row_pos_2 + 1, ks_new_end_date,
                               content_header_date)

            # Journals
            row_pos_2 += 0
            sheet.write_string(row_pos_2, 3, _('Journals'), format_header)
            j_list = ', '.join(
                journal.get('code') or '' for journal in ks_df_informations['journals'] if journal.get('selected'))
            sheet.write_string(row_pos_2 + 1, 3, j_list, content_header)
            #
            # # Accounts
            row_pos_2 += 0
            if ks_df_informations.get('analytic_accounts'):
                sheet.write_string(row_pos_2, 5, _('Analytic Accounts'), format_header)
                a_list = ', '.join(lt or '' for lt in ks_df_informations['selected_analytic_account_names'])
                sheet.write_string(row_pos_2 + 1, 5, a_list, content_header)
            row_pos_2 += 0
            if ks_df_informations.get('analytic_tags'):
                sheet.write_string(row_pos_2, 6, _('Tags'), format_header)
                a_list = ', '.join(lt or '' for lt in ks_df_informations['selected_analytic_tag_names'])
                sheet.write_string(row_pos_2 + 1, 6, a_list, content_header)

            row_pos_2 += 0
            sheet.write_string(row_pos_2, 7, _('Accounts'), format_header)
            j_list = ', '.join(
                account.get('name') or '' for account in ks_df_informations['account'] if account.get('selected'))
            sheet.write_string(row_pos_2 + 1, 7, j_list, content_header)

        row_pos += 5
        if ks_df_informations.get('ks_report_with_lines', False):
            sheet.write_string(row_pos, 0, _('Date'),
                               format_header)
            sheet.write_string(row_pos, 1, _('JRNL'),
                               format_header)
            sheet.write_string(row_pos, 2, _('Partner'),
                               format_header)
            # sheet.write_string(row_pos, 3, _('Ref'),
            #                         format_header)
            sheet.write_string(row_pos, 3, _('Move'),
                               format_header)
            sheet.write_string(row_pos, 4, _('Entry Label'),
                               format_header)
            if self.env['ir.config_parameter'].sudo().get_param('ks_enable_ledger_in_bal'):
                sheet.write_string(row_pos, 5, _('Initial Balance'),
                                   format_header)
                sheet.write_string(row_pos, 6, _('Debit'),
                                   format_header)
                sheet.write_string(row_pos, 7, _('Credit'),
                                   format_header)
                sheet.write_string(row_pos, 8, _('Balance'),
                                   format_header)
            else:
                sheet.write_string(row_pos, 5, _('Debit'),
                                   format_header)
                sheet.write_string(row_pos, 6, _('Credit'),
                                   format_header)
                sheet.write_string(row_pos, 7, _('Balance'),
                                   format_header)
        else:
            sheet.merge_range(row_pos, 0, row_pos, 1, _('Code'), format_header)
            sheet.merge_range(row_pos, 2, row_pos, 4, _('Account'), format_header)
            if self.env['ir.config_parameter'].sudo().get_param('ks_enable_ledger_in_bal'):
                sheet.write_string(row_pos, 5, _('Initial Balance'),
                                   format_header)
                sheet.write_string(row_pos, 6, _('Debit'),
                                   format_header)
                sheet.write_string(row_pos, 7, _('Credit'),
                                   format_header)
                sheet.write_string(row_pos, 8, _('Balance'),
                                   format_header)
            else:
                sheet.write_string(row_pos, 5, _('Debit'),
                                   format_header)
                sheet.write_string(row_pos, 6, _('Credit'),
                                   format_header)
                sheet.write_string(row_pos, 7, _('Balance'),
                                   format_header)

        if move_lines:
            for line in move_lines[0]:
                # line = line[0]
                row_pos += 1
                sheet.merge_range(row_pos, 0, row_pos, 4,
                                  '            ' + move_lines[0][line].get('code') + ' - ' + move_lines[0][line].get(
                                      'name'),
                                  line_header_left)
                if self.env['ir.config_parameter'].sudo().get_param('ks_enable_ledger_in_bal'):
                    sheet.write_number(row_pos, 5, float(move_lines[0][line].get('initial_balance', 0)), line_header)
                    sheet.write_number(row_pos, 6, float(move_lines[0][line].get('debit')), line_header)
                    sheet.write_number(row_pos, 7, float(move_lines[0][line].get('credit')), line_header)
                    sheet.write_number(row_pos, 8, float(move_lines[0][line].get('balance')), line_header)
                else:
                    sheet.write_number(row_pos, 5, float(move_lines[0][line].get('debit')), line_header)
                    sheet.write_number(row_pos, 6, float(move_lines[0][line].get('credit')), line_header)
                    sheet.write_number(row_pos, 7, float(move_lines[0][line].get('balance')), line_header)

                if ks_df_informations.get('ks_report_with_lines', False):
                    # offset = 0
                    # account = line

                    # count, offset, sub_lines = self.with_context().build_detailed_move_lines(ks_df_informations,offset=0,account=line,
                    #                                                           fetch_range=1000000)
                    for sub_line in move_lines[0][line]['lines']:
                        if sub_line['initial_bal']:
                            row_pos += 1
                            sheet.write_string(row_pos, 4, sub_line.get('move_name'),
                                               line_header_light_initial)
                            if self.env['ir.config_parameter'].sudo().get_param('ks_enable_ledger_in_bal'):
                                sheet.write_number(row_pos, 5, float(move_lines[0][line].get('initial_balance', 0)),
                                                   line_header_light_initial)
                                sheet.write_number(row_pos, 6, float(move_lines[0][line].get('debit')),
                                                   line_header_light_initial)
                                sheet.write_number(row_pos, 7, float(move_lines[0][line].get('credit')),
                                                   line_header_light_initial)
                                sheet.write_number(row_pos, 8, float(move_lines[0][line].get('balance')),
                                                   line_header_light_initial)
                            else:
                                sheet.write_number(row_pos, 5, float(move_lines[0][line].get('debit')),
                                                   line_header_light_initial)
                                sheet.write_number(row_pos, 6, float(move_lines[0][line].get('credit')),
                                                   line_header_light_initial)
                                sheet.write_number(row_pos, 7, float(move_lines[0][line].get('balance')),
                                                   line_header_light_initial)
                        elif not sub_line['initial_bal'] and not sub_line['ending_bal']:
                            row_pos += 1
                            date = sub_line.get('ldate')
                            lang = self.env.user.lang
                            lang_id = self.env['res.lang'].search([('code', '=', lang)])['date_format']
                            new_date = date.strftime(lang_id)
                            sheet.write(row_pos, 0, new_date,
                                        line_header_light_date)
                            sheet.write_string(row_pos, 1, sub_line.get('lcode'),
                                               line_header_light)
                            sheet.write_string(row_pos, 2, sub_line.get('partner_name') or '',
                                               line_header_light)
                            # sheet.write_string(row_pos, 3, sub_line.get('lref') or '',
                            #                         line_header_light)
                            sheet.write_string(row_pos, 3, sub_line.get('move_name'),
                                               line_header_light)
                            sheet.write_string(row_pos, 4, sub_line.get('lname') or '',
                                               line_header_light)
                            if self.env['ir.config_parameter'].sudo().get_param('ks_enable_ledger_in_bal'):
                                sheet.write_number(row_pos, 5,
                                                   float(sub_line.get('initial_balance', 0)), line_header_light)
                                sheet.write_number(row_pos, 6,
                                                   float(sub_line.get('debit')), line_header_light)
                                sheet.write_number(row_pos, 7,
                                                   float(sub_line.get('credit')), line_header_light)
                                sheet.write_number(row_pos, 8,
                                                   float(sub_line.get('balance')), line_header_light)
                            else:
                                sheet.write_number(row_pos, 5,
                                                   float(sub_line.get('debit')), line_header_light)
                                sheet.write_number(row_pos, 6,
                                                   float(sub_line.get('credit')), line_header_light)
                                sheet.write_number(row_pos, 7,
                                                   float(sub_line.get('balance')), line_header_light)
                        else:  # Ending Balance
                            row_pos += 1

                            sheet.write(row_pos, 4, sub_line.get('move_name'),
                                        line_header_light_ending)
                            if self.env['ir.config_parameter'].sudo().get_param('ks_enable_ledger_in_bal'):
                                sheet.write_number(row_pos, 5, float(move_lines[0][line].get('initial_balance', 0)),
                                                   line_header_light_ending)
                                sheet.write_number(row_pos, 6, float(move_lines[0][line].get('debit')),
                                                   line_header_light_ending)
                                sheet.write_number(row_pos, 7, float(move_lines[0][line].get('credit')),
                                                   line_header_light_ending)
                                sheet.write_number(row_pos, 8, float(move_lines[0][line].get('balance')),
                                                   line_header_light_ending)

                            else:
                                sheet.write_number(row_pos, 5, float(move_lines[0][line].get('debit')),
                                                   line_header_light_ending)
                                sheet.write_number(row_pos, 6, float(move_lines[0][line].get('credit')),
                                                   line_header_light_ending)
                                sheet.write_number(row_pos, 7, float(move_lines[0][line].get('balance')),
                                                   line_header_light_ending)
        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return generated_file
