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
            display: inline-block;
        }
        .user-settings-item svg {
            fill: white;
            height: 20px;
            width: 20px;
            cursor: pointer;
            margin-left: 10px;
        }
        .user-settings-input {
            margin-left: 10px;
            font-size: 1rem;
            max-width: 20ch;
            min-width: 10ch;
        }
        .user-settings-item > div {
            margin-left: auto;
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

    get value() {
        return this._value;
    }

    set value(newVal) {
        this._value = newVal;

        // Only re-render the element if not currently editing
        if (!this.editing) this.render();
    }

    get setting() {
        return this.getAttribute("setting");
    }

    set setting(settingName) {
        this.setAttribute("setting", settingName);
    }


    get editing() {
        return this.hasAttribute("editing");
    }

    set editing(status) {

        if (status) this.setAttribute("editing", status)
        else this.removeAttribute("editing")
    }


    toggleInput = () => {
        
        const currently_editing = this.editing;
        const toggle_val = !currently_editing;

        if (toggle_val) {
            const valueEl = this.shadowRoot.querySelector("span");

            const inputEl = document.createElement("input");
            inputEl.value = this.value;
            inputEl.classList.add("user-settings-input")

            valueEl.replaceWith(inputEl);
            inputEl.focus();

            inputEl.addEventListener("keydown", (e) => {
                
                if (this.setting === 'mashKey') {
                    this.value = e.code;

                    const event = new CustomEvent("setting-update", {
                        bubbles: true,
                        cancelable: false,
                        composed: true,
                        detail: {
                            setting: this.setting,
                            value: this.value
                        }
                    });

                    this.dispatchEvent(event);
                    this.toggleInput();
                } else {
                    
                    if (e.key === 'Enter') {
                        this.value = inputEl.value.trim();

                        const event = new CustomEvent("setting-update", {
                            bubbles: true,
                            composed: true,
                            cancelable: false,
                            detail: {
                                setting: this.setting,
                                value: this.value
                            }
                        });

                        this.dispatchEvent(event);
                        this.toggleInput();
                    } else if (e.key == "Escape") {
                        this.toggleInput();
                    }

                }

            })


        } else {
            const inputEl = this.shadowRoot.querySelector("input");

            const newValueEl = document.createElement("span");
            newValueEl.textContent = this.value;

            inputEl.replaceWith(newValueEl);
        }

        this.editing = !this.editing;
    }

    connectedCallback() {
        this._value = null;
        this.render();
    }

    attributeChangedCallback(attrName, oldVal, newVal) {
        // No need to re-render when editing since that would overwrite the input element
        if (attrName === 'editing') return 

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
        this.valueEl = valueSpan;
        valueSpan.textContent = this.value;

        const editDiv = innerDiv.querySelector("div");
        this.editEl = editDiv;
        editDiv.addEventListener("click", this.toggleInput);

        this.shadowRoot.replaceChildren(this.stylesheet, innerDiv);

    }

    static get observedAttributes() {
        return ["setting", "editing"]
    }
}

customElements.define("settings-option", SettingsOption);
// customElements.define("client-card", ClientCard);
