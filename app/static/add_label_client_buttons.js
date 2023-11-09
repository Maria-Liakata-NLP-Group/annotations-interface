// Function to toggle an additional form group for each label for client annotations
$(document).ready(function () {
  $("#btn_client_label_a_add").click(function () {
    $("#client_label_a_add").toggle();
    if ($(this).hasClass("active")) {
      $(this).removeClass("active");
    } else {
      $(this).addClass("active");
    }
  });
  $("#btn_client_label_b_add").click(function () {
    $("#client_label_b_add").toggle();
    if ($(this).hasClass("active")) {
      $(this).removeClass("active");
    } else {
      $(this).addClass("active");
    }
  });
  $("#btn_client_label_c_add").click(function () {
    $("#client_label_c_add").toggle();
    if ($(this).hasClass("active")) {
      $(this).removeClass("active");
    } else {
      $(this).addClass("active");
    }
  });
  $("#btn_client_label_d_add").click(function () {
    $("#client_label_d_add").toggle();
    if ($(this).hasClass("active")) {
      $(this).removeClass("active");
    } else {
      $(this).addClass("active");
    }
  });
  $("#btn_client_label_e_add").click(function () {
    $("#client_label_e_add").toggle();
    if ($(this).hasClass("active")) {
      $(this).removeClass("active");
    } else {
      $(this).addClass("active");
    }
  });
});
