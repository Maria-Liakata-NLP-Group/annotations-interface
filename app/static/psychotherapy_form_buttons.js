$(document).ready(function () {
  $("#btn_client").on("click", function () {
    var url = $(this).attr("form-url");
    window.location.href = url; // Redirect to client form
    $("#btn_therapist").removeClass("active"); // Remove active class from therapist button
    $("#btn_dyad").removeClass("active"); // Remove active class from dyad button
    $(this).addClass("active"); // Add active class to client button
  });
  $("#btn_therapist").on("click", function () {
    var url = $(this).attr("form-url");
    window.location.href = url; // Redirect to therapist form
    $("#btn_client").removeClass("active"); // Remove active class from client button
    $("#btn_dyad").removeClass("active"); // Remove active class from dyad button
    $(this).addClass("active"); // Add active class to therapist button
  });
  $("#btn_dyad").on("click", function () {
    var url = $(this).attr("form-url");
    window.location.href = url; // Redirect to dyad form
    $("#btn_client").removeClass("active"); // Remove active class from client button
    $("#btn_therapist").removeClass("active"); // Remove active class from therapist button
    $(this).addClass("active"); // Add active class to dyad button
  });
});
