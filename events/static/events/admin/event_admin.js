document.addEventListener("DOMContentLoaded", function () {
    const eventTypeField = document.getElementById("id_event_type");
    const customEventTypeRow = document.getElementById("id_custom_event_type").closest(".form-row, .mb-3, .field-custom_event_type") || document.getElementById("id_custom_event_type").closest("div");

    function toggleCustomField() {
        if (!eventTypeField || !customEventTypeRow) return;

        if (eventTypeField.value === "outro") {
            customEventTypeRow.style.display = "";
        } else {
            customEventTypeRow.style.display = "none";
            document.getElementById("id_custom_event_type").value = "";
        }
    }

    toggleCustomField();
    eventTypeField.addEventListener("change", toggleCustomField);
});