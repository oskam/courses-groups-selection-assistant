"use strict";
function getCheckboxes(formGroupDiv) {
    return Array.from(formGroupDiv.querySelectorAll("div label"));
}
function setClickCallbackFor(element, callback, callbackArgs) {
    element.addEventListener("click", () => {
        callback(...callbackArgs);
    });
}
let weekdaysDivs = new Array(5);
let weekdaysLabels = new Array(5);
let postButton;
function togglePeriods(mainInput, inputs) {
    inputs.forEach((input) => {
        input.checked = mainInput.checked;
    });
}
function toggleAllDay(sourceInput, mainInput) {
    if (!sourceInput.checked) {
        mainInput.checked = false;
    }
}
function disablePeriodsOnClick(weekdaysLabels) {
    weekdaysLabels.forEach((labels) => {
        let mainInput = labels[0].querySelector("input");
        let otherInputs = labels.slice(1).map(l => l.querySelector("input"));
        if (mainInput !== null) {
            setClickCallbackFor(mainInput, togglePeriods, [mainInput, otherInputs]);
            otherInputs.forEach((input) => {
                setClickCallbackFor(input, toggleAllDay, [input, mainInput]);
            });
        }
    });
}
function addLoader() {
    let newDiv = document.createElement('div');
    newDiv.className = 'loader';
    document.body.appendChild(newDiv);
}
document.onreadystatechange = () => {
    if (document.readyState === 'complete') {
        for (let i = 0; i < 5; i++) {
            weekdaysDivs[i] = document.querySelector("#id_3-" + i) || new Element();
            weekdaysLabels[i] = getCheckboxes(weekdaysDivs[i]);
        }
        disablePeriodsOnClick(weekdaysLabels);
        postButton = document.querySelector("#final") || new HTMLButtonElement();
        setClickCallbackFor(postButton, addLoader, []);
    }
};
