body {
    font-family: 'Ubuntu', sans-serif;
    font-size: 11px;
    background: url(/background);
}
* {
    font-weight: inherit;
    color: black;
}
#login {
    background: #222;
    opacity: 0.9;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 100;
}
#login #login-hide {
    position: absolute;
    top: 2px;
    right: 2px;
    width: 16px;
    padding: 16px;
    height: 12px;
    text-decoration: none;
}
#login #login-hide:hover {
    color: #ccc;
}
#login form {
    opacity: 0.9;
    position: fixed;
    background: #fff;
    width: 256px;
    height: 256px;
    top: 50%;
    left: 50%;
    margin-top: -160px;
    margin-left: -160px;
    padding: 32px;
    border-radius: 8px;
    box-shadow: 1px 1px 16px #000;
}
#login form * {
    font-family: 'Ubuntu', sans-serif;
    font-size: 11px;
}
#login form h2 {
    margin-bottom: 16px;
    font-size: 17px;
}
#login form input.text {
    width: 248px;
    border: 1px solid #ccc;
    border-radius: 3px;
    margin-top: 4px;
    padding: 4px;
}
#login form input[type="submit"] {
    width: 96px;
    margin: 12px 0 0 -1px;
    padding: 2px;
}
#login form .error {
    font-weight: bold;;
}
#controls {

    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 96px;
    background: #eee; /* for non-css3 browsers */
    background: -webkit-gradient(linear, left top, left bottom, from(#f7f7f7), to(#eee));
    background: -moz-linear-gradient(top,  #f7f7f7, #eee);
    box-shadow: 0 0 8px #ccc;
    z-index: 1;
}
#controls textarea {
    width: 40%;
    height: 60px;
    margin: 16px;
    margin-left: 12px;
    float: left;
    border: 1px solid #999;
    border-radius: 4px;
    box-shadow: 0 0 1px #444;
}
#controls .button {
    padding: 4px;
    width: 96px;
    height: 16px;
    text-align: center;
    line-height: 16px;
    text-decoration: none;
    border: 1px solid #999;
    float: left;
    box-shadow: 0 0 1px #444;
    margin-top: 56px;
    margin-right: 16px;
    border-radius: 4px;
    background: #eee; /* for non-css3 browsers */
    background: -webkit-gradient(linear, left top, left bottom, from(#f7f7f7), to(#ccc));
    background: -moz-linear-gradient(top,  #f7f7f7, #eee);
}
#controls .button:hover {
    background: -webkit-gradient(linear, left top, left bottom, from(#f7f7f7), to(#ddd));
    background: -moz-linear-gradient(top,  #fff, #eee);
}
#controls .button:active {
    background: -webkit-gradient(linear, left top, left bottom, from(#ccc), to(#f7f7f7));
    background: -moz-linear-gradient(top,  #eee, #f7f7f7);
}
#controls p {
    margin-left: 36px;
    line-height: 72px;
}
#sidebar {
    position: fixed;
    right: 0;
    top: 0;
    width: 320px;
    height: 100%;
    padding-bottom: 96px;
    overflow: hidden;
}
#sidebar #user-list {
    display: block;
}
#sidebar #starred-list {
    clear: both;
    padding-top: 12px;
}
#sidebar #starred-list p {
    display: inline;
    top: 8px;
}
#sidebar #starred-list span {
}
#sidebar .user-avatar {
    float: left;
    border: 1px solid #fff;
    height: 32px;
}
#sidebar h2 {
    margin-bottom: -16px;
}
#page {
    margin-right: 320px;
    padding-bottom: 96px;
    z-index: 1;
}
#page table {
    border-collapse: separate; 
    border-spacing: 6px;
    margin-bottom: 24px;
}
td.chat-username {
    display: inline-block;
    vertical-align: top;
    padding-top: 8px;
    width: 96px;
    line-height: 17px;
}
td.chat-username a {
    text-decoration: none;
}
td.chat-username img {
    margin-right: 4px;
}
td.chat-username img:hover {
    outline: 1px solid #ccc;
}
td.chat-message {
    background: #f4f4f4;
    width: 100%;
    border-radius: 8px;
}
tr:nth-child(even) td.chat-message {
    background: #eaeaea;
}
td.chat-message p {
    float: left;
    display: inline;
    margin: 8px;
}
td.chat-message pre {
    float: left;
    display: inline;
    margin: 8px;
}
td.chat-message strong {
    font-weight: bold;
}
td.chat-message img {
    width: 240px;
    max-height: 320px;
}
#sidebar #starred-list img {
    max-width: 64px;
    max-height: 64px;
    text-decoration: none;
    background: #fff:
}
td.chat-message .star-link {
    color: #ccc;
    float: right;
    text-decoration: none;
    padding: 8px;
}
td.chat-message:hover .star-link {
    color: #999;
}
td.chat-message .star-link:hover {
   color: #000;
}
td.chat-message .reply-link {
    color: #ccc;
    float: right;
    text-decoration: none;
    padding: 8px;
}
td.chat-message:hover .reply-link {
    color: #999;
}
td.chat-message .reply-link:hover {
   color: #000;
}
td.chat-message .timestamp {
    float: right;
    background: #fff;
    border-radius: 2px;
    margin: 8px;
    padding: 0 2px 0 2px;
    opacity: 0.4;
}
td.chat-message:hover .timestamp {
    opacity: 1;
}
.own-message td.chat-message {
    background: #aaa;
}
#starred-list .starred-message p {
    display: inline;
    padding: 4px;
}
 #starred-list .starred-message {
    background: #f7f7f7;
    width: 90%;
    border-radius: 8px;
    padding: 8px;
    margin-bottom: 8px;
}
.infobox {
    position: fixed;
    right: 16px;
    bottom: 0;
    z-index: 10;
    font-size: smaller;
    text-align: right;
}
.infobox * {
    color: #000;
}
a:hover {
    color: #555;
}
#problem {
    opacity: 0.9;
    display: none;
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    height: 64px;
    background: #eee; /* for non-css3 browsers */
    background: -webkit-gradient(linear, left top, left bottom, from(#f7f7f7), to(#eee));
    background: -moz-linear-gradient(top,  #f7f7f7, #eee);
    box-shadow: 0 0 8px #ccc;
}
#problem p {
    margin-left: 32px;
    line-height: 32px;
    font-size: 15px;
}
