
def writeHtmlTemplate(title, content):
	html = ''
	#html = 'Content-type:  text/html\n\n'
	html = "<html><title>" + title + "</title>"

	html += '''
<head>
	<link REL="SHORTCUT ICON" HREF="/favicon.ico">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta property="og:title" content="grabfile: Easy file sharing"/>
	<meta property="og:description" content="Easy file sharing for everyone"/>
	<meta property="og:url" content="http://something.org/"/>
	<meta property="og:locale" content="en_US"/>
	<link rel="stylesheet" href="/static/style.css" type="text/css" charset="utf-8"/>
</head>
<div class="container">
<div id="header">
	<div class="wrapper">
	<div id="logo">
		<a href="http://localhost:5000/">
			<img src="/static/grabfile_logo_64.png" alt="grabfile logo" title="grabfile"/>
			<img src="/static/grabfile_name_white_64.png" alt="grabfile logo" title="grabfile"/>
		</a>
	</div>
	<div id="menu">
		<ul class="navigation">
			<li><a class="piwik_link" href="/">Home</a></li>
			<li><a class="piwik_link" href="/">Upload</a></li>
			<li><a class="piwik_link" href="#download">My Files</a></li>
			<li><a class="piwik_link" href="#gallery">Gallery</a></li>
			<li><a class="piwik_link" href="/about">About</a></li>
			<li><a class="piwik_link" href="/logout">logout</a></li>
		</ul>
	</div>
	</div> <!-- end of wrapper -->
</div> <!-- end of header -->
	'''

	html += '''
<div id="content">
	<!-- global wrapper -->
	<div class="wrapper">
	    <div style="clear: both;"></div>	
		<div class="panel" id="panel-aboutus">
	'''
	html += '<h2>' + title + '</h2><p>' + content + '''
			</p>
	    	<div style="clear: both;"></div>	
		</div>
	</div> <!-- end of wrapper -->
</div> <!-- end of content -->
	'''

	html += '''
<div id="footer">
	<div class="wrapper">
		<div class="col1">
			<p>
				<a href="https://github.com/AlanKK/grabfile">Project home</a>
			</p>
			<p>
				<a href="https://github.com/AlanKK/grabfile">Report a bug</a>
			</p>
		</div>
		<div class="col2">
			<p>
				<a href="mailto:<enter siteadmin email>">Contact</a>
			</p>
		</div>
	</div>
	<div style="clear: both;"></div>
</div>
</div> <!-- end of container -->
	'''
	html += '</html>'

	return html



