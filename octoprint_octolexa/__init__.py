# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import logging

import octoprint.plugin
from octoprint.events import Events
from octoprint.util import RepeatedTimer
from .update_status import UpdateStatus

class OctolexaPlugin(octoprint.plugin.StartupPlugin,
		     octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.AssetPlugin,
                     octoprint.plugin.TemplatePlugin,
		     octoprint.plugin.EventHandlerPlugin):

	def __init__(self):
		super(OctolexaPlugin, self).__init__()
		self._logger = logging.getLogger("octoprint.plugins.octolexa")
		self._updateStatusTimer = None
		self._update_status = UpdateStatus(self._logger)


	##~~ StartupPlugin mixin

	def on_after_startup(self):
	        self._logger.info("Octolexa Is Alive!")
        	self._restart_timer()

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
			update_settings_interval=10,
			baseApiUrl="https://octoprintalexaap.azurewebsites.net",
			baseRegistrationUrl="https://octoalexa.auth.us-east-1.amazoncognito.com/login",
			registration_client_key="3kk2ejt1u5bfv5un2sh1r8jjdf",
			printer_name=None,
			printer_uid=None,
			printer_is_registered=False,
			printer_last_update_result=None
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/octolexa.js"],
			css=["css/octolexa.css"],
			less=["less/octolexa.less"]
		)

	##~~ TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="settings", name='Octolexa', custom_bindings=True)
		]

        ##~~ EventHandler Plugin

	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED or event == Events.PRINT_DONE or event == Events.PRINT_FAILED:
			self._update_status.handle_event(event, payload)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			octolexa=dict(
				displayName="Octolexa Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="johnnyruz",
				repo="OctoPrint-Octolexa",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/johnnyruz/OctoPrint-Octolexa/archive/{target_version}.zip"
			)
		)

	##~~ Timer Functions

	def _restart_timer(self):
		# stop the timer
		if self._updateStatusTimer:
			self._logger.info(u"Stopping Timer...")
			self._updateStatusTimer.cancel()
			self.updateStatusTimer = None

		# start a new timer
		interval = self._settings.get_int(['update_settings_interval'])
		if interval:
			self._logger.info(u"Starting Timer...")
			self._updateStatusTimer = RepeatedTimer(interval, self.run_timer_job, None, None, True)
			self._updateStatusTimer.start()


	def run_timer_job(self):
		self._update_status.update_status(self._printer, self._settings)



# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Octolexa Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OctolexaPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
