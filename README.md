# SublimePreviewAndPrint
Preview and Print for Sublime Text 3

This plugin previews and prints from Sublime Text. It is evoked with a key binding 
(ctrl+p), from the File menu, from the right click context menu, or from the command palette.

If you have selected one or more blocks of text when PreviewAndPrint is triggered, only 
the selected blocks of text will be previewed or printed. (You can change this behavior 
in the user configuration file.)

At the lowest level, you can configure this plugin to do nothing more than send text directly 
to a printer via lpr. At the next level, a standard dialog box allows you to choose a printer, 
page range, single vs duplex, etc. Additional options allow a feature-rich preview of your 
document via evince or okular. Finally, if you enable formatting/conversion 
options, you can apply fonts, margins, word-wrap, headers, etc to printed text, and syntax 
color highlighting for code. Working with markdown files, you can preview and print latex 
formatted documents as well. (The latter depends on a working installation of pandoc and latex.)

The following summarizes PreviewAndPrint's options and the external programs you should install 
to enable each option.

 - Send unformatted text direct to a printer: Requires lpr.
 - Display a standard dialog box for choosing a printer, duplex vs single sided, sheets per page, 
 	etc: Requires gtklp or xpp. (No need to install gtklp or xpp if you use one of the viewers below.)
 - Full page preview. Requires evince or okular. (xpdf or acroread also work for markdown.)
 - Formatting of text documents or syntax highlighting of code: Needs enscript to create a temporary 
 	formatted postscript version of your document. 
 - Formatting of markdown documents: Pandoc with latex, context or wkhtmltopdf. A temporary copy of 
 	your document will be converted to pdf.

Which viewer program - okular, evince, xpdf, acroread - should you use for page preview? The simplest
answer is okular, since it can work with all the (temporary) formats PreviewAndPrint creates: text, 
postscript, pdf. A more detailed answer is: If you have not enabled formatting, then you need a viewer
that can display raw text: okular. If you have enabled formatting of text documents or highlighted code 
with enscript, then you need a viewer that can preview postscript files: evince or okular. If you will 
be formatting markdown documents, then you need a viewer that can display pdf files: okular, evince, 
xpdf, or acroread. If you will be formatting both markdown and text documents then you need a viewer 
that can display postscript and pdf: okular or enscript. Whichever viwer program you use, select 
File-> Print from the viewer's main menu when you are ready to select print options and send your 
document to the printer.

Use the "postscript_options" section of the configuration file to set fonts, margins, headers, etc for 
your printed output. If you are going to be printing blocks of code - rather than just prose - enscript 
can apply (color) code highlighting to many of Sublime Text's syntaxes. From the command line, 

     "enscript --help-highlight" 

will display a list of all the languages enscript knows about. If enscript can highlight your language, 
place the language name in the "postscript_options" "highlight" field. For example, 

     "highlight" : "python"

Other helpful settings are "color" : "1"  and "line-numbers" : "1". 

Once you have settled on highlighting and other postscript options, these become the default for 
everything you preview or print that passes first through the enscript converter. This can be annoying 
however if sometimes you want to print plain text documents in addition to color highlighted code. (Most 
people do not want syntax formatting applied to plain text.) To deal with this situation, you can define 
a second set of postscript conversion options that apply to plain text rather than code. 

	"secondary_postscript_syntax_override": "plain text"

When you preview/print plain text files, PreviewAndPrint will pass enscript your "secondary_postscript_options" 
rather than the options you have defined for your primary coding language. This gives you a default configuration 
for your primary coding language, and a secondary configuration for plain text. (A third set of configuration 
options is available for markdown/latex files.)

So far, this plugin has been tested primarily under Linux. For Windows, you must specify the full paths for any external 
programs listed in the configuration file. For evince, for example, you would need something like this:

	"c:\Users\[username]\AppData\Local\Apps\Evince-2.32.0\bin\evince.exe" 

After you install one of these programs in Windows, you can search for its full path using the "where" command 
line utility. Paste the full path/filename into the configuration file.


Anticipated frequently asked questions:

Q: I can't install enscript or pandoc on my system but I still want to use print preview. What do I do?
A: You need a viewer that can work with raw text files. First, install okular. Then, in the configuration file, set

	"skip_conversion" : True 

and: 

	"previewer/printer" : "okular". 


Q: I don't need to preview my files but I would like to use a standard dialog box to select a printer, choose duplex 
vs single-sided, etc. What do I do? 
A: First install a cups or lpr front end on your system such as xpp or gtklp. Then specify the front end in the 
configuration file. For example, 

	"previewer/printer" : "gtklp",

Q: I just want to get my text to the printer in the simplest possible way, without any formatting, previewing or 
dialog boxes. What do I do?
A: First, in the configuration file set 

	"send_directly_to_printer" : true. 

Then make sure lpr is working on your system.

Q: I am using pandoc with latex for formatting my document. When I preview an entire document it looks fine, but when 
I preview selected blocks of text the formatting is incorrect. What do I do?
A: If you have a YAML header block at the start of your document it will not be included when you preview/print a 
selection unless:

> 1) You include the YAML block as the first of your selections. 

OR 

> 2) You make a copy  of your YAML header and place it in a stand-alone file. Then use configuration options to tell PrintAndPreview to include the YAML block when dealing with selected blocks of text:

	"yaml_header_injection" : true,
	"yaml_header_include_file_location" : "{path to YAML block}"


Q: Why doesn't SublimeText include its own native print capability?
A: Hmm. The goal of PreviewAndPrint is to function close enough to what most people need so that the lack of native 
printing capabilities is no longer a serious impediment. I would very much appreciate feedback on how well this goal 
is accomplished here, bug reporting, as well as suggestions for added features.

Acknowledgments: This plugin owes much to SublimePrint.py and Pandoc.py. The errors (and clunky coding) are all my own.
