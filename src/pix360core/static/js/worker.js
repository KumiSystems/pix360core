$("#options").hide();

$body = $("body");

var intervals = {};

function toggleOptions() {
  $("#options").toggle();
}

function lockform() {
  $("#theform :input").prop("disabled", true);
  $body.addClass("loading");
}

function unlockform() {
  $("#theform :input").prop("disabled", false);
  $body.removeClass("loading");
}

function deletecard(jobid) {
  if ($("#" + jobid).length) {
    $("#" + jobid).remove();
    $.ajax({
      type: "GET",
      url: "/delete/" + jobid,
    });
  }
}

function checkServerForFile(jobid, title, interval) {
  $.ajax({
    type: "GET",
    cache: false,
    url: "/status/" + jobid,
    statusCode: {
      403: function () {
        Notification.requestPermission(function (permission) {
          if (permission === "granted") {
            var notification = new Notification("PIX360", {
              body: "Your session has expired. Please log in again.",
            });
          }
        });
        window.location.href = "/";
      },
      404: function () {
        clearInterval(intervals[jobid]);
        failcard(jobid, title);
        return;
      },
      200: function (data, tstatus, xhr) {
        if (data.status == "completed") {
          clearInterval(intervals[jobid]);
          finishcard(jobid, title, data.content_type == "video/mp4");
          return;
        } else if (data.status == "failed") {
          clearInterval(intervals[jobid]);
          failcard(jobid, title);
          return;
        }
      },
      500: function () {
        clearInterval(intervals[jobid]);
        failcard(jobid, title);
        return;
      },
    },
  });
}

function addcard(jobid, title) {
  var text =
    '<div class="col-sm-3" id="' +
    jobid +
    '"> <div class="card"> <img class="card-img-top img-fluid" src="/static/img/spinner.gif" alt="Creating Image"><div style="text-align: center; font-weight: bold;" class="card-block">' +
    title +
    "</div> </div> </div>";
  $("#cards").append(text);
  $("html,body").animate({ scrollTop: $("#" + jobid).offset().top });
}

function restartconversion(jobid, title) {
  $.ajax({
    type: "GET",
    url: "/retry/" + jobid,
    success: function (msg) {
      var interval = setInterval(checkServerForFile, 3000, msg.id, title);
      intervals[msg.id] = interval;
      addcard(msg.id, title);
    },
  });
}

function failcard(jobid, title) {
  Notification.requestPermission(function (permission) {
    if (permission === "granted") {
      var notification = new Notification("PIX360", {
        body: title + ": Export failed.",
      });
    }
  });
  var text =
    '<div class="card"> <div style="text-align: center; color: red; font-weight: bold;" class="card-block">' +
    title +
    ': Export failed.</div><div style="text-align: center;" class="card-block"><a style="color: white;" onclick="restartconversion (\'' +
    jobid +
    "', '" +
    title +
    '\');" class="btn btn-info">Retry</a> <a style="color: white;" onclick="deletecard(\'' +
    jobid +
    '\');" class="btn btn-danger">Hide</a></div> </div>';
  $("#" + jobid).html(text);
}

function finishcard(jobid, title, video) {
  Notification.requestPermission(function (permission) {
    if (permission === "granted") {
      var notification = new Notification("PIX360", {
        body: title + ": Export finished.",
      });
    }
  });
  var text =
    '<div class="card"> <' +
    (video ? "video controls" : "img") +
    ' class="card-img-top img-fluid" download src="/download/' +
    jobid +
    '" alt="Final ' +
    (video ? "Video" : "Image") +
    '">' +
    (video ? "</video>" : "") +
    '<div style="text-align: center; font-weight: bold;" class="card-block">' +
    title +
    '</div> <div style="text-align: center; color: white;" class="card-block"><a style="color: white;" onclick="restartconversion(\'' +
    jobid +
    "', '" +
    title +
    '\');" class="btn btn-info">Retry</a> <a href="/download/' +
    jobid +
    '" class="btn btn-primary">Download</a> <a onclick="deletecard(\'' +
    jobid +
    '\');" class="btn btn-danger">Hide</a> </div> </div>';
  $("#" + jobid).html(text);

  $("#" + jobid + " img").on("click", function () {
    imgurl = $(this).attr("src");
    pannellum.viewer("panorama", {
      type: "equirectangular",
      panorama: imgurl + "/3840/1920/",
      autoLoad: true,
    });
    $("#panoramaModal").modal("show");
  });
}

$("#theform").submit(function (event) {
  event.preventDefault();
  if (this.checkValidity()) {
    $.ajax({
      type: "POST",
      url: "/start",
      data: $("#theform").serialize(),
      success: function (msg) {
        var title = $("#title").val() ? $("#title").val() : "No title";
        var interval = setInterval(checkServerForFile, 3000, msg.id, title);
        intervals[msg.id] = interval;
        addcard(msg.id, title);
      },
    });
  }
});

function initialize() {
  $.ajax({
    type: "GET",
    url: "/list",
    success: function (msg) {
      for (var i = 0; i < msg["conversions"].length; i++) {
        var job = msg["conversions"][i];
        if (job.status >= 0) {
          var title = job.title ? job.title : "No title";
          addcard(job.id, title);
          var interval = setInterval(checkServerForFile, 3000, job.id, title);
          intervals[job.id] = interval;
        }
      }
    },
  });
}

$(document).ready(function () {
  if (Notification.permission !== "granted") {
    Notification.requestPermission();
  }
  initialize();
});
