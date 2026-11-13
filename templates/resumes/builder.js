
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // FOUR-STEP FORM NAVIGATION
    // =====================================

    const sections = document.querySelectorAll(".form-section");
    const steps = document.querySelectorAll(".step");

    const previousButton = document.getElementById("previousButton");
    const nextButton = document.getElementById("nextButton");
    const generateButton = document.getElementById("generateButton");
    const resumeForm = document.getElementById("resumeForm");

    let currentStep = 1;

    function showStep(number) {
        currentStep = number;

        sections.forEach((section, index) => {
            section.style.display =
                index + 1 === number ? "block" : "none";
        });

        steps.forEach(step => {
            const stepNumber = Number(step.dataset.step);

            step.classList.toggle("active", stepNumber === number);
            step.classList.toggle("completed", stepNumber < number);
        });

        if (previousButton) {
            previousButton.disabled = number === 1;
        }

        if (nextButton) {
            nextButton.style.display =
                number === sections.length ? "none" : "inline-flex";
        }

        if (generateButton) {
            generateButton.style.display =
                number === sections.length ? "inline-flex" : "none";
        }
    }

    function validateStep() {
        const section = sections[currentStep - 1];

        if (!section) return true;

        const fields = section.querySelectorAll(
            "input[required], textarea[required], select[required]"
        );

        for (const field of fields) {
            if (!field.checkValidity()) {
                field.reportValidity();
                field.focus();
                return false;
            }
        }

        return true;
    }

    if (nextButton) {
        nextButton.addEventListener("click", function () {
            if (!validateStep()) return;

            if (currentStep < sections.length) {
                showStep(currentStep + 1);
            }
        });
    }

    if (previousButton) {
        previousButton.addEventListener("click", function () {
            if (currentStep > 1) {
                showStep(currentStep - 1);
            }
        });
    }

    steps.forEach(step => {
        step.addEventListener("click", function () {
            const number = Number(step.dataset.step);

            if (number > currentStep && !validateStep()) return;

            if (number >= 1 && number <= sections.length) {
                showStep(number);
            }
        });
    });

    if (resumeForm) {
        resumeForm.addEventListener("submit", function (event) {
            const requiredFields = resumeForm.querySelectorAll(
                "input[required], textarea[required], select[required]"
            );

            for (const field of requiredFields) {
                if (!field.checkValidity()) {
                    event.preventDefault();

                    const section = field.closest(".form-section");
                    const index = Array.from(sections).indexOf(section);

                    if (index >= 0) showStep(index + 1);

                    field.reportValidity();
                    field.focus();
                    return;
                }
            }
        });
    }

    if (sections.length > 0) {
        showStep(1);
    }


    // =====================================
    // VOICE INPUT
    // =====================================

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    const voiceLanguage = document.getElementById("voiceLanguage");
    const voiceStatus = document.getElementById("voiceStatus");

    let recognition = null;
    let activeButton = null;

    function status(message, type = "") {
        if (!voiceStatus) return;

        voiceStatus.textContent = message;
        voiceStatus.className = "voice-status";

        if (type) {
            voiceStatus.classList.add(type);
        }
    }

    function stopVoice() {
        if (recognition) {
            const oldRecognition = recognition;
            recognition = null;

            try {
                oldRecognition.stop();
            } catch (error) {
                // Recognition may already have stopped.
            }
        }

        if (activeButton) {
            activeButton.textContent = "🎙 Voice";
            activeButton.classList.remove("recording");
            activeButton = null;
        }
    }

    function startVoice(field, button) {

        if (!SpeechRecognition) {
            status(
                "Voice recognition is not supported. Please use Chrome or Edge.",
                "error"
            );
            return;
        }

        if (activeButton === button && recognition) {
            stopVoice();
            status("Voice input stopped.");
            return;
        }

        stopVoice();

        const speech = new SpeechRecognition();

        speech.lang = voiceLanguage
            ? voiceLanguage.value
            : "en-IN";

        speech.continuous = false;
        speech.interimResults = true;

        let finalText = "";

        recognition = speech;
        activeButton = button;

        button.textContent = "⏹ Stop";
        button.classList.add("recording");

        status("Listening... Please speak.", "listening");

        speech.onresult = function (event) {
            let interimText = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                const text = result[0].transcript;

                if (result.isFinal) {
                    finalText += text;
                } else {
                    interimText += text;
                }
            }

            if (interimText) {
                status("Hearing: " + interimText, "listening");
            }

            if (finalText) {
                const separator = field.value.trim() ? " " : "";

                field.value = field.value.trim() +
                    separator + finalText.trim();

                field.dispatchEvent(
                    new Event("input", { bubbles: true })
                );

                field.dispatchEvent(
                    new Event("change", { bubbles: true })
                );

                status("Speech added. You can edit the text.");
            }
        };

        speech.onerror = function (event) {
            const errors = {
                "not-allowed": "Please allow microphone permission.",
                "no-speech": "No speech detected. Try again.",
                "network": "Network error during speech recognition.",
                "audio-capture": "No microphone was detected."
            };

            status(
                errors[event.error] || "Voice recognition error: " + event.error,
                "error"
            );
        };

        speech.onend = function () {
            if (recognition === speech) {
                recognition = null;
            }

            if (activeButton === button) {
                activeButton = null;
            }

            button.textContent = "🎙 Voice";
            button.classList.remove("recording");

            if (!finalText) {
                status("Voice input ended. Try again if needed.");
            }
        };

        try {
            speech.start();
        } catch (error) {
            stopVoice();
            status("Unable to start microphone. Please try again.", "error");
        }
    }


    // =====================================
    // ADD VOICE BUTTONS TO FORM FIELDS
    // =====================================

    const fields = document.querySelectorAll(
        ".form-control:not(select):not([type='hidden']):not([type='submit']):not([type='button'])"
    );

    fields.forEach(field => {

        const supportedTypes = [
            "text", "email", "tel", "url", "search"
        ];

        const isTextarea = field.tagName === "TEXTAREA";

        if (
            (!isTextarea && !supportedTypes.includes(field.type)) ||
            field.disabled ||
            field.readOnly ||
            field.dataset.voiceAdded === "true"
        ) {
            return;
        }

        field.dataset.voiceAdded = "true";

        const wrapper = document.createElement("div");
        wrapper.className = "voice-input-wrap";

        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);

        const button = document.createElement("button");

        button.type = "button";
        button.className = "voice-input-button";
        button.textContent = "🎙 Voice";

        button.addEventListener("click", function () {
            startVoice(field, button);
        });

        wrapper.appendChild(button);
    });

    if (SpeechRecognition) {
        status("Voice input is ready. Select a language and press Voice.");
    } else {
        status("Voice recognition is unavailable. Try Chrome or Edge.", "error");
    }

});
