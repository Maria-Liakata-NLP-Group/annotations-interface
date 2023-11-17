// JavaScript to dynamically update the choices of a second select field
// based on the choice of another select field. If the updated choices are
// empty, the second select field is not required.

$(document).ready(function () {
  // find all select fields with the class "dynamic_select"
  $(".dynamic_select").each(function () {
    var firstSelect = $(this);
    var firstSelectName = firstSelect.attr("name");
    var targetId = firstSelect.data("target");
    var secondSelect = $("#" + targetId);

    firstSelect.on("change", function () {
      var selectedValue = firstSelect.val(); // get the selected value from the first select field
      // make an AJAX request to the server to get the updated
      // choices for the second select field
      $.ajax({
        url: "/annotate/_update_select_choices",
        type: "POST",
        data: {
          select_field_name: firstSelectName,
          selected_value: selectedValue,
        },
        success: function (data) {
          // if the updated choices are empty, the second select field is not required
          if (data.options) {
            secondSelect.prop("required", true);
          } else {
            secondSelect.prop("required", false);
          }
          // update the second select field with the new choices
          secondSelect.html(data.options);
        },
      });
    });
  });
});
