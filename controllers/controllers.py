# -*- coding: utf-8 -*-
import logging
#import urllib3
#import json
from odoo import http

class Salchigramo(http.Controller):
	@http.route('/salchigramo/publication/', auth='public')
	def index(self, **kw):
		@http.route('/salchigramo/publication/objects/', auth='public')
		def list(self, **kw):
			return http.request.render('salchigramo.publication_listing', {
				'root': '/salchigramo/publication',
				'objects': http.request.env['salchigramo.publication'].search([]),
				})
			
			@http.route('/salchigramo/publication/objects/<model("salchigramo.publication"):obj>/', auth='public')
			def object(self, obj, **kw):
				return http.request.render('salchigramo.publication_object', {
					'object': obj
					})

class SalchigramoTwitter(http.Controller):
	@http.route('/salchigramo/twitter/', auth='public')
	def index(self, **kw):
		@http.route('/salchigramo/twitter/objects/', auth='public')
		def list(self, **kw):
			return http.request.render('salchigramo.twitter_listing', {
				'root': '/salchigramo/twitter',
				'objects': http.request.env['salchigramo.twitter'].search([]),
				})
			
			@http.route('/salchigramo/salchigramo/objects/<model("salchigramo.twitter"):obj>/', auth='public')
			def object(self, obj, **kw):
				return http.request.render('salchigramo.publication_object', {
					'object': obj
					})