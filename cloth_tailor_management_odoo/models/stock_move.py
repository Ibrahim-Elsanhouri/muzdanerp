from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        if not self.inventory_id.tailor_request_id:
            return super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)

        res = super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
        self.ensure_one()
        if self.product_id.type != 'product':
            # no stock valuation for consumable products
            return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return False

        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        expense_account = self.product_id.categ_id.property_account_expense_categ_id.id
        if self._is_in():
            journal_id, stock_input, stock_output, acc_valuation = self._get_accounting_data_for_valuation()
            self.with_context(force_company=company_to.id)._create_account_move_line(expense_account, stock_input, journal_id, qty, description, svl_id, cost)

        # Create Journal Entry for products leaving the company
        if self._is_out():
            cost = -1 * cost
            journal_id, stock_input, stock_output, acc_valuation = self._get_accounting_data_for_valuation()
            self.with_context(force_company=company_from.id)._create_account_move_line(stock_output, expense_account, journal_id, qty, description, svl_id, cost)

        if self.company_id.anglo_saxon_accounting:
            #eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            self._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=self.product_id)
        return res