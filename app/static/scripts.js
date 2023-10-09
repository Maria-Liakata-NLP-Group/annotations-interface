// Function to show/hide client, therapist and dyad annotation forms at segment level
$(document).ready(function () {
$("#btn_client").on("click", function () {
    if ($(this).hasClass("active")) {
    // Button is already active, so deactivate it
    $("#form_client").collapse("hide"); // Hide client form
    $(this).removeClass("active"); // Remove active class from client button
    } else {
    // Button is not active, so activate it
    $("#form_therapist").collapse("hide"); // Hide therapist form
    $("#form_dyad").collapse("hide"); // Hide dyad form
    $("#form_client").collapse("show"); // Show client form
    $("#btn_therapist").removeClass("active"); // Remove active class from therapist button
    $("#btn_dyad").removeClass("active"); // Remove active class from dyad button
    $(this).addClass("active"); // Add active class to client button
    }
});
$("#btn_therapist").on("click", function () {
    if ($(this).hasClass("active")) {
    // Button is already active, so deactivate it
    $("#form_therapist").collapse("hide"); // Hide therapist form
    $(this).removeClass("active"); // Remove active class from therapist button
    } else {
    // Button is not active, so activate it
    $("#form_client").collapse("hide"); // Hide client form
    $("#form_dyad").collapse("hide"); // Hide dyad form
    $("#form_therapist").collapse("show"); // Show therapist form
    $("#btn_client").removeClass("active"); // Remove active class from client button
    $("#btn_dyad").removeClass("active"); // Remove active class from dyad button
    $(this).addClass("active"); // Add active class to therapist button
    }
});
$("#btn_dyad").on("click", function () {
    if ($(this).hasClass("active")) {
    // Button is already active, so deactivate it
    $("#form_dyad").collapse("hide"); // Hide dyad form
    $(this).removeClass("active"); // Remove active class from dyad button
    } else {
    // Button is not active, so activate it
    $("#form_client").collapse("hide"); // Hide client form
    $("#form_therapist").collapse("hide"); // Hide therapist form
    $("#form_dyad").collapse("show"); // Show dyad form
    $("#btn_client").removeClass("active"); // Remove active class from client button
    $("#btn_therapist").removeClass("active"); // Remove active class from therapist button
    $(this).addClass("active"); // Add active class to dyad button
    }
});
});
