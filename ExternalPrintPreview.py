import sublime
import sublime_plugin
import subprocess
import tempfile
import os.path
import shutil

def getmysettings(settingtoget):
	return sublime.load_settings("ExternalPrintPreview.sublime-settings").get(settingtoget)
class ExternalPrintPreviewCommand(sublime_plugin.TextCommand):
	def run(self, view):

		how_much_to_print = self.get_how_much_to_print()
		if not how_much_to_print:
			return

		file_to_print = self.get_file_to_print()
		syntax = self.view.settings().get('syntax').lower()

		if how_much_to_print == "savedfile":
			text = False
			stdin = False

		elif how_much_to_print == "selection":
			text = self.get_selections(syntax)
			stdin = subprocess.PIPE

		else: 			# "unsavedfile":
			text = self.view.substr(sublime.Region(0, self.view.size())) # entire buffer
			text = text.encode('utf-8')
			stdin = subprocess.PIPE

		if getmysettings("send_directly_to_printer"):	#no conversion, no preview, direct to lpr
			cmd = self.get_lpr_options(how_much_to_print)
			self.pipeit(cmd, textvalue = text, stdinvalue = stdin)
			return

		if not getmysettings("skip_conversion"):
			tmp_file_name = tempfile.NamedTemporaryFile(delete=False).name
			if "markdown" in syntax:
				tmp_file_name = tmp_file_name+".pdf"	# windows enscript needs +".ps" ?

			cmd = self.get_converter_cmd_and_options(syntax,tmp_file_name, how_much_to_print, file_to_print)
			if not self.pipeit(cmd, textvalue = text, stdinvalue = stdin): # do file conversion
				return
		else: #skip file conversion
			if not text:
				tmp_file_name = file_to_print
			else:
				tmp_file_name = tempfile.NamedTemporaryFile(delete=False).name
				with open(tmp_file_name, 'wb') as file_:
					file_.write(text)

		self.send_to_preview(tmp_file_name)		# preview
		return

	def get_converter_cmd_and_options(self, syntax, tmp_file_name, how_much_to_print, file_to_print):
		titlelist= ["$n", "-J", "title", "-t"]

		if "markdown" in syntax:
			cmd = getmysettings("pdf_converter")
			options = getmysettings("pdf_options")

		elif getmysettings("secondary_postscript_syntax_override") in syntax:
			cmd = getmysettings("postscript_converter")
			options = getmysettings("secondary_postscript_options")

		else:
			cmd = getmysettings("postscript_converter")
			options = getmysettings("postscript_options")

		# thanks SublimePrint.py for this options_list approach:
		options_list = ["--{0}={1}".format(k, v) for k, v in options.items() if v != ""]
		options_list += ["--{0}".format(k) for k, v in options.items() if v == ""]
		options_list.append("--output={0}".format(tmp_file_name))

		if how_much_to_print == "savedfile":
			cmd = [cmd] + [file_to_print] + options_list

		elif how_much_to_print == "unsavedfile":
			if any((True for x in titlelist if x in str(options_list))) and "markdown" not in syntax:
				options_list.append("--title={0}".format(file_to_print))
			cmd = [cmd] + options_list

		else:	#selection
			if any((True for x in titlelist if x in str(options_list))) and "markdown" not in syntax:
				if getmysettings("override_title_for_selections") == "":
					options_list.append("--title={0}".format(file_to_print))
				elif (getmysettings("override_title_for_selections").lower()) == "notitle":
					options_list.append("--title={0}".format(""))
				else:
					options_list.append("--title={0}".format(getmysettings("override_title_for_selections")))
			cmd = [cmd] + options_list
		return cmd

	def get_file_to_print(self):
		if self.view.file_name():
		 	return self.view.file_name()
		else:
			return "untitled"

	def get_current_directory(self):
		if self.get_file_to_print() == "untitled":
			return None
		else:
			return os.path.dirname(self.get_file_to_print())

	def get_how_much_to_print(self):
		if getmysettings("print_selections"):
			if len(self.view.sel()[0]) > 0:
				return "selection"

		if self.view.file_name() and not self.view.is_dirty():
			return "savedfile"
		else:
			if getmysettings("warn_if_dirty"):
				if not sublime.ok_cancel_dialog("You have unsaved changes.\nOkay to preview/print from buffer?"):
					return False
			return("unsavedfile")

	def get_selections(self, syntax):
		text = ""
		for region in self.view.sel():
			text = text + self.view.substr(region) + "\n\n"
		text = text.encode('utf-8')

		if "markdown" in syntax:
			if getmysettings("yaml_header_injection") and getmysettings("yaml_header_include_file_location")!= "":
				try:
					with open(getmysettings("yaml_header_include_file_location"), 'r') as filex:
						filetext=(filex.read())
						filetext = filetext+"\n\n"
						text = filetext.encode('utf-8') + text
				except:
					print("Couldn't read YAML file")
					sublime.message_dialog("Couldn't read YAML file")
		return text

	def pipeit(self, cmd, textvalue=None, shellvalue=False, stdinvalue = None):
		current_directory = self.get_current_directory()
		p = subprocess.Popen(cmd, shell=shellvalue, cwd=current_directory, universal_newlines=False,
		stdin=stdinvalue, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		result, error = p.communicate(textvalue)
		if p.returncode > 0:
			error=error.decode('utf-8').strip()
			sublime.error_message("Error: "+str(p.returncode)+"\n\n"+error)
			return False
		return True

	def send_to_preview(self, tmp_file_name):
	# note: we don't want a handler for stderr or stdout here.
	# otherwise sublime hangs while waiting for the previewer to exit
		current_directory = self.get_current_directory()
		cmd = getmysettings("previewer/printer")
		if cmd == "gtklp":
# gtklp has a bug wherein it will only process a filename if
# it is piped to it on the command line. This forces us to use
# shell = true and sets up a command injection vulnerability.
# So only pass a known good temporary filename to gtklp.
# Once gtklp is updated and fixed, we can
# revert to the following code:
#			cmd = cmd + tmp_file_name
#			try: subprocess.Popen([cmd], cwd=current_directory, shell=False)

			tmp_file_name2 = tempfile.NamedTemporaryFile(delete=False).name
			shutil.copyfile(tmp_file_name, tmp_file_name2)
			cmd = cmd + " < "+ tmp_file_name2			#gtklp requires pipe for filename
			try: subprocess.Popen([cmd], cwd=current_directory, shell=True)	# ugh
			except: sublime.error_message("Error launching preview/print")
		else:
			try: subprocess.Popen([cmd, tmp_file_name], cwd=current_directory, shell=False)
			except: sublime.error_message("Error launching preview/print")

	def get_lpr_options(self, how_much_to_print):
		options = getmysettings("lpr_options")
		options_list = ["-o {0}={1}".format(k, v) for k, v in options.items() if v != ""]
		options_list += ["-o {0}".format(k) for k, v in options.items() if v == ""]
		cmd = "lpr"
		cmd = [cmd] + options_list
		if how_much_to_print == "savedfile":
			cmd = cmd + [self.get_file_to_print()]
		return cmd
