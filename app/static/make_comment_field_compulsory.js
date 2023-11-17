// JavaScript to make the comment field compulsory if the user selects
// "Other" in its data target select field.

$(document).ready(function () {
  // find all text ara field with the class "comment_field"
  $(".comment_field").each(function () {
    var commentField = $(this);
    var commentFieldName = commentField.attr("name");
    var targetId = commentField.data("target");
    var targetSelect = $("#" + targetId);

    targetSelect.on("change", function () {
      // get the label of the selected value
      var selectedLabel = targetSelect.find("option:selected").text();
      // if the selected value is "Other", the comment field is required
      if (selectedLabel === "Other") {
        commentField.prop("required", true);
        // TODO: set custom validation message
      } else {
        commentField.prop("required", false);
      }
    });
  });
});
