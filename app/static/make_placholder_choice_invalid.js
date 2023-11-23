// JavaScript to make the placeholder choice invalid
// when the user submits the form without selecting a value.
// If the select field is inside a collapsible form-group
// that is hidden, the select field is ignored.

function validateForm() {
  var selectFields = document.querySelectorAll("select");
  for (var i = 0; i < selectFields.length; i++) {
    if (selectFields[i].value === "0") {
      // find the collapsible form-group
      var collapsibleFormGroup = findParentFormGroup(selectFields[i]);

      if (collapsibleFormGroup) {
        // check if the button associated with the collapsible form-group is active
        var button = document.querySelector(
          "[data-target='#" + collapsibleFormGroup.id + "']"
        );
        // if the button is not active, the collapsible form-group is hidden, so skip this select field
        if (button && !isActive(button)) {
          continue;
        }
      }

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

// Helper function to find the collapsible form-group an element belongs to
function findParentFormGroup(element) {
  var currentElement = element;
  var parentElement = currentElement.parentElement;

  while (parentElement.classList.contains("form-group")) {
    currentElement = parentElement;
    parentElement = currentElement.parentElement;
    if (
      parentElement.classList.contains("form-group") &&
      parentElement.classList.contains("collapse")
    ) {
      return parentElement;
    }
  }

  return null;
}

// Helper function to check if an element is active
function isActive(element) {
  return element.classList.contains("active");
}
