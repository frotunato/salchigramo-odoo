#-*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from io import BytesIO
import requests, pip, logging, twitter, base64, json

_logger = logging.getLogger(__name__)

class Error(Exception):
   pass

class RRSSTimeout(Error):
   pass

def publish_tweet (self, vals, afterCreation):
	try:
		image = self.image if afterCreation else vals['image']
		description = self.description if afterCreation else vals['description']
		file = BytesIO(base64.b64decode(image))
		file.mode = 'rb+'
		file.name = 'tmp.png'
		file.seek(0)
		
		twitterApi = twitter.Api(
			consumer_key = self.env['ir.config_parameter'].sudo().get_param('twitter_consumer_key'),
			consumer_secret = self.env['ir.config_parameter'].sudo().get_param('twitter_consumer_secret'),
			access_token_key = self.env['ir.config_parameter'].sudo().get_param('twitter_access_token_key'),
			access_token_secret = self.env['ir.config_parameter'].sudo().get_param('twitter_access_token_secret'))

		twitterResponse = twitterApi.PostUpdate(description, file)
		vals['twitter_id'] = twitterResponse.id
		vals['twitter_post_url'] = twitterResponse.media[0].expanded_url
		vals['active'] = True
	except twitter.TwitterError as e:
		raise exceptions.ValidationError(e)

	#_logger.debug(twitterResponse)

def delete_tweet (self, vals):
	if not self.twitter_id or not self.twitter_post_url:
		return
	try:
		twitterApi = twitter.Api(
			consumer_key = self.env['ir.config_parameter'].sudo().get_param('twitter_consumer_key'),
			consumer_secret = self.env['ir.config_parameter'].sudo().get_param('twitter_consumer_secret'),
			access_token_key = self.env['ir.config_parameter'].sudo().get_param('twitter_access_token_key'),
			access_token_secret = self.env['ir.config_parameter'].sudo().get_param('twitter_access_token_secret'))
		twitterResponse = twitterApi.DestroyStatus(self.twitter_id)
		_logger.debug(twitterResponse)
	except twitter.TwitterError as e:
		_logger.debug('deleting tweet that does not exist anymore!')
		#raise exceptions.ValidationError(e)
	finally:
		if vals:
			vals['twitter_id'] = vals['twitter_post_url'] = ""

def publish_instagram (self, vals, afterCreation):
	instagram_external_url = self.env['ir.config_parameter'].sudo().get_param('instagram_external_url')
	instagram_username = self.env['ir.config_parameter'].sudo().get_param('instagram_username')
	instagram_password = self.env['ir.config_parameter'].sudo().get_param('instagram_password')
	try:
		image = self.image if afterCreation else vals['image']
		description = self.description if afterCreation else vals['description']
		#instagramResponse = requests.post('https://salchigramo.herokuapp.com/', data={'image': image, 'description': description})

		instagramResponse = requests.post(instagram_external_url, headers={'username': instagram_username, 'password': instagram_password}, data={'image': image, 'description': description})
		instagramResponseData = json.loads(instagramResponse.text)
		#_logger.debug(json.loads(instagramResponse.text))
		if (instagramResponse.status_code >= 400):
			raise RRSSTimeout
		else:
			vals['instagram_post_url'] = instagramResponseData['url']
			vals['instagram_id'] = instagramResponseData['id']
			vals['active'] = True
	except RRSSTimeout:
		raise exceptions.ValidationError('Error posting to instagram: ' + instagramResponseData['message'])

def delete_instagram (self, vals):
	instagram_external_url = self.env['ir.config_parameter'].sudo().get_param('instagram_external_url')
	instagram_username = self.env['ir.config_parameter'].sudo().get_param('instagram_username')
	instagram_password = self.env['ir.config_parameter'].sudo().get_param('instagram_password')

	if not self.instagram_id or not self.instagram_post_url:
		return
	try:
		instagramResponse = requests.delete(instagram_external_url, headers={'username': instagram_username, 'password': instagram_password}, data={'url': self.instagram_post_url})
		instagramResponseData = json.loads(instagramResponse.text)
		if (instagramResponse.status_code >= 400):
			raise RRSSTimeout
		else:
			if vals:
				vals['instagram_id'] = vals['instagram_post_url'] = ""
			#_logger.debug(instagramResponseData)
	except RRSSTimeout as e:
		#_logger.debug('deleting instagram post that does not exist anymore!')
		raise exceptions.ValidationError('Error deleting from instagram: ' + instagramResponseData['message'])

