// JavaScript to make the placeholder choice invalid
// when the user submits the form without selecting a value.

function validateForm() {
  var selectFields = document.querySelectorAll("select");
  for (var i = 0; i < selectFields.length; i++) {
    if (selectFields[i].value === "0") {
      alert("Please select a value for all fields.");
      // color the select field red
      selectFields[i].style.backgroundColor = "#ffcccc";
      // remove the color after a timeout
      setTimeout(function () {
        selectFields[i].style.backgroundColor = "";
      }, 3000);
      // redirect focus back to the select field
      selectFields[i].focus();
      return false; // Prevent form submission
    }
  }
  return true; // Allow form submission
}
