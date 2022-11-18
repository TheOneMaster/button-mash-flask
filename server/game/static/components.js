// class ClientCard extends HTMLElement {

//     constructor() {
//         super();

//         this.attachShadow({mode:"open"});

//         // Set default property values
//         this.name = "";
//         this.leader = false;

//         // Attach CSS to the component
//         this.style = document.createElement("link");
//         this.style.setAttribute("rel", "stylesheet");
//         this.style.setAttribute("href", "ClientCard.css");

//         this.shadowRoot.appendChild(this.style);

//         // Create template layout
//         this.template = document.createElement("template");
//         const innerDiv = document.createElement("div");

//     }

//     connectedCallback() {

//     }

//     render() {

//     }

//     attributeChangedCallback(attrName, oldVal, newVal) {

//     }

//     static get observedAttributes() {
//         return ["name", "leader"]
//     }
// }

class SettingsOption extends HTMLElement {
    constructor() {
        super();

        this.attachShadow({mode: "open"});

        this.stylesheet = document.createElement("style");
        this.stylesheet.innerHTML = `
        .user-settings-item {
            color: var(--primary-font-color);
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            flex-direction: row;
        }
        .user-settings-item span {
            color: var(--second-font-color);
            margin-left: 5px;
            font-weight: 400;
        }
        .user-settings-item > div {
            margin-left: auto;
        }
        .user-settings-item svg {
            fill: white;
            height: 20px;
            width: 20px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        @media screen and (prefers-color-scheme: light) {
            .user-settings-item svg {
                fill: black;
            }
        }
        `;

        // Template
        this.template = document.createElement("template");

        const innerDiv = document.createElement("div");
        innerDiv.classList.add("user-settings-item");
        const valueEl = document.createElement("span");
        const editEl = document.createElement("div");

        const editSVG = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        editSVG.setAttribute("viewBox", "0 0 32 32");
        editSVG.setAttribute("width", "64px");
        editSVG.setAttribute("height", "64px");

        editSVG.innerHTML = '<path d="M 23.90625 3.96875 C 22.859375 3.96875 21.8125 4.375 21 5.1875 L 5.1875 21 L 5.125 21.3125 L 4.03125 26.8125 L 3.71875 28.28125 L 5.1875 27.96875 L 10.6875 26.875 L 11 26.8125 L 26.8125 11 C 28.4375 9.375 28.4375 6.8125 26.8125 5.1875 C 26 4.375 24.953125 3.96875 23.90625 3.96875 Z M 23.90625 5.875 C 24.410156 5.875 24.917969 6.105469 25.40625 6.59375 C 26.378906 7.566406 26.378906 8.621094 25.40625 9.59375 L 24.6875 10.28125 L 21.71875 7.3125 L 22.40625 6.59375 C 22.894531 6.105469 23.402344 5.875 23.90625 5.875 Z M 20.3125 8.71875 L 23.28125 11.6875 L 11.1875 23.78125 C 10.53125 22.5 9.5 21.46875 8.21875 20.8125 Z M 6.9375 22.4375 C 8.136719 22.921875 9.078125 23.863281 9.5625 25.0625 L 6.28125 25.71875 Z"/>'

        editEl.appendChild(editSVG);

        innerDiv.replaceChildren(valueEl, editEl);

        this.template.appendChild(innerDiv);
    }

    

    get setting() {
        return this.getAttribute("setting");
    }

    set setting(settingName) {
        this.setAttribute("setting", settingName);
    }

    get value() {
        return this.getAttribute("value");
    }

    set value(newVal) {
        this.setAttribute("value", newVal);
    }



    connectedCallback() {
        this.render();
    }

    attributeChangedCallback(attrName, oldVal, newVal) {
        if (oldVal !== newVal) {
            this[attrName] = newVal;
            this.render();
        }
    }

    render() {
        
        const template = this.template.cloneNode(true);

        const innerDiv = template.firstChild;

        const settingString = this.setting.charAt(0).toUpperCase() + this.setting.slice(1) + ": ";
        innerDiv.insertAdjacentText('afterbegin', settingString);
        
        const valueSpan = innerDiv.querySelector("span");
        valueSpan.textContent = this.value;

        this.shadowRoot.replaceChildren(this.stylesheet, innerDiv);

    }

    static get observedAttributes() {
        return ["setting", "value"]
    }
}

customElements.define("settings-option", SettingsOption);
// customElements.define("client-card", ClientCard);
