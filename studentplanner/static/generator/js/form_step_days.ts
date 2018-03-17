function getCheckboxes(formGroupDiv: Element) {
    return Array.from(formGroupDiv.querySelectorAll("div label"));
}

function setClickCallbackFor(element: Element, callback: Function, callbackArgs: any[]) {
    element.addEventListener("click", () => {
        callback(...callbackArgs);
    });
}

let weekdaysDivs: Element[] = new Array<Element>(5);
let weekdaysLabels: Element[][] = new Array<Element[]>(5);
let postButton: HTMLButtonElement;

function togglePeriods(mainInput: HTMLInputElement, inputs: HTMLInputElement[]) {
    inputs.forEach((input) => {
       input.checked = mainInput.checked;
    });
}

function toggleAllDay(sourceInput: HTMLInputElement, mainInput: HTMLInputElement) {
    if (!sourceInput.checked) {
        mainInput.checked = false;
    }
}

function disablePeriodsOnClick(weekdaysLabels: Element[][]) {
    weekdaysLabels.forEach((labels) => {
        let mainInput = labels[0].querySelector("input") as HTMLInputElement;
        let otherInputs = labels.slice(1).map(l => l.querySelector("input") as HTMLInputElement);
        if (mainInput !== null) {
            setClickCallbackFor(mainInput, togglePeriods, [mainInput, otherInputs]);
            otherInputs.forEach((input) => {
                setClickCallbackFor(input, toggleAllDay, [input, mainInput]);
            })
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
            weekdaysDivs[i] = document.querySelector("#id_3-"+i) || new Element();
            weekdaysLabels[i] = getCheckboxes(weekdaysDivs[i])
        }

        disablePeriodsOnClick(weekdaysLabels);

        postButton = document.querySelector("#final") as HTMLButtonElement || new HTMLButtonElement();
        setClickCallbackFor(postButton, addLoader, []);
    }
};