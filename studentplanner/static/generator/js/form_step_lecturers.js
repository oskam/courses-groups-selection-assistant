"use strict";
function getCheckboxes(formGroupDiv) {
    return Array.from(formGroupDiv.querySelectorAll("div label"));
}
function setClickCallbackFor(element, callback, callbackArgs) {
    element.addEventListener("click", () => {
        callback(...callbackArgs);
    });
}
let lovedLecturersDiv;
let hatedLecturersDiv;
let lovedLecturersLabels;
let hatedLecturersLabels;
function toggleDisabled(label, input) {
    if (input.disabled) {
        label.classList.remove('crossed-out');
    }
    else {
        label.classList.add('crossed-out');
    }
    input.disabled = !input.disabled;
}
function disableOppositeOnClick(labelPairs) {
    labelPairs.forEach(([label1, label2]) => {
        let input1 = label1.querySelector("input");
        let input2 = label2.querySelector("input");
        if (input1 !== null && input2 !== null) {
            setClickCallbackFor(input1, toggleDisabled, [label2, input2]);
            setClickCallbackFor(input2, toggleDisabled, [label1, input1]);
        }
    });
}
document.onreadystatechange = () => {
    if (document.readyState === 'complete') {
        lovedLecturersDiv = document.querySelector("#id_2-loved_lecturers") || new Element();
        hatedLecturersDiv = document.querySelector("#id_2-hated_lecturers") || new Element();
        lovedLecturersLabels = getCheckboxes(lovedLecturersDiv);
        hatedLecturersLabels = getCheckboxes(hatedLecturersDiv);
        const labelPairs = lovedLecturersLabels.map((l, i) => [l, hatedLecturersLabels[i]]);
        disableOppositeOnClick(labelPairs);
    }
};
