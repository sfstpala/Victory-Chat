<%
    if not logged_in:
        if 'login_error' in session and session['login_error'] == "username":
            error = "Invalid Username"
        elif 'login_error' in session and session['login_error'] == "password":
            error = "Invalid Password"
        elif 'login_error' in session and session['login_error'] == "username_taken":
            error = "We already have a user by this name"
        elif 'login_error' in session and session['login_error'] == "email_taken":
            error = "We already have a user with this email address"
        elif 'login_error' in session and session['login_error'] == "no_password":
            error = "You have to choose a password"
        else:
            error = ""
        context.write(
    """<p id="login-show"><a id="login-show-link" href="/login">Login</a></p>
<div id="login"><form id="login-form" action="/do_login" method="post">
    <h2 id="login-header">Please log in:</h2>
    <a href="/" id="login-hide">&#x25B4;</a>
    <span class="error">%s</span><br />
    <input class="text" id="username" type="text" name="username" value="username" /><br />
    <input class="text" id="email" type="text" name="email" value="email@example.com" /><br />
    <input class="text" id="password" type="password" name="password" value="password" /><br />
    <input type="submit" id="login-button" value="Log In"/>&nbsp;
    <a href="javascript:void(0)" id="guest-login">I don't want to</a></p>
    <a href="javascript:void(0)" id="register">Register a new account</a></p>
<div id="guest-login-form">
    <p>Do you want to log in as a guest?<br />
    You'll be missing out on cool features!<br />
    <a id="guest-yes" href="javascript:void(0)">yes</a>
</div>
</form>
</div>
<script type="text/javascript">
    $(function () {
        %s
        $(".error").show('slow');
        setTimeout(function () { $(".error").animate({'opacity': 'show'}, 'fast'); }, 200);
        setTimeout(function () { $(".error").animate({'opacity': 'hide'}, 'fast'); }, 400);
        setTimeout(function () { $(".error").animate({'opacity': 'show'}, 'fast'); }, 550);
        $("#guest-login-form").hide();
        $("#guest-login").click(function () {
            $("#guest-login").animate({'opacity': 'hide'}, "slow");
            setTimeout(function () {
                $("#guest-login-form").animate({'opacity': 'show'}, "slow");
            }, 610);
        });
        $("#login-form").submit(function () {
            $("#login-form").hide('fast');
            return true;
        });
        $("#guest-yes").click(function () {
            $("#username").val("guest");
            $("#password").val("");
            $("#login-form").submit();
        });
        $("#login-hide").click(function () {
            $("#login-show").animate({'opacity': 'show'}, 'fast');
            $("#login").animate({'opacity': 'hide'}, 'slow');
            $("#login-form").animate({'height': 'hide'}, 'fast');
            $.get("login_skipped", function (response) {});
            window.history.pushState("", window.title, "/");
        });
        $("#login-show-link").click(function () {
            window.history.pushState("", window.title, "/login");
            $("#login-show").animate({'opacity': 'hide'}, 'fast');
            $("#login").animate({'opacity': 'show'}, 'slow');
            $("#login-form").animate({'height': 'show'}, 'fast');
        });
        $("#email").hide();
        $("#register").click(function () {
            window.history.pushState("", window.title, "/register");
            $(".error").show();
            $("#email").show();
            $("#register").hide();
            $("#login-button").val("Register");
            $("#login-header").html("Tell us something about yourself");
            $("#guest-login").hide();
            $("#login-form").get(0).setAttribute('action', '/do_register')
        });
    });
</script>""" % (error, """$("#login-show").show();$("#login").hide();"""
    if 'login_skipped' in session else """$("#login-show").hide();window.history.pushState("",
        window.title, "/login");"""))
    elif logged_in:
        context.write(
    """<p id="logged-in">Logged in as <a href="/users/%s/%s">%s</a> (<a href="/logout">Log out</a>)</p>""" %
        (session['user_id'], session['username'], session['username']))
    if 'register' in session and session['register'] and not 'login_skipped' in session:
        context.write("""<script type="text/javascript">$(function(){$("#register").click();});</script>""")
%>
