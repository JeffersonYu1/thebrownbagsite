$(document).ready(function() {
    $("#custom-fields-inputs").hide();

    $("#custom-fields-check").on('click', function() {
        if ($("#custom-fields-check").is(":checked")) {
            $("#custom-fields-inputs").css("display", "block");
            for (let i = 1; i <= 4; i++) {
                let option = $("#field" + i + "-select").find(":selected").text();
                if (option != "Open-Ended" && option != "Dropdown") {
                    hideFields(i, false);
                }
            }
        }
        else {
            $("#custom-fields-inputs").hide();
        }
    });

    $("#field1-select").change(function() {fieldChange(1)});
    $("#field2-select").change(function() {fieldChange(2)});
    $("#field3-select").change(function() {fieldChange(3)});
    $("#field4-select").change(function() {fieldChange(4)});
 
});

function fieldChange(fieldNum) {
    let option = $("#field" + fieldNum + "-select").find(":selected").text();
    if (option == "Open-Ended") {
        createOpen(fieldNum);
    }
    else if (option == "Dropdown") {
        createDropdown(fieldNum);
    }
    else {
        hideFields(fieldNum, false);
    }
}

function hideFields(fieldNum, allFields) {
    if (allFields) {
        $("#field" + fieldNum + "-input-super-div").hide();
    }    

    $("#field" + fieldNum + "-input-div").hide();
    $("#field" + fieldNum + "-input-dropdown-div").hide();
    $("#field" + fieldNum + "-preview-div").hide();
    $("#field" + fieldNum + "-dropdown-preview-div").hide();
}

function createOpen(fieldNum) {
    $("#field" + fieldNum + "-input-super-div").show();
    $("#field" + fieldNum + "-input-div").show();
    $("#field" + fieldNum + "-input-dropdown-div").hide();
    $("#field" + fieldNum + "-preview-div").show();
    $("#field" + fieldNum + "-dropdown-preview-div").hide();
}

function createDropdown(fieldNum) {
    $("#field" + fieldNum + "-input-super-div").show();
    $("#field" + fieldNum + "-input-div").show();
    $("#field" + fieldNum + "-input-dropdown-div").show();
    $("#field" + fieldNum + "-preview-div").hide();
    $("#field" + fieldNum + "-dropdown-preview-div").show();
}

function dropdownPreview(e, dropdownID, defaultText) {
    let res = e.value.trim();
    let arr = [defaultText.trim()];
    if (res) {
        arr = res.split(",");
    }
    $("#" + dropdownID).empty();
    
    let contentExists = false;
    for (let i = 0; i < arr.length; i++) {
        let text = arr[i].trim();
        if (text) {
            $("#" + dropdownID).append("<option>" + arr[i].trim() + "</option>");
            contentExists = true;
        }        
    }

    if (!contentExists) {
        $("#" + dropdownID).append("<option>" + defaultText.trim() + "</option>");
    }
}

