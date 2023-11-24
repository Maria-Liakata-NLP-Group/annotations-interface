// Function to toggle an additional form group for each label for client annotations
// It also makes the evidence field compulsory when the form group is visible

function toggleAdditionalFormGroup(buttonId, formGroupId, evidenceId) {
  $(buttonId).click(function () {
    $(formGroupId).toggle();
    if ($(this).hasClass("active")) {
      // if the toggle button is active...
      $(this).removeClass("active");
      // make the evidence field optional when the form group is hidden
      $(evidenceId).prop("required", false);
    } else {
      // if the toggle button is not active...
      $(this).addClass("active");
      // make the evidence field compulsory when the form group is visible
      $(evidenceId).prop("required", true);
    }
  });
}

$(document).ready(function () {
  // call the function for the client labels
  toggleAdditionalFormGroup(
    "#btn_client_label_a_add",
    "#client_label_a_add",
    "#evidence_a_client_add"
  );
  toggleAdditionalFormGroup(
    "#btn_client_label_b_add",
    "#client_label_b_add",
    "#evidence_b_client_add"
  );
  toggleAdditionalFormGroup(
    "#btn_client_label_c_add",
    "#client_label_c_add",
    "#evidence_c_client_add"
  );
  toggleAdditionalFormGroup(
    "#btn_client_label_d_add",
    "#client_label_d_add",
    "#evidence_d_client_add"
  );
  toggleAdditionalFormGroup(
    "#btn_client_label_e_add",
    "#client_label_e_add",
    "#evidence_e_client_add"
  );

  // call the function for the therapist labels
  toggleAdditionalFormGroup(
    "#btn_therapist_label_a_add",
    "#therapist_label_a_add",
    "#evidence_a_therapist_add"
  );
});
