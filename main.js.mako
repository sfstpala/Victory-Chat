$(function () {
    var last_atime = 0;
    var is_focus = true;
    var unread = 0;
    var oldTitle = document.title;
    var soundOn = 0;
    var notificationsOn = false;
    var notificationsAllowed = false;
    var firstIteration = true;
    $(window).blur(function () {
        is_focus = false;
    }).focus(function () {
        is_focus = true;
    });
    $("#controls").hide();
    $("#controls").show(1200);
    $("html").animate({"scrollTop": $("body").height()}, 1000);
    $("body").animate({"scrollTop": $("body").height()}, 1000);
    $(".button#fixed-font").click(function () {
        $("#message").val(("    " + $("#message").val().split("\n").join("\n    ")));
    });
    $('#message').bind('keypress', function(e) {
        if(e.keyCode==13 && !e.shiftKey) {
            $("#send-button").click();
            return false;
        }
    });
    $("#sound").click(function () {
        if (soundOn == 0) {
            $("#sound").html("sound is on (for all messages)");
            soundOn = 1;
        } else {
            if (soundOn == 1) {
                $("#sound").html("sound is on (for messages to me)");
                soundOn = 2;
            } else {
                if (soundOn == 2) {
                    $("#sound").html("sound is off");
                    soundOn = 0;
                }
            }
        }
    });
    if (!window.webkitNotifications) {
        $("#notifications").hide();
    }
    $("#notifications").click(function () {
        if (notificationsOn == false) {
            window.webkitNotifications.requestPermission(function () {
                notificationsAllowed = true;
                notificationsOn = true;
                $("#notifications").html("desktop notifications are on");
                console.log(notificationsOn);
            });
            if (notificationsAllowed == true) {
                notificationsOn = true;
                $("#notifications").html("desktop notifications are on");
            }
        } else {
            notificationsOn = false;
            $("#notifications").html("desktop notifications are off");
        }
        console.log(notificationsOn);
    });

    $("#send-button").click(function () {
        $.post("/post_message", {'message': $("#message").val()});
        $("#message").val("");
    });
    (function updateLoop () {
        $.get("/read_messages", {'last_atime': last_atime}, function (response) {
            var doScroll = false;
            for (i in response) {
                doScroll = true;
                last_atime = parseFloat(response[i]['time']);
                $("#chat-table").append("<tr class=\"message-row\">" +
                    "    <td class=\"chat-username\">" +
                    "        <a href=\"/users/" + response[i]['user_id'] + "/" + response[i]['username'] +"\">" +
                    "            <img title=\"" + response[i]['username'] +"\"" +
                    "                src=\"http://www.gravatar.com/avatar/" + response[i]['emailhash'] + "?s=16&d=identicon&r=PG\" />" +
                    "        </a>" +
                    "        " + response[i]['username'] +"" +
                    "    </td>" +
                    "    <td class=\"chat-message\" id=\"" + response[i]['message_id'] + "\">" +
                    "        " + response[i]['message'] +
                    "        <span class=\"timestamp\" data-time=\"" + response[i]['time'] + "\">" +
                        ((firstIteration == true) ? response[i]['stime'] : "") + "</span>" +
                    (!response[i]['own_message'] ? ("        <a class=\"star-link\" id=\"" +
                        response[i]['message_id'] +
                        "\" href=\"javascript:void(0)\">&#x2605;</a>") : "") +
                    (!response[i]['own_message'] ? ("        <a class=\"reply-link\" data-username=\"" +
                        response[i]['username'] +
                        "\" href=\"javascript:void(0)\">&#x21A9;</a>") : "") +
                    "    </td>" +
                    "</tr>");

                if (response[i]['message_for_me'] == true) {
                    $(".chat-message#" + response[i]['message_id']).attr('style', 'background: #ffcaca');
                }
                unread = unread + 1;
                $(".star-link").click(function (event) {
                    event.stopImmediatePropagation();
                    $.post("/star_message", {'message_id': $(this).attr('id') });
                    $(this).hide('slow');
                });
                $(".reply-link").click(function (event) {
                    event.stopImmediatePropagation();
                    $("#message").focus()
                    $("#message").val($("#message").val() + "@" + $(this).attr('data-username').split(" ")[0] + " ");
                });
                if ((firstIteration == false) && (response[i]['own_message'] == false)) {
                    if ((soundOn > 0) && (response[i]['message_for_me'] == true)) {
                        (new Audio("message_for_me")).play();
                    }
                    if ((soundOn == 1) && (response[i]['message_for_me'] == false)) {
                        (new Audio("ding")).play();
                    }
                    if ((notificationsOn == true) && (response[i]['message_for_me'] == true)) {
                        console.log("notification!");
                        window.webkitNotifications.createNotification("http://www.gravatar.com/avatar/" +
                            response[i]['emailhash'] + "?s=32&d=identicon&r=PG",
                            "Message from " + response[i]['username'] + ":",
                            response[i]['raw_message']).show();
                    }
                }
            }
            firstIteration = false;
            if (doScroll == true) {
                $("html").animate({"scrollTop": $("body").height()}, 600);
                $("body").animate({"scrollTop": $("body").height()}, 600);
            }
        });
        $.get("/user_list", function (response) {
            $("#user-list").html("");
            for (i in response) {
                $("#user-list").append("            <div class=\"user-avatar\">" +
                    "<a href=\"/users/" + response[i]['user_id'] + "/" + response[i]['username'] + "\">" +
                    "<img title=\"" + response[i]['username'] + "\"" +
                    " src=\"http://www.gravatar.com/avatar/" + response[i]['emailhash'] + "?s=32&d=identicon&r=PG\" />" +
                    "</a></div>");
            }
        });
        $.get("/get_starred_messages", function (response) {
            $("#starred-list").html("");
            for (i in response) {
                $("#starred-list").append("<div class=\"starred-message\">" +
                    "<p>" + response[i][1] + "&#x2605;&nbsp;" + response[i][0]['username'] + ":&nbsp;</p><span>" +
                    response[i][0]['message'] + "</span></div>");
            }
        });
        if ($("#message").val().indexOf("\n") != -1) {
            $(".button#fixed-font").show('slow');
        } else {
            $(".button#fixed-font").hide('slow');
        }
        if ((is_focus == false) && (parseInt(unread) > 0)) {
            document.title = oldTitle + " (" + parseInt(unread) + ")";
        } else {
            document.title = oldTitle;
            unread = 0;
        }
        $(".timestamp").html(function () {
            NAMES = [[["seconds", "second"], 60],
                 [["minutes", "minute"], 60], [["hours", "hour"], 24], [["days", "day"], 7],
                 [["weeks", "week"], 4], [["months", "month"], 12], [["years", "year"], 1]
            ];
            u = ((new Date).getTime() / 1000)  - (parseFloat($(this).attr('data-time')));
            for (i in NAMES) {
                if (u < NAMES[i][1])
                    break;
                else
                    u /= NAMES[i][1];
            }
            var result = String(String(Math.floor(u)) + " " +
                String(parseInt(u) == 1 ? NAMES[i][0][1] : NAMES[i][0][0]) + 
                " ago");
            if (result.indexOf("second") != -1) {
                return "";
            } else {
                return result.replace("1 day ago", "Yesterday");
            }
        });
        setTimeout(updateLoop, 1000);
    })();
    $(document).ajaxError(function () {
        $("#problem").show('slow');
        setTimeout(function () {
            location.reload();
        }, 5000);
    });
});
