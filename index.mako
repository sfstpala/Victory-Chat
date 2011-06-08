<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" /> 
        <title>test</title>
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js"></script>
        <link href='http://fonts.googleapis.com/css?family=Ubuntu:light,lightitalic,bold' rel='stylesheet' type='text/css'>
        <style type="text/css" media="screen">
            <%include file="/index.css.mako"/>
            .button#fixed-font {
                display: none;
            }
            .button#upload-image {
                display: none;
            }
        </style>
    </head>
    <body>

    <div id="controls">
    %if logged_in:
        <div id="controls">
            <form id="control-form">
                <textarea id="message"></textarea>
                <a href="javascript:void(0)" class="button" id="send-button">Send</a>
                <a href="javascript:void(0)" class="button" id="fixed-font">Fixed Font</a>
                <a href="javascript:void(0)" class="button" id="upload-image">Upload Image</a>
            </form>
        </div>
    %else:
        <p>Please <a href="/login">log in</a> to post a message</p>
    %endif
    </div>
    <div id="sidebar">
        <h2>Room Name</h2>
        <h4>Room Description</h4>
        <small><a href="javascript:void(0)" id="sound">sound is off</a></small>
        <small><a href="javascript:void(0)" id="notifications">desktop notification are off</a></small>
        <%include file="/login.mako"/>
        <div id="user-list"></div>
        <div id="starred-list"></div>
        <div class="infobox">
            <p>Doesn't-have-a-name-yet Chat (<a href="#">FAQ</a>&nbsp;-&nbsp;<a href="#">Legal</a>)<br>
            Powered by <a href="http://www.cherrypy.org/">CherryPy</a>,
            <a href="http://www.makotemplates.org/">Mako Templates</a>,
            and <a href="http://jquery.com/">jQuery</a>.</p>
        </div>
    </div>
    <div id="page">
        <table id="chat-table"></table>
    </div>

        <div id="problem">
            <p>There seems to be problem connecting to the server -
            <a href="javascript:location.reload()">click here</a> to reload the page</p>
        </div>
    <script type="text/javascript">
<%include file="/main.js.mako"/>
    </script>
    </body>
</html>