def publish_facebook (self, vals, afterCreation):
	facebook_external_url = self.env['ir.config_parameter'].sudo().get_param('facebook_external_url')
	facebook_page_id = self.env['ir.config_parameter'].sudo().get_param('facebook_page_id')
	facebook_username = self.env['ir.config_parameter'].sudo().get_param('facebook_username')
	facebook_password = self.env['ir.config_parameter'].sudo().get_param('facebook_password')
	try:
		image = self.image if afterCreation else vals['image']
		description = self.description if afterCreation else vals['description']
		#instagramResponse = requests.post('https://salchigramo.herokuapp.com/', data={'image': image, 'description': description})

		facebookResponse = requests.post(facebook_external_url, headers={'username': facebook_username, 'password': facebook_password}, data={'image': image, 'pageId': facebook_page_id, 'description': description})
		_logger.debug(json.loads(facebookResponse.text))

		facebookResponseData = json.loads(facebookResponse.text)
		if (facebookResponse.status_code >= 400):
			raise RRSSTimeout
		else:
			vals['facebook_post_url'] = facebookResponseData['url']
			vals['facebook_id'] = facebookResponseData['id']
			vals['active'] = True
	except RRSSTimeout:
		raise exceptions.ValidationError('Error posting to Facebook: ' + facebookResponseData['message'])

def delete_facebook (self, vals):
	facebook_external_url = self.env['ir.config_parameter'].sudo().get_param('facebook_external_url')
	facebook_page_id = self.env['ir.config_parameter'].sudo().get_param('facebook_page_id')
	facebook_username = self.env['ir.config_parameter'].sudo().get_param('facebook_username')
	facebook_password = self.env['ir.config_parameter'].sudo().get_param('facebook_password')

	if not self.facebook_id or not self.facebook_post_url:
		return
	try:
		facebookResponse = requests.delete(facebook_external_url, headers={'username': facebook_username, 'password': facebook_password}, data={'postId': self.facebook_id, 'pageId': facebook_page_id})
		facebookResponseData = json.loads(facebookResponse.text)
		if (facebookResponse.status_code >= 400):
			raise RRSSTimeout
		else:
			if vals:
				vals['facebook_id'] = vals['facebook_post_url'] = ""
			#_logger.debug(instagramResponseData)
	except RRSSTimeout as e:
		#_logger.debug('deleting instagram post that does not exist anymore!')
		raise exceptions.ValidationError('Error deleting from Facebook: ' + facebookResponseData['message'])

class Salchigramo (models.Model):
	_name = 'salchigramo.publication'
	_description = 'desc Salchigramo.Publication'

	def check_pusblished_status (self):
		for record in self:
			record.active = any([record.publish_on_twitter, record.publish_on_instagram, record.publish_on_facebook])

	name = fields.Char(string="Nombre de la publicación")
	description = fields.Text()
	image = fields.Binary("Image")
	active = fields.Boolean(compute=check_pusblished_status, default=False)
	
	publish_on_twitter = fields.Boolean(string="Publicar en Twitter", default=False)
	publish_on_facebook = fields.Boolean(string="Publicar en Facebook", default=False)
	publish_on_instagram = fields.Boolean(string="Publicar en Instagram", default=False)
	
	twitter_id = fields.Char(string="Tweet ID", readonly=True)
	facebook_id = fields.Char(string="Facebook post ID", readonly=True)
	instagram_id = fields.Char(string="Instagram post ID", readonly=True)
	
	twitter_post_url = fields.Char(readonly=True)
	facebook_post_url = fields.Char(readonly=True)
	instagram_post_url = fields.Char(readonly=True)

	product_template_id = fields.Many2one('product.template', 'Producto')

	@api.model
	def create (self, vals):
		#for record in self:
		if vals['publish_on_twitter']:
			publish_tweet(self, vals, False)
		
		if vals['publish_on_instagram']:
			publish_instagram(self, vals, False)
		
		if vals['publish_on_instagram']:
			publish_facebook(self, vals, False)

		return super(Salchigramo, self).create(vals)
		
	def write (self, vals):
		#for record in self:
		if 'publish_on_instagram' in vals:
			if self.publish_on_instagram == True and vals['publish_on_instagram'] == False:
				delete_instagram (self, vals)
			elif self.publish_on_instagram == False and vals['publish_on_instagram'] == True:
				publish_instagram(self, vals, True)
		
		if 'publish_on_facebook' in vals:
			if self.publish_on_facebook == True and vals['publish_on_facebook'] == False:
				delete_facebook (self, vals)
			elif self.publish_on_facebook == False and vals['publish_on_facebook'] == True:
				publish_facebook(self, vals, True)
				
		if 'publish_on_twitter' in vals :
			if self.publish_on_twitter == True and vals['publish_on_twitter'] == False:
				delete_tweet (self, vals)
			elif self.publish_on_twitter == False and vals['publish_on_twitter'] == True:
				publish_tweet (self, vals, True)

		return super(Salchigramo, self).write(vals)
	
	def unlink (self):
		for record in self:
			if record.publish_on_instagram == True:
				delete_instagram(record, False)

			if record.publish_on_twitter == True:
				delete_tweet(record, False)

			if record.publish_on_facebook == True:
				delete_facebook(record, False)
					
		return super(Salchigramo, self).unlink()

