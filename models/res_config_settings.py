import logging
_logger = logging.getLogger(__name__)
from ast import literal_eval
from odoo import api, models, fields

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	_logger.info('ResConfigSettings')
	mycompany_myname_flag = fields.Boolean("Just another checkbox")

	@api.multi
	def set_values(self):
		_logger.info('ResConfigSettings.set_values()')
		self.env['ir.config_parameter'].set_param('mycompany_myname_flag', bool(self.mycompany_myname_flag))

	@api.model
	def get_values(self):
		_logger.info('ResConfigSettings.get_values()')
		res = super(ResConfigSettings, self).get_values()
		#res.update(mycompany_myname_flag = self.env['ir.config_parameter'].get_param('mycompany_myname_flag'))
		return res