class SalchigramoConfig (models.TransientModel):
	#_name = 'salchigramo.twitter'
	_inherit = 'res.config.settings'
	#_description = 'desc Salchigramo.Twitter'
	twitter_consumer_key = fields.Char(string="Consumer key")
	twitter_consumer_secret = fields.Char(string="Consumer secret")
	twitter_access_token_key = fields.Char(string="Access token key")
	twitter_access_token_secret = fields.Char(string="Access token secret")

	facebook_external_url = fields.Char(string="Puppeteer server URL")
	facebook_page_id = fields.Char(string="Facebook page ID")
	facebook_username = fields.Char(string="Username")
	facebook_password = fields.Char(string="Password")

	instagram_external_url = fields.Char(string="Puppeteer server URL")
	instagram_username = fields.Char(string="Username")
	instagram_password = fields.Char(string="Password")

	def get_values(self):
		res = super(SalchigramoConfig, self).get_values()
		params = self.env['ir.config_parameter'].sudo()
		res.update(
			twitter_consumer_key = params.get_param('twitter_consumer_key', default=""),
			twitter_consumer_secret = params.get_param('twitter_consumer_secret', default=""),
			twitter_access_token_key = params.get_param('twitter_access_token_key', default=""),
			twitter_access_token_secret = params.get_param('twitter_access_token_secret', default=""),
			facebook_external_url = params.get_param('facebook_external_url', default=""),
			facebook_page_id = params.get_param('facebook_page_id', default=""),
			facebook_username = params.get_param('facebook_username', default=""),
			facebook_password = params.get_param('facebook_password', default=""),
			instagram_external_url = params.get_param('instagram_external_url', default=""),
			instagram_username = params.get_param('instagram_username', default=""),
			instagram_password = params.get_param('instagram_password', default=""))
		return res
	
	def set_values(self):
		for record in self:
			super(SalchigramoConfig, record).set_values()
			record.env['ir.config_parameter'].sudo().set_param("twitter_consumer_key",  record.twitter_consumer_key)
			record.env['ir.config_parameter'].sudo().set_param("twitter_consumer_secret",  record.twitter_consumer_secret)
			record.env['ir.config_parameter'].sudo().set_param("twitter_access_token_key",  record.twitter_access_token_key)
			record.env['ir.config_parameter'].sudo().set_param("twitter_access_token_secret",  record.twitter_access_token_secret)
			
			record.env['ir.config_parameter'].sudo().set_param("facebook_username",  record.facebook_username)
			record.env['ir.config_parameter'].sudo().set_param("facebook_password",  record.facebook_password)
			record.env['ir.config_parameter'].sudo().set_param("facebook_external_url",  record.facebook_external_url)
			record.env['ir.config_parameter'].sudo().set_param("facebook_page_id",  record.facebook_page_id)

			record.env['ir.config_parameter'].sudo().set_param("instagram_username",  record.instagram_username)
			record.env['ir.config_parameter'].sudo().set_param("instagram_password",  record.instagram_password)
			record.env['ir.config_parameter'].sudo().set_param("instagram_external_url",  record.instagram_external_url)
